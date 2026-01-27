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
