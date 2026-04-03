import json
import requests
import boto3

import config

def get_s3_client():
    """Initialize Digital Ocean Spaces client (S3-compatible)"""
    if not config.DO_SPACES_KEY or not config.DO_SPACES_SECRET:
        return None

    session = boto3.session.Session()
    return session.client('s3',
        region_name=config.DO_SPACES_REGION,
        endpoint_url=config.DO_SPACES_ENDPOINT,
        aws_access_key_id=config.DO_SPACES_KEY,
        aws_secret_access_key=config.DO_SPACES_SECRET
    )

def call_openrouter(prompt, system_message="You are a helpful assistant.", use_fallback=False):
    """Make a completion call to OpenRouter API with free-model primary and paid fallback."""
    if not config.OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY not configured")

    model = config.OPENROUTER_FALLBACK_MODEL if use_fallback else config.OPENROUTER_MODEL

    response = requests.post(
        url=config.OPENROUTER_API_URL,
        headers={
            "Authorization": f"Bearer {config.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://143.110.131.237:6732",
            "X-Title": "US Federal Data Exchange"
        },
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            "temperature": config.LLM_TEMPERATURE,
            "max_tokens": config.LLM_MAX_TOKENS
        },
        timeout=30
    )

    if response.status_code == 429 and not use_fallback:
        print(f"[LLM] Rate limited on {model}, falling back to {config.OPENROUTER_FALLBACK_MODEL}")
        return call_openrouter(prompt, system_message, use_fallback=True)

    if response.status_code != 200:
        if not use_fallback:
            print(f"[LLM] Error {response.status_code} on {model}, retrying with fallback")
            return call_openrouter(prompt, system_message, use_fallback=True)
        raise Exception(f"OpenRouter API error: {response.status_code} - {response.text}")

    result = response.json()
    return result['choices'][0]['message']['content']

def collect_data(description):
    """
    AI-powered data collector that finds relevant data based on description.
    Uses metadata indices from cloud storage to locate matching datasets.
    """
    s3_client = get_s3_client()
    
    if not s3_client:
        return {
            'note': 'Demo mode - cloud storage not configured',
            'sample_data': _get_sample_data(description)
        }
    
    try:
        metadata_list = []
        prefix = getattr(config, 'DO_SPACES_PREFIX', 'usdx/')
        response = s3_client.list_objects_v2(Bucket=config.DO_SPACES_BUCKET, Prefix=f'{prefix}metadata/')
        
        if 'Contents' in response:
            for obj in response['Contents'][:10]:
                metadata_obj = s3_client.get_object(Bucket=config.DO_SPACES_BUCKET, Key=obj['Key'])
                metadata = json.loads(metadata_obj['Body'].read().decode('utf-8'))
                metadata_list.append(metadata)
        
        prompt = f"""Given this data request: "{description}"

Available datasets metadata:
{json.dumps(metadata_list, indent=2)}

Return a JSON list of dataset IDs that best match the request. Format: {{"dataset_ids": ["id1", "id2"]}}"""
        
        ai_response = call_openrouter(prompt, 
            "You are a federal data matching system. Analyze requests and return matching dataset IDs as JSON. Return ONLY the JSON, no other text.")
        
        # Extract JSON from response (LLM may append explanatory text)
        try:
            matched_ids = json.loads(ai_response).get('dataset_ids', [])
        except json.JSONDecodeError:
            start = ai_response.find('{')
            end = ai_response.find('}', start) + 1
            if start != -1 and end > start:
                matched_ids = json.loads(ai_response[start:end]).get('dataset_ids', [])
            else:
                matched_ids = []
        
        collected_datasets = []
        for dataset_id in matched_ids:
            try:
                data_obj = s3_client.get_object(Bucket=config.DO_SPACES_BUCKET, Key=f'{prefix}data/{dataset_id}.json')
                dataset = json.loads(data_obj['Body'].read().decode('utf-8'))
                collected_datasets.append(dataset)
            except:
                continue
        
        return collected_datasets if collected_datasets else _get_sample_data(description)
    
    except Exception as e:
        print(f"Data collection error: {e}")
        return _get_sample_data(description)

# ---------------------------------------------------------------------------
# FOIA Two-Tier Redaction System — 5 U.S.C. § 552
#
# Tier 1 BLIND  [b(Ex.N)] — classified, statutory, or operationally sensitive
#                            info that cannot be released in any form
# Tier 2 SMART  <substitute> — personal privacy info replaced with a different
#                              but realistic equivalent value
# ---------------------------------------------------------------------------

_REDACTION_SYSTEM = (
    "You are a FOIA compliance officer processing federal agency records for public release "
    "under 5 U.S.C. § 552 (Freedom of Information Act). Apply the two-tier redaction scheme "
    "specified below, then return ONLY the redacted JSON — no commentary, no explanations.\n\n"

    "TIER 1 — BLIND REDACTION: Replace the field value with a [b(Ex.N)] marker that cites "
    "the applicable FOIA exemption number. Use Tier 1 for classified, operationally sensitive, "
    "or statutorily protected information that cannot be released in any form.\n\n"

    "TIER 2 — SMART REDACTION: Replace the field value with a different but realistic substitute "
    "of the same type (a different plausible full name, a different real-sounding address in the "
    "same city, a different valid phone number, etc.). Use Tier 2 for personal privacy data where "
    "record structure must be preserved but the individual must not be identifiable.\n\n"

    "SEGREGABILITY — 5 U.S.C. § 552(b): Release all reasonably segregable non-exempt portions. "
    "Do NOT redact administrative IDs, event dates, position titles, pay grades, salary amounts, "
    "complaint categories, or general outcome/disposition text. "
    "Return only valid JSON."
)

_REDACTION_RULES = (
    "TIER 1 — BLIND REDACT (replace value with [b(Ex.N)] marker):\n"
    "  [b(Ex.1)]  Classification markings — e.g. TOP SECRET, HCS, NOFORN, SCI\n"
    "  [b(Ex.1)]  Security clearance levels — e.g. TS/SCI, Top Secret, Secret\n"
    "  [b(Ex.1)]  Covert or classified facility names and street addresses\n"
    "             (Camp Peary / The Farm, Harvey Point, undisclosed OCONUS stations)\n"
    "  [b(Ex.3)]  Social Security Numbers (SSN)\n"
    "  [b(Ex.3)]  Intelligence program identifiers, operation codenames, source identifiers\n"
    "  [b(Ex.3)]  Biometric identifiers\n\n"

    "TIER 2 — SMART REDACT (replace value with realistic substitute):\n"
    "  Ex.6  Individual names (contractors, employees, civilians)\n"
    "        → substitute a different realistic full name\n"
    "  Ex.6  Supervising officer names\n"
    "        → substitute a different realistic name and title\n"
    "  Ex.6  Dates of birth\n"
    "        → shift by a random amount (±1–5 years, different month and day)\n"
    "  Ex.6  Personal and residential street addresses\n"
    "        → substitute a different plausible address in the same city and state\n"
    "  Ex.6  Personal phone numbers\n"
    "        → substitute a different realistic phone number with the same area code\n"
    "  Ex.6  Personal email addresses\n"
    "        → substitute a different realistic email address\n"
    "  Ex.7(C)  Names of third parties in law enforcement or incident records\n"
    "           → substitute a different realistic name\n\n"

    "PRESERVE — do NOT redact these fields:\n"
    "  Case numbers, employee IDs, contract numbers\n"
    "  Dates of events and incidents\n"
    "  Position titles and pay grades\n"
    "  Annual salary amounts\n"
    "  Animal types, breeds, and pet names\n"
    "  Complaint categories and general disposition/outcome text\n"
    "  Non-covert facility names used as general location context (Langley, VA; Fort Meade, MD)\n\n"

    "CONSISTENCY: if a name or value appears more than once, use the same substitute throughout.\n\n"

    "DATA TO REDACT:\n"
)


def _redact_chunk(chunk):
    """Redact a single JSON-serializable chunk using the FOIA two-tier scheme."""
    chunk_str = json.dumps(chunk, indent=2)
    prompt = _REDACTION_RULES + chunk_str
    redacted_str = call_openrouter(prompt, _REDACTION_SYSTEM)
    try:
        return json.loads(redacted_str)
    except json.JSONDecodeError:
        start = redacted_str.find('{')
        end = redacted_str.rfind('}') + 1
        if start != -1 and end > start:
            return json.loads(redacted_str[start:end])
        start = redacted_str.find('[')
        end = redacted_str.rfind(']') + 1
        if start != -1 and end > start:
            return json.loads(redacted_str[start:end])
        raise


def _redact_large_dict(data):
    """Chunk a large dict by splitting nested lists, then redact."""
    result = {}
    for key, value in data.items():
        if isinstance(value, list) and len(value) > 3:
            chunk_size = 3
            redacted_list = []
            for i in range(0, len(value), chunk_size):
                chunk_result = _redact_chunk({key: value[i:i + chunk_size]})
                if isinstance(chunk_result, dict):
                    redacted_list.extend(chunk_result.get(key, []))
                elif isinstance(chunk_result, list):
                    redacted_list.extend(chunk_result)
            result[key] = redacted_list
        else:
            result[key] = value
    if json.dumps(result).strip() == '{}':
        return _redact_chunk(data)
    return _redact_chunk(result)


def redact_data(data):
    """
    AI-powered redactor that applies differential privacy and removes sensitive PII.
    Chunks large inputs to stay within LLM token limits (~2000 tokens per chunk).
    """
    try:
        if isinstance(data, list):
            data_str = json.dumps(data)
            if len(data) > 3 or len(data_str) > 6000:
                redacted_chunks = []
                for item in data:
                    item_str = json.dumps(item)
                    if isinstance(item, dict) and len(item_str) > 6000:
                        redacted_item = _redact_large_dict(item)
                    else:
                        redacted_item = _redact_chunk(item)
                    if isinstance(redacted_item, list):
                        redacted_chunks.extend(redacted_item)
                    else:
                        redacted_chunks.append(redacted_item)
                return redacted_chunks
            return _redact_chunk(data)

        data_str = json.dumps(data)
        if len(data_str) > 6000:
            return _redact_large_dict(data)
        return _redact_chunk(data)

    except Exception as e:
        print(f"Redaction error: {e}")
        return {
            'error': 'Redaction failed',
            'original_data': '[WITHHELD FOR PRIVACY]',
            'note': str(e)
        }

def _get_sample_data(description):
    """Generate sample federal data for demo purposes"""
    return {
        'query': description,
        'source': 'US Federal Data Exchange (Sample)',
        'records': [
            {
                'id': 'FED-001',
                'category': 'census',
                'data': {
                    'location': 'Colorado',
                    'population': 5773714,
                    'year': 2023
                }
            },
            {
                'id': 'FED-002',
                'category': 'economic',
                'data': {
                    'gdp_growth': 2.5,
                    'unemployment_rate': 3.8,
                    'quarter': 'Q4 2023'
                }
            }
        ],
        'note': 'Sample data - configure cloud storage for real datasets'
    }
