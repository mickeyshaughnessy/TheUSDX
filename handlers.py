import json
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
            "X-Title": "Acme Redactors"
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

_REDACTION_SYSTEM = (
    "You are a privacy protection system for federal data. "
    "Redact PII while maintaining data utility. Return only valid JSON. "
    "Treat pet/animal names as personally identifiable information that must be substituted."
)
_REDACTION_RULES = """Redaction rules:
- Replace proper names with realistic alternatives (e.g., "Mickey" -> "Jamison")
- IMPORTANT: Replace ALL pet/animal names in fields like "animal_name" with DIFFERENT realistic pet names — every single animal name must be changed to a different name (e.g., "Buddy" -> "Max", "Whiskers" -> "Mittens", "Tinkerbell" -> "Daisy", "Sergeant" -> "Rex", "Blue" -> "Scout"). Pet names are PII that can identify owners.
- Replace specific locations with generalized regions (e.g., "123 Main St, Denver" -> "Colorado")
- Replace or remove other PII (SSN, phone numbers, email addresses, etc.)
- For faces in image metadata, replace with "[FACE_REDACTED]"
- Maintain data structure and utility while protecting privacy

Return ONLY the redacted JSON data, no explanations."""


_FALLBACK_PET_NAMES = [
    "Milo", "Rosie", "Ginger", "Toby", "Sadie", "Harley", "Ruby",
    "Tucker", "Molly", "Winston", "Penny", "Bruno", "Stella", "Baxter",
    "Olive", "Duke", "Hazel", "Murphy", "Nala", "Zeus", "Cleo",
]


def _extract_pet_names(data):
    """Extract all pet/animal names from a dataset for cross-chunk collision avoidance."""
    names = set()
    data_str = json.dumps(data)
    if '"animal_name"' not in data_str:
        return names
    
    def _walk(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == 'animal_name' and isinstance(v, str):
                    names.add(v)
                else:
                    _walk(v)
        elif isinstance(obj, list):
            for item in obj:
                _walk(item)
    
    _walk(data)
    return names


def _fix_pet_name_collisions(redacted, original_names):
    """Post-process redacted data to replace any pet names that collide with originals."""
    if not original_names:
        return redacted
    
    # Build pool of safe replacement names
    safe_pool = [n for n in _FALLBACK_PET_NAMES if n not in original_names]
    pool_idx = 0
    
    def _fix(obj):
        nonlocal pool_idx
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == 'animal_name' and isinstance(v, str) and v in original_names:
                    if pool_idx < len(safe_pool):
                        obj[k] = safe_pool[pool_idx]
                        pool_idx += 1
                else:
                    _fix(v)
        elif isinstance(obj, list):
            for item in obj:
                _fix(item)
    
    _fix(redacted)
    return redacted


def _redact_chunk(chunk, forbidden_names=None):
    """Redact a single JSON-serializable chunk and return parsed result."""
    chunk_str = json.dumps(chunk, indent=2)
    # Detect if chunk contains animal/pet name fields for extra emphasis
    extra = ""
    if '"animal_name"' in chunk_str:
        forbidden_str = ""
        if forbidden_names:
            forbidden_str = (
                f" Do NOT use any of these names as replacements: "
                f"{', '.join(sorted(forbidden_names))}."
            )
        extra = (
            "\nCRITICAL: Every \"animal_name\" value MUST be replaced with a "
            "DIFFERENT pet name. Do not keep any original animal_name values."
            f"{forbidden_str}\n"
        )
    prompt = (
        f"Apply differential privacy and redact sensitive personal information:\n\n"
        f"{chunk_str}\n\n{_REDACTION_RULES}{extra}"
    )
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


def _redact_large_dict(data, forbidden_names=None):
    """Chunk a large dict by splitting nested lists, then redact."""
    result = {}
    for key, value in data.items():
        if isinstance(value, list) and len(value) > 3:
            chunk_size = 3
            redacted_list = []
            for i in range(0, len(value), chunk_size):
                chunk_result = _redact_chunk({key: value[i:i + chunk_size]}, forbidden_names)
                if isinstance(chunk_result, dict):
                    redacted_list.extend(chunk_result.get(key, []))
                elif isinstance(chunk_result, list):
                    redacted_list.extend(chunk_result)
            result[key] = redacted_list
        else:
            result[key] = value
    # If result is still large, just send it as-is (best effort)
    if json.dumps(result).strip() == '{}':
        return _redact_chunk(data, forbidden_names)
    return _redact_chunk(result, forbidden_names)


def redact_data(data):
    """
    AI-powered redactor that applies differential privacy and removes sensitive PII.
    Chunks large inputs to stay within LLM token limits (~2000 tokens per chunk).
    """
    try:
        # Extract pet/animal names from the full dataset to avoid
        # cross-chunk collisions when the LLM picks replacement names
        forbidden_names = _extract_pet_names(data)

        # For list payloads, chunk to stay under token limit
        if isinstance(data, list):
            data_str = json.dumps(data)
            if len(data) > 3 or len(data_str) > 6000:
                # Process each list element individually if large,
                # or in small chunks
                redacted_chunks = []
                for item in data:
                    item_str = json.dumps(item)
                    if isinstance(item, dict) and len(item_str) > 6000:
                        # Chunk nested lists within this dict
                        redacted_item = _redact_large_dict(item, forbidden_names)
                    else:
                        redacted_item = _redact_chunk(item, forbidden_names)
                    if isinstance(redacted_item, list):
                        redacted_chunks.extend(redacted_item)
                    else:
                        redacted_chunks.append(redacted_item)
                return _fix_pet_name_collisions(redacted_chunks, forbidden_names)
            result = _redact_chunk(data, forbidden_names)
            return _fix_pet_name_collisions(result, forbidden_names)

        # For dict payloads, check size and chunk nested lists if needed
        data_str = json.dumps(data)
        if len(data_str) > 6000:
            result = _redact_large_dict(data, forbidden_names)
            return _fix_pet_name_collisions(result, forbidden_names)

        result = _redact_chunk(data, forbidden_names)
        return _fix_pet_name_collisions(result, forbidden_names)

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
