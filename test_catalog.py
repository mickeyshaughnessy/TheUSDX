"""Unit tests for catalog matching — no running server required."""
import catalog


def test_public_view_strips_url():
    listing = catalog.get_listing('co-traffic-counts-2025')
    assert listing and listing.get('url')
    pub = catalog.public_view(listing)
    assert 'url' not in pub
    assert pub.get('has_url') is True
    assert pub['id'] == 'co-traffic-counts-2025'


def test_match_colorado_traffic_keyword_only():
    catalog._llm_rerank = lambda query, candidates: []
    matches = catalog.match_listings('traffic data for Colorado in 2025', top_k=3)
    assert matches, 'expected at least one match'
    assert matches[0]['id'] == 'co-traffic-counts-2025'
    assert 'url' not in matches[0]
    assert matches[0]['match_score'] >= 0.5


def test_match_does_not_leak_other_urls():
    catalog._llm_rerank = lambda query, candidates: []
    matches = catalog.match_listings('EU electricity prices 2024', top_k=3)
    assert matches
    assert matches[0]['id'] == 'eu-day-ahead-energy-2024'
    for m in matches:
        assert 'url' not in m
        assert 'seller_email' not in m


def test_add_listing_keeps_url_private():
    listing = catalog.add_listing({
        'title': 'Unit Test Weather Grid',
        'description': 'Hourly weather observations for unit tests',
        'url': 'https://example.com/weather-grid.json',
        'keywords': 'weather, hourly, observations',
        'geography': 'Utah',
        'time_range': '2024',
        'category': 'weather',
        'price_usd': 1.25,
        'delivery': 'url',
    })
    assert listing['url'] == 'https://example.com/weather-grid.json'
    pub = catalog.public_view(listing)
    assert 'url' not in pub
    assert pub['has_url'] is True
    fetched = catalog.get_listing(listing['id'])
    assert fetched['url'] == 'https://example.com/weather-grid.json'
    # cleanup
    remaining = [x for x in catalog._load_local() if x.get('id') != listing['id']]
    catalog._save_local(remaining)


if __name__ == '__main__':
    test_public_view_strips_url()
    print('  ✓ public view strips url')
    test_match_colorado_traffic_keyword_only()
    print('  ✓ colorado traffic matches')
    test_match_does_not_leak_other_urls()
    print('  ✓ energy match, no url leak')
    test_add_listing_keeps_url_private()
    print('  ✓ seller listing stores url privately')
    print('All catalog tests passed.')
