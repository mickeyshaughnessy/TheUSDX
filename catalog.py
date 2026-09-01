"""
Dataset catalog for the Acme Redactors data market.

Sellers list a pointer (metadata + private URL). Buyers browse and match
against metadata only — source URLs are withheld until a (demo) purchase.
After payment the API returns the URL, redacted records, or both.
"""
from __future__ import annotations

import json
import os
import re
import hashlib
import ipaddress
import socket
from datetime import datetime
from urllib.parse import urlparse

import requests

import config

LOCAL_STORE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.catalog_listings.json')

PUBLIC_FIELDS = (
    'id', 'title', 'description', 'category', 'keywords',
    'geography', 'time_range', 'license', 'price_usd',
    'delivery', 'source_name', 'created_at', 'record_count_est',
    'builtin', 'synthetic',
)

_STOP = {
    'the', 'a', 'an', 'for', 'in', 'of', 'and', 'or', 'to', 'on', 'at',
    'with', 'from', 'by', 'is', 'are', 'be', 'this', 'that', 'data',
    'dataset', 'datasets', 'records', 'record', 'please', 'show', 'get',
    'need', 'want', 'looking', 'find', 'request', 'query',
}

# Extra market listings (not US-gov FOIA demos). URLs are private until purchase.
MARKET_LISTINGS = [
    {
        'id': 'co-traffic-counts-2025',
        'title': 'Colorado Statewide Traffic Counts 2025',
        'description': (
            'Hourly and AADT traffic counts for Colorado highways and arterial roads '
            'in calendar year 2025, including station IDs, route, county, and vehicle class.'
        ),
        'category': 'transportation',
        'keywords': [
            'traffic', 'colorado', 'dot', 'aadt', 'highway', 'counts',
            'vehicles', 'roads', '2025', 'transportation', 'cdot',
        ],
        'geography': 'Colorado',
        'time_range': '2025',
        'license': 'Demo / synthetic',
        'price_usd': 2.50,
        'delivery': 'both',
        'source_name': 'Acme Market (synthetic CDOT-style)',
        'url': 'https://datasets.acmeredactors.example/co-traffic-counts-2025.json',
        'synthetic': True,
        'builtin': True,
        'records': {
            'source': 'Colorado Department of Transportation — Traffic Volume Program (synthetic)',
            'year': 2025,
            'records': [
                {
                    'station_id': 'CDOT-I25-214',
                    'route': 'I-25',
                    'county': 'Denver',
                    'location': 'I-25 at 20th Street, Denver, CO',
                    'aadt': 248100,
                    'peak_hour': '07:00-08:00',
                    'peak_volume': 18420,
                    'contact_name': 'Marisol Vega',
                    'contact_email': 'mvega@example.cdothub.test',
                    'contact_phone': '303-555-0142',
                },
                {
                    'station_id': 'CDOT-US36-088',
                    'route': 'US-36',
                    'county': 'Boulder',
                    'location': 'US-36 at Foothills Parkway, Boulder, CO',
                    'aadt': 97200,
                    'peak_hour': '16:00-17:00',
                    'peak_volume': 8104,
                    'contact_name': 'James K. Ellroy',
                    'contact_email': 'jellroy@example.cdothub.test',
                    'contact_phone': '720-555-0198',
                },
                {
                    'station_id': 'CDOT-I70-441',
                    'route': 'I-70',
                    'county': 'Jefferson',
                    'location': 'I-70 at C-470 interchange, Golden, CO',
                    'aadt': 131500,
                    'peak_hour': '15:00-16:00',
                    'peak_volume': 11280,
                    'contact_name': 'Priya Nandakumar',
                    'contact_email': 'pnanda@example.cdothub.test',
                    'contact_phone': '303-555-0281',
                },
            ],
        },
    },
    {
        'id': 'eu-day-ahead-energy-2024',
        'title': 'EU Day-Ahead Electricity Prices 2024',
        'description': (
            'Hourly day-ahead wholesale electricity prices for selected European bidding '
            'zones in 2024, in EUR/MWh, with zone, timestamp, and volume.'
        ),
        'category': 'energy',
        'keywords': [
            'energy', 'electricity', 'prices', 'europe', 'eu', 'wholesale',
            'day-ahead', '2024', 'mwh', 'power',
        ],
        'geography': 'European Union',
        'time_range': '2024',
        'license': 'Demo / synthetic',
        'price_usd': 3.00,
        'delivery': 'both',
        'source_name': 'Acme Market (synthetic ENTSO-E-style)',
        'url': 'https://datasets.acmeredactors.example/eu-day-ahead-energy-2024.json',
        'synthetic': True,
        'builtin': True,
        'records': {
            'source': 'ENTSO-E Transparency Platform (synthetic extract)',
            'year': 2024,
            'unit': 'EUR/MWh',
            'records': [
                {'zone': 'DE-LU', 'timestamp': '2024-01-08T18:00:00Z', 'price_eur_mwh': 142.31, 'volume_mwh': 51240},
                {'zone': 'FR', 'timestamp': '2024-01-08T18:00:00Z', 'price_eur_mwh': 128.04, 'volume_mwh': 43110},
                {'zone': 'ES', 'timestamp': '2024-01-08T18:00:00Z', 'price_eur_mwh': 91.55, 'volume_mwh': 28760},
            ],
        },
    },
    {
        'id': 'retail-sku-movements-q1',
        'title': 'North American Retail SKU Movements Q1',
        'description': (
            'Weekly sell-through and inventory movements for a synthetic panel of North American '
            'grocery SKUs in Q1, including store region, SKU, units, and buyer contact.'
        ),
        'category': 'retail',
        'keywords': [
            'retail', 'sku', 'inventory', 'grocery', 'sell-through', 'north america',
            'q1', 'sales', 'stores', 'commerce',
        ],
        'geography': 'North America',
        'time_range': '2025-Q1',
        'license': 'Demo / synthetic',
        'price_usd': 5.00,
        'delivery': 'url',
        'source_name': 'Acme Market (synthetic retail panel)',
        'url': 'https://datasets.acmeredactors.example/retail-sku-movements-q1.json',
        'synthetic': True,
        'builtin': True,
        'records': None,
    },
]


def _s3():
    if not getattr(config, 'DO_SPACES_KEY', None) or not getattr(config, 'DO_SPACES_SECRET', None):
        return None
    try:
        import boto3
        session = boto3.session.Session()
        return session.client(
            's3',
            region_name=config.DO_SPACES_REGION,
            endpoint_url=config.DO_SPACES_ENDPOINT,
            aws_access_key_id=config.DO_SPACES_KEY,
            aws_secret_access_key=config.DO_SPACES_SECRET,
        )
    except Exception as e:
        print(f'[catalog] s3 init failed: {e}')
        return None


def _prefix():
    return getattr(config, 'DO_SPACES_PREFIX', 'usdx/')


def _tokens(text: str) -> set:
    return {t for t in re.findall(r'[a-z0-9]+', (text or '').lower()) if t not in _STOP and len(t) > 1}


def _slug(title: str) -> str:
    base = re.sub(r'[^a-z0-9]+', '-', (title or 'dataset').lower()).strip('-')[:48] or 'dataset'
    suffix = hashlib.sha1(f'{title}{datetime.utcnow().isoformat()}'.encode()).hexdigest()[:8]
    return f'{base}-{suffix}'


def public_view(listing: dict) -> dict:
    """Metadata only — never include source URL or seller email."""
    out = {k: listing.get(k) for k in PUBLIC_FIELDS if k in listing or listing.get(k) is not None}
    out['id'] = listing.get('id')
    out['title'] = listing.get('title')
    out['description'] = listing.get('description')
    out['category'] = listing.get('category') or 'general'
    out['keywords'] = listing.get('keywords') or []
    out['geography'] = listing.get('geography') or ''
    out['time_range'] = listing.get('time_range') or ''
    out['license'] = listing.get('license') or ''
    out['price_usd'] = float(listing.get('price_usd') or 0)
    out['delivery'] = listing.get('delivery') or 'url'
    out['source_name'] = listing.get('source_name') or listing.get('source') or ''
    out['created_at'] = listing.get('created_at') or ''
    out['record_count_est'] = listing.get('record_count_est')
    if out['record_count_est'] is None and listing.get('records'):
        recs = listing['records']
        if isinstance(recs, dict) and isinstance(recs.get('records'), list):
            out['record_count_est'] = len(recs['records'])
        elif isinstance(recs, list):
            out['record_count_est'] = len(recs)
    out['has_records'] = bool(listing.get('records') or listing.get('has_records'))
    out['has_url'] = bool(listing.get('url'))
    out['builtin'] = bool(listing.get('builtin'))
    out['synthetic'] = bool(listing.get('synthetic', listing.get('builtin')))
    return out


def _foia_listings() -> list:
    try:
        from seed_data import DATASETS
    except Exception:
        return []
    out = []
    for ds in DATASETS:
        records = ds.get('data')
        rec_count = None
        if isinstance(records, dict) and isinstance(records.get('records'), list):
            rec_count = len(records['records'])
        out.append({
            'id': ds['id'],
            'title': ds.get('title') or ds['id'],
            'description': ds.get('description') or '',
            'category': ds.get('category') or 'government',
            'keywords': ds.get('keywords') or [],
            'geography': 'United States',
            'time_range': '',
            'license': 'Demo / synthetic FOIA records',
            'price_usd': 0.25,
            'delivery': 'redacted',
            'source_name': (records or {}).get('source') if isinstance(records, dict) else 'Acme FOIA demo',
            'url': None,
            'records': None,
            'has_records': True,
            'synthetic': True,
            'builtin': True,
            'record_count_est': rec_count,
            'created_at': '',
        })
    return out


def _load_local() -> list:
    if not os.path.exists(LOCAL_STORE):
        return []
    try:
        with open(LOCAL_STORE, 'r') as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception as e:
        print(f'[catalog] local load failed: {e}')
        return []


def _save_local(listings: list) -> None:
    try:
        with open(LOCAL_STORE, 'w') as f:
            json.dump(listings, f, indent=2)
    except Exception as e:
        print(f'[catalog] local save failed: {e}')


def _load_remote() -> list:
    s3 = _s3()
    if not s3:
        return []
    listings = []
    try:
        prefix = f'{_prefix()}catalog/'
        resp = s3.list_objects_v2(Bucket=config.DO_SPACES_BUCKET, Prefix=prefix)
        for obj in resp.get('Contents') or []:
            try:
                body = s3.get_object(Bucket=config.DO_SPACES_BUCKET, Key=obj['Key'])['Body'].read()
                listings.append(json.loads(body.decode('utf-8')))
            except Exception:
                continue
    except Exception as e:
        print(f'[catalog] remote load failed: {e}')
    return listings


def _save_remote(listing: dict) -> bool:
    s3 = _s3()
    if not s3:
        return False
    try:
        key = f"{_prefix()}catalog/{listing['id']}.json"
        s3.put_object(
            Bucket=config.DO_SPACES_BUCKET,
            Key=key,
            Body=json.dumps(listing, indent=2),
            ContentType='application/json',
        )
        return True
    except Exception as e:
        print(f'[catalog] remote save failed: {e}')
        return False


def all_listings() -> list:
    """Builtin + persisted seller listings. Last writer of a given id wins (user listings override)."""
    by_id = {}
    for src in (_foia_listings(), MARKET_LISTINGS, _load_remote(), _load_local()):
        for item in src:
            if item.get('id'):
                by_id[item['id']] = item
    return list(by_id.values())


def get_listing(dataset_id: str):
    if not dataset_id:
        return None
    for item in all_listings():
        if item.get('id') == dataset_id:
            return item
    return None


def add_listing(payload: dict) -> dict:
    title = (payload.get('title') or '').strip()
    description = (payload.get('description') or '').strip()
    url = (payload.get('url') or '').strip()
    if not title or not description:
        raise ValueError('title and description are required')
    if url:
        parsed = urlparse(url)
        if parsed.scheme not in ('http', 'https') or not parsed.netloc:
            raise ValueError('url must be an http(s) URL')

    keywords = payload.get('keywords') or []
    if isinstance(keywords, str):
        keywords = [k.strip() for k in re.split(r'[,;]', keywords) if k.strip()]

    delivery = payload.get('delivery') or ('both' if url else 'redacted')
    if delivery not in ('url', 'redacted', 'both'):
        raise ValueError('delivery must be url, redacted, or both')

    listing = {
        'id': payload.get('id') or _slug(title),
        'title': title,
        'description': description,
        'category': (payload.get('category') or 'general').strip(),
        'keywords': keywords,
        'geography': (payload.get('geography') or '').strip(),
        'time_range': (payload.get('time_range') or '').strip(),
        'license': (payload.get('license') or '').strip(),
        'price_usd': float(payload.get('price_usd') or 0),
        'delivery': delivery,
        'source_name': (payload.get('source_name') or payload.get('source') or '').strip(),
        'url': url or None,
        'seller_email': (payload.get('seller_email') or '').strip() or None,
        'synthetic': bool(payload.get('synthetic', False)),
        'builtin': False,
        'created_at': datetime.utcnow().isoformat(),
        'records': payload.get('records'),
        'record_count_est': payload.get('record_count_est'),
    }
    if get_listing(listing['id']) and get_listing(listing['id']).get('builtin'):
        listing['id'] = _slug(title)

    local = [x for x in _load_local() if x.get('id') != listing['id']]
    local.append(listing)
    _save_local(local)
    _save_remote(listing)
    return listing


def keyword_score(query: str, listing: dict) -> float:
    q_tokens = _tokens(query)
    if not q_tokens:
        return 0.0
    blob = ' '.join([
        listing.get('title') or '',
        listing.get('description') or '',
        listing.get('category') or '',
        listing.get('geography') or '',
        listing.get('time_range') or '',
        listing.get('source_name') or '',
        ' '.join(listing.get('keywords') or []),
    ])
    h_tokens = _tokens(blob)
    overlap = q_tokens & h_tokens
    score = len(overlap) / max(len(q_tokens), 1)
    q_lower = query.lower()
    geo = (listing.get('geography') or '').lower()
    if geo and geo in q_lower:
        score += 0.25
    tr = str(listing.get('time_range') or '')
    if tr and tr.lower() in q_lower:
        score += 0.2
    years = re.findall(r'\b(20\d{2})\b', query)
    for y in years:
        if y in blob:
            score += 0.15
            break
    for kw in listing.get('keywords') or []:
        if kw.lower() in q_lower:
            score += 0.08
    title = (listing.get('title') or '').lower()
    if title and title in q_lower:
        score += 0.3
    return round(min(score, 1.0), 4)


def _llm_rerank(query: str, candidates: list) -> list:
    """Optional LLM re-rank. Returns list of {id, score, reason}. Never sees URLs."""
    try:
        from handlers import call_openrouter
    except Exception:
        return []
    if not getattr(config, 'OPENROUTER_API_KEY', None):
        return []
    meta = [public_view(c) for c in candidates]
    for m in meta:
        m.pop('has_url', None)
    prompt = (
        f'Buyer query: "{query}"\n\nCatalog metadata (no source URLs):\n'
        f'{json.dumps(meta, indent=2)}\n\n'
        'Return JSON only: {"matches": [{"id": "...", "score": 0.0, "reason": "short"}]} '
        'Rank best first. score is 0-1. Omit irrelevant datasets (score < 0.35).'
    )
    try:
        raw = call_openrouter(
            prompt,
            'You match buyer queries to dataset metadata for a data market. '
            'Return ONLY JSON. Never invent URLs or mention source links.',
        )
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            start = raw.find('{')
            end = raw.rfind('}') + 1
            parsed = json.loads(raw[start:end]) if start != -1 and end > start else {}
        matches = parsed.get('matches') or []
        out = []
        for m in matches:
            if isinstance(m, dict) and m.get('id'):
                out.append({
                    'id': m['id'],
                    'score': float(m.get('score') or 0),
                    'reason': (m.get('reason') or '').strip(),
                })
        return out
    except Exception as e:
        print(f'[catalog] llm rerank failed: {e}')
        return []


def match_listings(query: str, top_k: int = 5) -> list:
    query = (query or '').strip()
    if not query:
        return []
    listings = all_listings()
    scored = []
    for listing in listings:
        ks = keyword_score(query, listing)
        if ks <= 0:
            continue
        scored.append((ks, listing))
    scored.sort(key=lambda x: x[0], reverse=True)
    shortlist = [item for _, item in scored[: max(top_k * 3, 8)]]
    if not shortlist:
        return []

    llm = _llm_rerank(query, shortlist)
    llm_by_id = {m['id']: m for m in llm}
    results = []
    seen = set()
    if llm:
        for m in llm:
            listing = next((x for x in listings if x.get('id') == m['id']), None)
            if not listing:
                continue
            ks = keyword_score(query, listing)
            combined = round(min(1.0, 0.55 * float(m['score']) + 0.45 * ks), 4)
            if combined < 0.2:
                continue
            row = public_view(listing)
            row['match_score'] = combined
            row['match_reason'] = m.get('reason') or 'Matched on metadata.'
            results.append(row)
            seen.add(listing['id'])
            if len(results) >= top_k:
                return results

    for ks, listing in scored:
        if listing['id'] in seen:
            continue
        if ks < 0.15:
            continue
        row = public_view(listing)
        row['match_score'] = ks
        bits = []
        if listing.get('geography') and listing['geography'].lower() in query.lower():
            bits.append(listing['geography'])
        if listing.get('time_range') and str(listing['time_range']).lower() in query.lower():
            bits.append(str(listing['time_range']))
        overlap = _tokens(query) & _tokens(' '.join(listing.get('keywords') or []) + ' ' + (listing.get('title') or ''))
        if overlap:
            bits.append(', '.join(sorted(overlap)[:6]))
        row['match_reason'] = 'Matched on ' + ('; '.join(bits) if bits else 'title and description tokens') + '.'
        results.append(row)
        if len(results) >= top_k:
            break
    return results


def listing_records(listing: dict):
    recs = listing.get('records')
    if recs:
        return recs
    # Builtin FOIA payloads live on seed_data
    if listing.get('builtin'):
        try:
            from seed_data import DATASETS
            for ds in DATASETS:
                if ds['id'] == listing['id']:
                    return {'id': ds['id'], 'category': ds.get('category'), 'data': ds.get('data')}
        except Exception:
            pass
        for m in MARKET_LISTINGS:
            if m['id'] == listing['id'] and m.get('records'):
                return m['records']
    return None


def _is_private_host(host: str) -> bool:
    if not host:
        return True
    host = host.lower().rstrip('.')
    if host in ('localhost', 'localhost.localdomain') or host.endswith('.local'):
        return True
    try:
        infos = socket.getaddrinfo(host, None)
    except Exception:
        return True
    for info in infos:
        ip = info[4][0]
        try:
            addr = ipaddress.ip_address(ip)
        except ValueError:
            continue
        if (
            addr.is_private or addr.is_loopback or addr.is_link_local
            or addr.is_reserved or addr.is_multicast or addr.is_unspecified
        ):
            return True
    return False


def safe_fetch_json(url: str, max_bytes: int = 400_000):
    """Fetch a public JSON pointer. Blocks private/link-local hosts (SSRF)."""
    parsed = urlparse(url or '')
    if parsed.scheme not in ('http', 'https') or not parsed.netloc:
        return None, 'url must be http(s)'
    if _is_private_host(parsed.hostname):
        return None, 'refusing to fetch private or local host'
    try:
        r = requests.get(url, timeout=12, stream=True, allow_redirects=True)
        if r.status_code != 200:
            return None, f'upstream status {r.status_code}'
        final = urlparse(r.url)
        if final.scheme not in ('http', 'https') or _is_private_host(final.hostname):
            return None, 'refusing redirect to private host'
        buf = b''
        for chunk in r.iter_content(8192):
            buf += chunk
            if len(buf) > max_bytes:
                return None, 'payload too large'
        return json.loads(buf.decode('utf-8')), None
    except Exception as e:
        return None, str(e)
