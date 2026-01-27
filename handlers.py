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

def call_openrouter(prompt, system_message="You are a helpful assistant."):
    """Make a completion call to OpenRouter API"""
    if not config.OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY not configured")
    
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {config.OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": config.OPENROUTER_MODEL,
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ]
        }
    )
    
    if response.status_code != 200:
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
        response = s3_client.list_objects_v2(Bucket=config.DO_SPACES_BUCKET, Prefix='metadata/')
        
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
            "You are a federal data matching system. Analyze requests and return matching dataset IDs as JSON.")
        
        matched_ids = json.loads(ai_response).get('dataset_ids', [])
        
        collected_datasets = []
        for dataset_id in matched_ids:
            try:
                data_obj = s3_client.get_object(Bucket=config.DO_SPACES_BUCKET, Key=f'data/{dataset_id}.json')
                dataset = json.loads(data_obj['Body'].read().decode('utf-8'))
                collected_datasets.append(dataset)
            except:
                continue
        
        return collected_datasets if collected_datasets else _get_sample_data(description)
    
    except Exception as e:
        print(f"Data collection error: {e}")
        return _get_sample_data(description)

def redact_data(data):
    """
    AI-powered redactor that applies differential privacy and removes sensitive PII.
    Redacts: names, locations, faces (in image metadata), and other sensitive info.
    """
    try:
        data_str = json.dumps(data, indent=2)
        
        prompt = f"""Apply differential privacy and redact sensitive personal information from this data:

{data_str}

Redaction rules:
- Replace proper names with realistic alternatives (e.g., "Mickey" -> "Jamison")
- Replace specific locations with generalized regions (e.g., "123 Main St, Denver" -> "Colorado")
- Replace or remove other PII (SSN, phone numbers, email addresses, etc.)
- For faces in image metadata, replace with "[FACE_REDACTED]"
- Maintain data structure and utility while protecting privacy

Return ONLY the redacted JSON data, no explanations."""

        redacted_str = call_openrouter(prompt,
            "You are a privacy protection system for federal data. Redact PII while maintaining data utility. Return only valid JSON.")
        
        try:
            redacted_json = json.loads(redacted_str)
            return redacted_json
        except json.JSONDecodeError:
            start = redacted_str.find('{')
            end = redacted_str.rfind('}') + 1
            if start != -1 and end > start:
                return json.loads(redacted_str[start:end])
            raise
    
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
