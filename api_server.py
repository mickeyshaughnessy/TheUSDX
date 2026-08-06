import json
import os
import time
import hashlib
from datetime import datetime, timedelta
from functools import wraps

import bcrypt
import jwt
import boto3
from flask import Flask, request, jsonify, send_from_directory, abort
from flask_cors import CORS

import config
from handlers import collect_data, redact_data, redact_text

# In-memory TTL cache
_cache: dict = {}
_cache_ts: dict = {}
_TTL_USER = 120       # seconds
_TTL_RESULT = 3600    # cache redacted results for 1 hour

# Per-query privacy pricing. "standard" is the FOIA-baseline tier included
# with every query; "reduced" and "aggressive" are paid add-ons that move
# the redaction dial down (less privacy, more raw identifiers released) or
# up (more privacy, more fields cloaked). Reduced never waives statutorily
# mandated Tier 1 exemptions -- see handlers.py.
BASE_QUERY_PRICE_USD = 0.25
PRIVACY_TIERS = {
    'reduced': {
        'label': 'Reduced Privacy',
        'price_usd': 4.00,
        'description': (
            'Only statutorily-mandated blind exemptions are withheld (SSNs, classification '
            'markings, biometric/ID numbers). Personal identifiers -- names, addresses, phone '
            'numbers, dates of birth -- are released in full. Intended for verified requesters '
            'with a legitimate need for identified records.'
        ),
    },
    'standard': {
        'label': 'Standard Privacy',
        'price_usd': 0.00,
        'description': (
            'Two-tier FOIA redaction: statutory blind exemptions plus smart cloaking of '
            'personal privacy fields (names, addresses, DOB, phone, email) with realistic '
            'substitutes. Included with every query.'
        ),
    },
    'aggressive': {
        'label': 'Enhanced Privacy',
        'price_usd': 1.50,
        'description': (
            'Standard redaction plus aggressive cloaking of indirect identifiers -- locations, '
            'dates, employers, relationships, physical descriptions, and any other field that '
            'could be cross-referenced to re-identify an individual.'
        ),
    },
}


def _price_for(privacy_level: str) -> dict:
    tier = PRIVACY_TIERS[privacy_level]
    return {
        'privacy_level': privacy_level,
        'tier_label': tier['label'],
        'base_price_usd': BASE_QUERY_PRICE_USD,
        'privacy_addon_usd': tier['price_usd'],
        'total_price_usd': round(BASE_QUERY_PRICE_USD + tier['price_usd'], 2),
        'description': tier['description'],
        'billing_note': 'Pricing shown for demonstration only; no payment is collected.',
    }


def _cache_get(key: str):
    if key in _cache and time.time() - _cache_ts.get(key, 0) < (
            _TTL_USER if key.startswith('user:') else _TTL_RESULT):
        return _cache[key]
    return None


def _cache_set(key: str, value) -> None:
    _cache[key] = value
    _cache_ts[key] = time.time()

app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY
CORS(app)

def get_s3_client():
    """Initialize Digital Ocean Spaces client"""
    session = boto3.session.Session()
    return session.client('s3',
        region_name=config.DO_SPACES_REGION,
        endpoint_url=config.DO_SPACES_ENDPOINT,
        aws_access_key_id=config.DO_SPACES_KEY,
        aws_secret_access_key=config.DO_SPACES_SECRET
    )

def get_user(email):
    """Retrieve user from DO Spaces, with in-memory cache."""
    cache_key = f'user:{email}'
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached
    try:
        s3 = get_s3_client()
        prefix = getattr(config, 'DO_SPACES_PREFIX', '')
        key = f'{prefix}users/{email}.json'
        response = s3.get_object(Bucket=config.DO_SPACES_BUCKET, Key=key)
        user_data = json.loads(response['Body'].read().decode('utf-8'))
        _cache_set(cache_key, user_data)
        return user_data
    except Exception as e:
        if 'NoSuchKey' not in str(e) and '404' not in str(e):
            print(f"Error retrieving user: {e}")
        return None

def save_user(email, password_hash):
    """Save user to DO Spaces and update cache."""
    try:
        s3 = get_s3_client()
        prefix = getattr(config, 'DO_SPACES_PREFIX', '')
        key = f'{prefix}users/{email}.json'
        user_data = {
            'email': email,
            'password_hash': password_hash.decode('utf-8') if isinstance(password_hash, bytes) else password_hash,
            'created_at': datetime.utcnow().isoformat()
        }
        s3.put_object(
            Bucket=config.DO_SPACES_BUCKET,
            Key=key,
            Body=json.dumps(user_data),
            ContentType='application/json'
        )
        _cache_set(f'user:{email}', user_data)
        return True
    except Exception as e:
        print(f"Error saving user: {e}")
        return False

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(*args, **kwargs)
    return decorated

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'Acme Redactors'
    }), 200

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    
    existing_user = get_user(email)
    if existing_user:
        return jsonify({'error': 'Email already exists'}), 409
    
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    if not save_user(email, password_hash):
        return jsonify({'error': 'Failed to create user'}), 500
    
    token = jwt.encode({
        'email': email,
        'exp': datetime.utcnow() + timedelta(days=30)
    }, app.config['SECRET_KEY'], algorithm='HS256')
    
    return jsonify({
        'message': 'User created successfully',
        'token': token
    }), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    
    user = get_user(email)
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    password_hash = user['password_hash']
    if isinstance(password_hash, str):
        password_hash = password_hash.encode('utf-8')
    
    if not bcrypt.checkpw(password.encode('utf-8'), password_hash):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    token = jwt.encode({
        'email': email,
        'exp': datetime.utcnow() + timedelta(days=30)
    }, app.config['SECRET_KEY'], algorithm='HS256')
    
    return jsonify({
        'message': 'Login successful',
        'token': token
    }), 200

@app.route('/get_data', methods=['POST'])
def get_data():
    start_time = time.time()
    data = request.get_json()
    description = data.get('description')
    privacy_level = data.get('privacy_level', 'standard')

    if not description:
        return jsonify({'error': 'Description required'}), 400
    if privacy_level not in PRIVACY_TIERS:
        return jsonify({'error': f'Invalid privacy_level. Choose one of: {", ".join(PRIVACY_TIERS)}'}), 400

    # Cache keyed by query + privacy_level
    cache_input = f'{description}|{privacy_level}'
    query_hash = hashlib.sha256(cache_input.encode()).hexdigest()
    cache_key = f'result:{query_hash}'
    cached_result = _cache_get(cache_key)
    if cached_result is not None:
        cache_time = time.time() - start_time
        cached_result['metadata']['cached'] = True
        cached_result['metadata']['processing_time_seconds'] = round(cache_time, 2)
        return jsonify(cached_result), 200

    try:
        collected_data = collect_data(description)
        redacted_data = redact_data(collected_data, privacy_level=privacy_level)

        processing_time = time.time() - start_time

        result = {
            'status': 'success',
            'original_data': collected_data,
            'data': redacted_data,
            'metadata': {
                'processing_time_seconds': round(processing_time, 2),
                'records_returned': len(redacted_data) if isinstance(redacted_data, list) else 1,
                'privacy_applied': True,
                'cached': False
            },
            'pricing': _price_for(privacy_level),
            'foia_compliance': {
                'statute': '5 U.S.C. § 552 (Freedom of Information Act)',
                'blind_redactions': '[b(Ex.N)] markers — Ex.1 classified info, Ex.3 statutorily protected (SSNs, program identifiers), Ex.7(F) life/safety',
                'smart_redactions': 'Realistic substitutes — Ex.6 personal privacy (names, addresses, DOB, phone), Ex.7(C) third-party names in law enforcement records',
                'segregability': 'Non-exempt fields preserved per § 552(b): case IDs, event dates, titles, pay grades, dispositions',
                'presumption': 'Openness — withheld only where disclosure would harm a protected interest per § 552(a)(8)(A)'
            }
        }
        _cache_set(cache_key, result)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({
            'error': 'Failed to process data request',
            'details': str(e)
        }), 500

@app.route('/redact', methods=['POST'])
def redact():
    start_time = time.time()
    data = request.get_json()
    record = data.get('record')
    if record is None:
        return jsonify({'error': 'record required'}), 400

    privacy_level = data.get('privacy_level', 'aggressive')  # default aggressive for paste
    if privacy_level not in PRIVACY_TIERS:
        return jsonify({'error': f'Invalid privacy_level. Choose one of: {", ".join(PRIVACY_TIERS)}'}), 400

    try:
        # Try to parse as JSON; fall back to treating as plain text
        if isinstance(record, str):
            try:
                import json as _json
                record = _json.loads(record)
                is_text = False
            except Exception:
                is_text = True
        else:
            is_text = False

        if is_text:
            redacted = redact_text(record, privacy_level=privacy_level)
        else:
            redacted = redact_data(record, privacy_level=privacy_level)

        return jsonify({
            'status': 'success',
            'original_data': record,
            'data': redacted,
            'is_text': is_text,
            'metadata': {
                'processing_time_seconds': round(time.time() - start_time, 2),
                'privacy_applied': True,
                'cached': False
            },
            'pricing': _price_for(privacy_level),
            'foia_compliance': {
                'statute': '5 U.S.C. § 552 (Freedom of Information Act)',
                'blind_redactions': '[b(Ex.N)] markers — Ex.1 classified info, Ex.3 SSNs/program IDs, Ex.7(F) life/safety',
                'smart_redactions': 'Realistic substitutes — Ex.6 personal privacy (names, addresses, DOB, phone), Ex.7(C) third-party names',
                'segregability': 'Non-exempt fields preserved per § 552(b)'
            }
        }), 200
    except Exception as e:
        return jsonify({'error': 'Redaction failed', 'details': str(e)}), 500

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api_docs.html')
def api_docs():
    return send_from_directory('.', 'api_docs.html')

@app.route('/deck.html')
def deck():
    return send_from_directory('.', 'deck.html')

@app.route('/assets/<path:filename>')
def assets(filename):
    return send_from_directory('assets', filename)

@app.route('/eagle.html')
@app.route('/eagle_drill.html')
def eagle_drill():
    name = 'eagle_drill.html' if os.path.exists('eagle_drill.html') else 'eagle.html'
    return send_from_directory('.', name)

@app.route('/plasma.html')
def plasma():
    # Prefer local copy; fall back to PlasmaSim deploy path on prod
    if os.path.exists('plasma.html'):
        return send_from_directory('.', 'plasma.html')
    if os.path.exists('/var/www/PlasmaSim/plasma.html'):
        return send_from_directory('/var/www/PlasmaSim', 'plasma.html')
    abort(404)

@app.route('/rifts.html')
def rifts_game():
    # Prefer local copy; fall back to RIFTs deploy path on prod
    if os.path.exists('rifts.html'):
        return send_from_directory('.', 'rifts.html')
    if os.path.exists('/var/www/RIFTs/rifts.html'):
        return send_from_directory('/var/www/RIFTs', 'rifts.html')
    abort(404)

@app.route('/api/rifts/narrate', methods=['POST'])
def rifts_narrate():
    """Optional Grok/xAI (or OpenRouter) scene enrichment for the text game."""
    try:
        data = request.get_json(force=True, silent=True) or {}
        scene = (data.get('scene') or '').strip()
        if not scene:
            return jsonify({'error': 'scene required'}), 400
        if len(scene) > 6000:
            scene = scene[:6000]

        operative = data.get('operative') or 'Operative'
        occ = data.get('occ') or 'adventurer'
        location = data.get('location') or 'unknown'
        mission = data.get('mission') or 'contract'
        tone = data.get('tone') or 'grim'

        system = (
            "You are the narrative AI for an unofficial text-only Rifts-inspired RPG "
            "(fan work; not affiliated with Palladium Books). Write 2-4 vivid sentences "
            "enriching the scene for the player. Stay in second person. No stats, no "
            "OOC, no markdown headings. Keep it PG-13 pulp: weird, deadly, moral gray. "
            "Do not invent copyrighted stat blocks; flavor only."
        )
        prompt = (
            f"Tone: {tone}\nLocation: {location}\nMission: {mission}\n"
            f"Operative: {operative} ({occ})\n\nScene:\n{scene}\n\n"
            "Enrich the sensory detail and stakes in 2-4 sentences:"
        )

        narration = None
        provider = None

        # Prefer xAI / Grok when configured (SpaceXAI / Grok Build stack)
        xai_key = getattr(config, 'XAI_API_KEY', None) or os.environ.get('XAI_API_KEY')
        xai_model = getattr(config, 'XAI_MODEL', None) or os.environ.get('XAI_MODEL') or 'grok-4.5'
        if xai_key:
            try:
                import requests as _req
                r = _req.post(
                    'https://api.x.ai/v1/chat/completions',
                    headers={
                        'Authorization': f'Bearer {xai_key}',
                        'Content-Type': 'application/json',
                    },
                    json={
                        'model': xai_model,
                        'messages': [
                            {'role': 'system', 'content': system},
                            {'role': 'user', 'content': prompt},
                        ],
                        'temperature': 0.85,
                        'max_tokens': 220,
                    },
                    timeout=25,
                )
                if r.status_code == 200:
                    narration = r.json()['choices'][0]['message']['content'].strip()
                    provider = f'xai:{xai_model}'
                else:
                    print(f"[rifts] xAI error {r.status_code}: {r.text[:200]}")
            except Exception as e:
                print(f"[rifts] xAI failed: {e}")

        # Fallback: OpenRouter (may include x-ai/grok models)
        if not narration and getattr(config, 'OPENROUTER_API_KEY', None):
            try:
                from handlers import call_openrouter
                model_override = getattr(config, 'RIFTS_MODEL', None)
                # Prefer grok on OpenRouter when available
                or_model = model_override or getattr(config, 'OPENROUTER_MODEL', None)
                narration = call_openrouter(prompt, system_message=system)
                provider = f'openrouter:{or_model}'
            except Exception as e:
                print(f"[rifts] OpenRouter failed: {e}")
                return jsonify({
                    'error': 'narration unavailable',
                    'details': str(e),
                    'fallback': True,
                }), 503

        if not narration:
            return jsonify({
                'error': 'No LLM configured (set XAI_API_KEY or OPENROUTER_API_KEY)',
                'fallback': True,
            }), 503

        return jsonify({
            'narration': narration,
            'provider': provider,
            'model_note': 'Unofficial fan narration; not Palladium canon.',
        }), 200
    except Exception as e:
        return jsonify({'error': 'narrate failed', 'details': str(e)}), 500

@app.route('/techtree.html')
def techtree():
    # Prefer local copy; fall back to TechTree deploy path on prod
    if os.path.exists('techtree.html'):
        return send_from_directory('.', 'techtree.html')
    if os.path.exists('/var/www/TechTree/techtree.html'):
        return send_from_directory('/var/www/TechTree', 'techtree.html')
    abort(404)

def main():
    ssl_cert = config.SSL_CERT_PATH
    ssl_key = config.SSL_KEY_PATH
    
    if ssl_cert and ssl_key and os.path.exists(ssl_cert) and os.path.exists(ssl_key):
        print(f"Starting HTTPS server on {config.HOST}:{config.PORT}...")
        app.run(host=config.HOST, port=config.PORT, ssl_context=(ssl_cert, ssl_key), debug=config.DEBUG)
    else:
        print(f"Starting HTTP server on {config.HOST}:{config.PORT}...")
        print("Warning: Running without SSL. For production, configure SSL certificates.")
        app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)

if __name__ == '__main__':
    main()
