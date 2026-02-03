import requests
import time
import sys

BASE_URL = 'http://localhost:6732'

def print_test(name):
    print(f'\n→ Testing: {name}')

def print_success(message):
    print(f'  ✓ {message}')

def print_error(message):
    print(f'  ✗ {message}')
    
def print_info(message):
    print(f'  ℹ {message}')

def test_ping():
    print_test('GET /ping')
    try:
        start = time.time()
        response = requests.get(f'{BASE_URL}/ping')
        latency = (time.time() - start) * 1000
        
        assert response.status_code == 200, f'Expected 200, got {response.status_code}'
        data = response.json()
        assert data['status'] == 'ok', f'Expected status ok, got {data["status"]}'
        
        print_success(f'Ping successful (latency: {latency:.2f}ms)')
        print_info(f'Timestamp: {data["timestamp"]}')
        return True
    except Exception as e:
        print_error(f'Failed: {e}')
        return False

def test_signup():
    print_test('POST /signup')
    try:
        test_email = f'test_{int(time.time())}@example.com'
        response = requests.post(f'{BASE_URL}/signup', json={
            'email': test_email,
            'password': 'TestPassword123!'
        })
        
        assert response.status_code == 201, f'Expected 201, got {response.status_code}'
        data = response.json()
        assert 'token' in data, 'No token in response'
        
        print_success('User signup successful')
        print_info(f'Email: {test_email}')
        return data['token'], test_email
    except Exception as e:
        print_error(f'Failed: {e}')
        return None, None

def test_login(email, password):
    print_test('POST /login')
    try:
        response = requests.post(f'{BASE_URL}/login', json={
            'email': email,
            'password': password
        })
        
        assert response.status_code == 200, f'Expected 200, got {response.status_code}'
        data = response.json()
        assert 'token' in data, 'No token in response'
        
        print_success('Login successful')
        return data['token']
    except Exception as e:
        print_error(f'Failed: {e}')
        return None

def test_get_data_authenticated(token):
    print_test('POST /get_data (authenticated)')
    try:
        response = requests.post(f'{BASE_URL}/get_data', 
            headers={'Authorization': f'Bearer {token}'},
            json={'description': 'Census data for Colorado from 2020-2023'}
        )
        
        assert response.status_code == 200, f'Expected 200, got {response.status_code}'
        data = response.json()
        assert data['status'] == 'success', f'Expected success status'
        assert 'data' in data, 'No data in response'
        assert 'metadata' in data, 'No metadata in response'
        
        print_success('Data retrieval successful')
        print_info(f'Processing time: {data["metadata"]["processing_time_seconds"]}s')
        print_info(f'Records returned: {data["metadata"]["records_returned"]}')
        print_info(f'Privacy applied: {data["metadata"]["privacy_applied"]}')
        return True
    except Exception as e:
        print_error(f'Failed: {e}')
        return False

def test_get_data_unauthenticated():
    print_test('POST /get_data (unauthenticated - should fail)')
    try:
        response = requests.post(f'{BASE_URL}/get_data',
            json={'description': 'Some data'}
        )
        
        assert response.status_code == 401, f'Expected 401, got {response.status_code}'
        print_success('Correctly rejected unauthenticated request')
        return True
    except Exception as e:
        print_error(f'Failed: {e}')
        return False

def test_duplicate_signup(email):
    print_test('POST /signup (duplicate email - should fail)')
    try:
        response = requests.post(f'{BASE_URL}/signup', json={
            'email': email,
            'password': 'AnotherPassword123!'
        })
        
        assert response.status_code == 409, f'Expected 409, got {response.status_code}'
        print_success('Correctly rejected duplicate email')
        return True
    except Exception as e:
        print_error(f'Failed: {e}')
        return False

def test_invalid_login():
    print_test('POST /login (invalid credentials - should fail)')
    try:
        response = requests.post(f'{BASE_URL}/login', json={
            'email': 'nonexistent@example.com',
            'password': 'WrongPassword'
        })
        
        assert response.status_code == 401, f'Expected 401, got {response.status_code}'
        print_success('Correctly rejected invalid credentials')
        return True
    except Exception as e:
        print_error(f'Failed: {e}')
        return False

def test_redaction_privacy_flag(token):
    print_test('Redaction: verify privacy_applied flag')
    try:
        response = requests.post(f'{BASE_URL}/get_data',
            headers={'Authorization': f'Bearer {token}'},
            json={'description': 'Personal records with names and SSN'}
        )
        
        assert response.status_code == 200, f'Expected 200, got {response.status_code}'
        data = response.json()
        assert data['metadata']['privacy_applied'] == True, 'Privacy not applied'
        
        print_success('Privacy flag is set to true')
        return True
    except Exception as e:
        print_error(f'Failed: {e}')
        return False

def test_redaction_no_ssn_patterns(token):
    print_test('Redaction: check response excludes raw SSN patterns')
    try:
        response = requests.post(f'{BASE_URL}/get_data',
            headers={'Authorization': f'Bearer {token}'},
            json={'description': 'Test data with potential PII'}
        )
        
        assert response.status_code == 200, f'Expected 200, got {response.status_code}'
        data = response.json()
        
        import re
        data_str = str(data.get('data', {}))
        ssn_pattern = re.compile(r'\d{3}-\d{2}-\d{4}')
        
        assert not ssn_pattern.search(data_str), 'SSN pattern found in redacted data'
        
        print_success('No SSN patterns found in response')
        return True
    except Exception as e:
        print_error(f'Failed: {e}')
        return False

def test_redaction_module_import():
    print_test('Redaction module: import and configuration')
    try:
        from redactor import (
            Redactor, RedactorConfig, RedactionTechnique, 
            SophisticationLevel, create_redactor
        )
        
        # Test creating redactor with different configurations
        r1 = create_redactor(technique='mask', sophistication='minimal')
        assert r1.config.technique == RedactionTechnique.MASK
        assert r1.config.sophistication == SophisticationLevel.MINIMAL
        
        r2 = create_redactor(technique='both', sophistication='paranoid')
        assert r2.config.technique == RedactionTechnique.BOTH
        assert r2.config.sophistication == SophisticationLevel.PARANOID
        
        # Test data type configuration for different levels
        from redactor import DataTypeConfig
        minimal_cfg = DataTypeConfig.for_level(SophisticationLevel.MINIMAL)
        paranoid_cfg = DataTypeConfig.for_level(SophisticationLevel.PARANOID)
        
        assert minimal_cfg.nicknames == False, 'Minimal should not include nicknames'
        assert paranoid_cfg.nicknames == True, 'Paranoid should include nicknames'
        assert paranoid_cfg.travel_history == True, 'Paranoid should include travel history'
        
        print_success('Redactor module imports and configures correctly')
        return True
    except Exception as e:
        print_error(f'Failed: {e}')
        return False

def test_redaction_prompt_generation():
    print_test('Redaction module: prompt template generation')
    try:
        from redactor import create_redactor
        
        # Test mask prompt generation
        r = create_redactor(technique='mask', target_individuals=['John Doe', 'Jane Smith'])
        prompt = r._build_mask_prompt('Test document with John Doe', '***', False)
        
        assert 'Test document with John Doe' in prompt, 'Document not in prompt'
        assert '***' in prompt, 'Mask character not in prompt'
        assert 'John Doe' in prompt, 'Target individual not in prompt'
        assert 'Jane Smith' in prompt, 'Target individual not in prompt'
        
        # Test substitution prompt generation
        r2 = create_redactor(technique='substitute', sophistication='comprehensive')
        prompt2 = r2._build_substitution_prompt('Document with sensitive data')
        
        assert 'Document with sensitive data' in prompt2, 'Document not in substitution prompt'
        assert 'Nicknames' in prompt2, 'Comprehensive level should mention nicknames'
        
        print_success('Prompt templates generated correctly')
        return True
    except Exception as e:
        print_error(f'Failed: {e}')
        return False

def test_redaction_two_phase_order():
    print_test('Redaction module: two-phase processing (mask before substitute)')
    try:
        from redactor import create_redactor, RedactionTechnique
        from unittest.mock import patch, MagicMock
        
        r = create_redactor(technique='both')
        assert r.config.technique == RedactionTechnique.BOTH
        
        # Track the order of calls
        call_order = []
        
        def mock_call_llm(prompt, system_msg):
            if 'MASK' in prompt or 'mask' in system_msg.lower():
                call_order.append('mask')
                return 'SSN: ***, Name: John'
            else:
                call_order.append('substitute')
                return 'SSN: ***, Name: Robert'
        
        with patch.object(r, '_call_llm', side_effect=mock_call_llm):
            result = r.redact('SSN: 123-45-6789, Name: John')
        
        assert call_order == ['mask', 'substitute'], f'Expected mask then substitute, got {call_order}'
        assert '***' in result, 'Masked content not preserved'
        
        print_success('Two-phase processing executes in correct order (mask → substitute)')
        return True
    except Exception as e:
        print_error(f'Failed: {e}')
        return False

def main():
    print('=' * 60)
    print('US Federal Data Exchange - Integration Tests')
    print('=' * 60)
    
    results = []
    
    if not test_ping():
        print_error('Server not responding. Make sure api_server.py is running on port 6732')
        sys.exit(1)
    
    token, test_email = test_signup()
    results.append(token is not None)
    
    if token:
        login_token = test_login(test_email, 'TestPassword123!')
        results.append(login_token is not None)
        
        results.append(test_get_data_authenticated(token))
        results.append(test_duplicate_signup(test_email))
    
    results.append(test_get_data_unauthenticated())
    results.append(test_invalid_login())
    
    # Redaction tests
    print('\n' + '-' * 60)
    print('REDACTION SYSTEM TESTS')
    print('-' * 60)
    
    if token:
        results.append(test_redaction_privacy_flag(token))
        results.append(test_redaction_no_ssn_patterns(token))
    
    results.append(test_redaction_module_import())
    results.append(test_redaction_prompt_generation())
    results.append(test_redaction_two_phase_order())
    
    print('\n' + '=' * 60)
    passed = sum(results)
    total = len(results)
    print(f'Results: {passed}/{total} tests passed')
    
    if passed == total:
        print('✓ All tests passed!')
        sys.exit(0)
    else:
        print(f'✗ {total - passed} test(s) failed')
        sys.exit(1)

if __name__ == '__main__':
    main()
