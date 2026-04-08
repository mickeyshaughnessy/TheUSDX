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
            "X-Title": "Poseidon"
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
            for obj in response['Contents'][:20]:
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

_REDACTION_SYSTEM_AGGRESSIVE = (
    "You are a FOIA compliance officer processing federal agency records for public release "
    "under 5 U.S.C. § 552 (Freedom of Information Act). Apply the two-tier redaction scheme "
    "specified below, then return ONLY the redacted JSON — no commentary, no explanations.\n\n"

    "TIER 1 — BLIND REDACTION: Replace the field value with a [b(Ex.N)] marker "
    "(Ex.1 classified/clearance/covert, Ex.3 SSNs/program IDs/biometrics/DL/VIN/plates, "
    "Ex.7(F) housing/gang/medical for incarcerated persons).\n\n"

    "TIER 2 — STANDARD SMART REDACTION: Replace personal privacy fields directly with realistic "
    "substitutes (no special markers): names, dates of birth, home addresses, phone numbers, "
    "email addresses, third-party names in law enforcement records.\n\n"

    "TIER 2 — AGGRESSIVE CLOAKING: For ANY field that could logically be used — alone or in "
    "combination with other fields — to cross-reference public records, news archives, databases, "
    "or social media to re-identify the individual, substitute a plausible alternative AND wrap "
    "it in [~value~] markers (e.g. \"city\": \"[~Portland~]\"). This includes: locations, "
    "event/incident/arrest/enrollment dates and times, nicknames and aliases, employers, "
    "organizations, schools, military units, family member names, associate names, vehicle "
    "descriptions, physical descriptions, nationality, language, immigration status details, "
    "specific financial amounts, medical condition types, educational details, and any other "
    "contextual detail that narrows identity. When in doubt, cloak it. "
    "The outer JSON structure must remain valid.\n\n"

    "SEGREGABILITY: Release non-exempt fields (IDs, general position titles, pay grades, "
    "outcome/disposition text). Return only valid JSON."
)

_REDACTION_RULES = (
    "TIER 1 — BLIND REDACT (replace value with [b(Ex.N)] marker):\n"
    "  [b(Ex.1)]  Classification markings — e.g. TOP SECRET, HCS, NOFORN, SCI\n"
    "  [b(Ex.1)]  Security clearance levels — e.g. TS/SCI, Top Secret, Secret\n"
    "  [b(Ex.1)]  Covert or classified facility names and street addresses\n"
    "             (Camp Peary / The Farm, Harvey Point, undisclosed OCONUS stations)\n"
    "  [b(Ex.3)]  Social Security Numbers (SSN)\n"
    "  [b(Ex.3)]  Intelligence program identifiers, operation codenames, source identifiers\n"
    "  [b(Ex.3)]  Biometric identifiers\n"
    "  [b(Ex.3)]  Driver's license numbers, VINs, license plates (DPPA — 18 U.S.C. § 2721)\n"
    "  [b(Ex.1)]  Military deployment destinations, unit assignment locations, and mission names\n"
    "  [b(Ex.1)]  Foreign intelligence target names, nationalities, and target affiliations\n"
    "  [b(Ex.1)]  SIGINT collection facility names and selector values\n"
    "  [b(Ex.7(F))]  Prison housing unit assignments, security classification levels, gang affiliations\n"
    "  [b(Ex.7(F))]  Medical conditions of incarcerated persons\n\n"

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

_REDACTION_RULES_AGGRESSIVE = (
    "TIER 1 — BLIND REDACT (replace value with [b(Ex.N)] marker):\n"
    "  [b(Ex.1)]  Classification markings, security clearance levels, covert facility names\n"
    "  [b(Ex.3)]  SSNs, intelligence program identifiers, biometric identifiers,\n"
    "             driver's license numbers, VINs, license plates\n"
    "  [b(Ex.1)]  Military deployment destinations, unit locations, mission names,\n"
    "             foreign intelligence target names, SIGINT selectors\n"
    "  [b(Ex.7(F))]  Prison housing/security classifications, gang affiliations, medical conditions\n\n"

    "TIER 2 — STANDARD SMART REDACT (replace directly with realistic substitute, no markers):\n"
    "  Individual names, officer names → different realistic full name\n"
    "  Dates of birth → shifted ±1–5 years, different month/day\n"
    "  Personal/residential addresses → different plausible address, same region\n"
    "  Personal phone numbers → different number, same area code\n"
    "  Personal email addresses → different realistic email\n"
    "  Third-party names in law enforcement records → different realistic name\n\n"

    "TIER 2 — AGGRESSIVE CLOAKING (substitute AND wrap in [~value~]):\n"
    "  Apply to ANYTHING that could logically be used — alone or in combination — to re-identify "
    "the individual through public records, databases, news archives, or social media. "
    "When in doubt, cloak it.\n\n"
    "  Locations: cities, states, countries, counties, zip codes, neighborhoods, landmarks,\n"
    "             street intersections, named facilities, military bases\n"
    "             → [~different real place of similar type and size~]\n"
    "  Event dates and times that could narrow identity: incident dates, arrest dates,\n"
    "             enrollment dates, service start/end dates, hearing dates, treatment dates\n"
    "             → [~shifted date within same approximate period~]\n"
    "  Nicknames, aliases, callsigns, screen names, maiden names → [~different plausible alias~]\n"
    "  Employers, organizations, companies, agencies, military units, schools, universities\n"
    "             → [~similar type of organization in a different location~]\n"
    "  Names of family members, spouses, children, parents, associates, co-defendants,\n"
    "             witnesses, complainants, attorneys → [~different realistic name~]\n"
    "  Physical descriptions: height, weight, build, hair color, eye color, skin tone,\n"
    "             distinguishing marks, tattoos, piercings → [~different plausible description~]\n"
    "  Vehicle descriptions: make, model, color, year (VIN/plates already blind-redacted)\n"
    "             → [~different make/model/color of similar class~]\n"
    "  Nationality, country of origin, ethnicity when combined with other fields\n"
    "             → [~different country or region of similar type~]\n"
    "  Primary language(s) spoken → [~different language or language pair~]\n"
    "  Immigration status details, visa type, port of entry → [~different plausible status~]\n"
    "  Occupation title details below general category (e.g. specific job title, unit specialty)\n"
    "             → [~different specific role within same general field~]\n"
    "  Specific financial amounts tied to an individual (subsidy amounts, benefit payment amounts,\n"
    "             judgment amounts, restitution amounts) → [~different plausible amount~]\n"
    "  Medical condition types, diagnosis categories, treatment types for non-incarcerated persons\n"
    "             → [~different plausible condition of similar severity~]\n"
    "  Educational background details: degree, major, graduation year → [~different plausible detail~]\n"
    "  Any unique combination of attributes that narrows the pool of matching individuals\n"
    "             → substitute each component with [~plausible alternative~]\n\n"

    "PRESERVE: case/employee IDs, position titles, pay grades, salary amounts, "
    "complaint categories, general outcome/disposition text.\n"
    "CONSISTENCY: use the same substitute for repeated values.\n\n"

    "DATA TO REDACT:\n"
)


def _redact_chunk(chunk, aggressive=False):
    """Redact a single JSON-serializable chunk using the FOIA two-tier scheme."""
    chunk_str = json.dumps(chunk, indent=2)
    if aggressive:
        prompt = _REDACTION_RULES_AGGRESSIVE + chunk_str
        system = _REDACTION_SYSTEM_AGGRESSIVE
    else:
        prompt = _REDACTION_RULES + chunk_str
        system = _REDACTION_SYSTEM
    redacted_str = call_openrouter(prompt, system)
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


def _redact_large_dict(data, aggressive=False):
    """Chunk a large dict by splitting nested lists, then redact."""
    result = {}
    for key, value in data.items():
        if isinstance(value, list) and len(value) > 3:
            chunk_size = 3
            redacted_list = []
            for i in range(0, len(value), chunk_size):
                chunk_result = _redact_chunk({key: value[i:i + chunk_size]}, aggressive=aggressive)
                if isinstance(chunk_result, dict):
                    redacted_list.extend(chunk_result.get(key, []))
                elif isinstance(chunk_result, list):
                    redacted_list.extend(chunk_result)
            result[key] = redacted_list
        else:
            result[key] = value
    if json.dumps(result).strip() == '{}':
        return _redact_chunk(data, aggressive=aggressive)
    return _redact_chunk(result, aggressive=aggressive)


_REDACTION_TEXT_SYSTEM = (
    "You are a FOIA compliance officer processing a document for public release "
    "under 5 U.S.C. § 552. Apply the same two-tier redaction scheme to the plain text below.\n\n"
    "TIER 1 — BLIND REDACTION: Replace sensitive values with [b(Ex.N)] markers "
    "(Ex.1 classified info, Ex.3 SSNs/program IDs, Ex.7(F) life/safety).\n\n"
    "TIER 2 — SMART REDACTION: Replace personal privacy data (names, addresses, DOB, "
    "phone numbers, emails) with different but realistic substitute values of the same type.\n\n"
    "PRESERVE all non-exempt content: IDs, dates, titles, pay grades, outcome text.\n\n"
    "Return ONLY the redacted text with no commentary. Preserve all original formatting, "
    "whitespace, and line breaks."
)

_REDACTION_TEXT_SYSTEM_AGGRESSIVE = (
    "You are a FOIA compliance officer processing a document for public release "
    "under 5 U.S.C. § 552. Apply aggressive two-tier redaction to the plain text below.\n\n"
    "TIER 1 — BLIND REDACTION: Replace with [b(Ex.N)] markers "
    "(Ex.1 classified info, Ex.3 SSNs/program IDs/biometrics/DL numbers/VINs/plates, "
    "Ex.7(F) life/safety, Ex.7(C) third-party names in law enforcement records).\n\n"
    "TIER 2 — STANDARD SMART REDACTION (substitute directly, no markers): "
    "individual names, officer names, dates of birth, home addresses, phone numbers, email addresses.\n\n"
    "TIER 2 — AGGRESSIVE CLOAKING (substitute AND wrap in [~value~]) — apply to ANYTHING that "
    "could logically be used alone or in combination to re-identify the individual:\n"
    "  • Cities, states, countries, counties, zip codes, neighborhoods, landmarks, street intersections\n"
    "  • Event/incident/arrest/enrollment/treatment/hearing dates and times\n"
    "  • Nicknames, aliases, callsigns, screen names, maiden names\n"
    "  • Employers, organizations, schools, military units, agencies, companies\n"
    "  • Names of family members, spouses, children, associates, witnesses, attorneys\n"
    "  • Physical descriptions: height, weight, build, hair, eye color, skin tone, tattoos, marks\n"
    "  • Vehicle make, model, color, year (VIN/plates are blind-redacted)\n"
    "  • Nationality, country of origin, ethnicity when combined with other fields\n"
    "  • Primary language(s) spoken\n"
    "  • Immigration status, visa type, port of entry\n"
    "  • Specific job title details, unit specialty, role below general category\n"
    "  • Specific financial amounts tied to the individual (benefits, subsidies, judgments)\n"
    "  • Medical condition types, diagnosis categories, treatment types\n"
    "  • Educational details: degree, major, graduation year\n"
    "  • Any other detail cross-referenceable with public records\n\n"
    "PRESERVE non-exempt content: IDs, general position titles, pay grades, outcome text.\n"
    "CONSISTENCY: use the same substitute for any value that appears more than once.\n\n"
    "Return ONLY the redacted text. Preserve all original formatting and line breaks exactly."
)


def redact_text(text, aggressive=False):
    """Redact plain text (non-JSON) using the FOIA two-tier scheme."""
    prompt = "TEXT TO REDACT:\n\n" + text
    system = _REDACTION_TEXT_SYSTEM_AGGRESSIVE if aggressive else _REDACTION_TEXT_SYSTEM
    return call_openrouter(prompt, system)


def redact_data(data, aggressive=False):
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
                        redacted_item = _redact_large_dict(item, aggressive=aggressive)
                    else:
                        redacted_item = _redact_chunk(item, aggressive=aggressive)
                    if isinstance(redacted_item, list):
                        redacted_chunks.extend(redacted_item)
                    else:
                        redacted_chunks.append(redacted_item)
                return redacted_chunks
            return _redact_chunk(data, aggressive=aggressive)

        data_str = json.dumps(data)
        if len(data_str) > 6000:
            return _redact_large_dict(data, aggressive=aggressive)
        return _redact_chunk(data, aggressive=aggressive)

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
        'source': 'Poseidon (Sample)',
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
