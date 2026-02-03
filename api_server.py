import json
import time
from datetime import datetime, timedelta
from functools import wraps

import bcrypt
import jwt
import boto3
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

import config
from handlers import collect_data, redact_data

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
    """Retrieve user from DO Spaces"""
    try:
        s3 = get_s3_client()
        prefix = getattr(config, 'DO_SPACES_PREFIX', '')
        key = f'{prefix}users/{email}.json'
        response = s3.get_object(Bucket=config.DO_SPACES_BUCKET, Key=key)
        user_data = json.loads(response['Body'].read().decode('utf-8'))
        return user_data
    except s3.exceptions.NoSuchKey:
        return None
    except Exception as e:
        print(f"Error retrieving user: {e}")
        return None

def save_user(email, password_hash):
    """Save user to DO Spaces"""
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
        'service': 'US Federal Data Exchange'
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
@token_required
def get_data():
    start_time = time.time()
    data = request.get_json()
    description = data.get('description')
    
    if not description:
        return jsonify({'error': 'Description required'}), 400
    
    try:
        collected_data = collect_data(description)
        redacted_data = redact_data(collected_data)
        
        processing_time = time.time() - start_time
        
        return jsonify({
            'status': 'success',
            'data': redacted_data,
            'metadata': {
                'processing_time_seconds': round(processing_time, 2),
                'records_returned': len(redacted_data) if isinstance(redacted_data, list) else 1,
                'privacy_applied': True
            }
        }), 200
    except Exception as e:
        return jsonify({
            'error': 'Failed to process data request',
            'details': str(e)
        }), 500

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api_docs.html')
def api_docs():
    return send_from_directory('.', 'api_docs.html')

def main():
    import os
    
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
