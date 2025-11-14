#!/usr/bin/env python3
"""
Test script to verify the API server works correctly.
Run this on Raspberry Pi before deploying to ESP8266.
"""

import time
import requests
import sys

BASE_URL = 'http://localhost:5000'

def test_endpoint(name, method, endpoint, expected_status=200, data=None):
    """Test a single endpoint"""
    url = BASE_URL + endpoint
    try:
        if method == 'GET':
            response = requests.get(url, timeout=5)
        elif method == 'POST':
            response = requests.post(url, json=data, timeout=5)
        elif method == 'OPTIONS':
            response = requests.options(url, timeout=5)
        
        status = '✅' if response.status_code == expected_status else '❌'
        print(f'{status} {name}: {method} {endpoint} -> {response.status_code}')
        if response.status_code != expected_status:
            print(f'   Expected: {expected_status}, Got: {response.status_code}')
            print(f'   Response: {response.text[:200]}')
        return response.status_code == expected_status
    except requests.exceptions.ConnectionError:
        print(f'❌ {name}: Connection refused - is server running?')
        return False
    except Exception as e:
        print(f'❌ {name}: {e}')
        return False

def main():
    print('🧪 Testing Fish Feeder API Server\n')
    print(f'Base URL: {BASE_URL}\n')
    
    tests_passed = 0
    tests_total = 0
    
    # Test API endpoints
    print('📡 Testing API Endpoints:\n')
    
    tests = [
        ('Ping', 'GET', '/api/ping'),
        ('Home', 'GET', '/api/home'),
        ('Get Quantity', 'GET', '/api/quantity'),
        ('Get Schedule', 'GET', '/api/schedule'),
        ('Get Last Fed', 'GET', '/api/lastfed'),
        ('OPTIONS CORS', 'OPTIONS', '/api/ping'),
    ]
    
    for test in tests:
        tests_total += 1
        if test_endpoint(*test):
            tests_passed += 1
    
    # Test static files
    print('\n📁 Testing Static Files:\n')
    
    static_tests = [
        ('Index Page', 'GET', '/'),
        ('Index HTML', 'GET', '/index.html'),
        ('Feed Now Page', 'GET', '/feednow.html'),
        ('Set Schedule Page', 'GET', '/setschedule.html'),
        ('Set Quantity Page', 'GET', '/setquantity.html'),
        ('CSS File', 'GET', '/css/styles.css'),
        ('Header Image', 'GET', '/assets/images/Header.png'),
    ]
    
    for test in static_tests:
        tests_total += 1
        if test_endpoint(*test):
            tests_passed += 1
    
    # Test POST endpoints (optional - may modify data)
    print('\n📝 Testing POST Endpoints (read-only):\n')
    print('⚠️  Skipping write operations to preserve data')
    
    # Summary
    print('\n' + '='*50)
    print(f'Tests Passed: {tests_passed}/{tests_total}')
    if tests_passed == tests_total:
        print('✅ All tests passed!')
        return 0
    else:
        print(f'❌ {tests_total - tests_passed} test(s) failed')
        return 1

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print('\n\n⚠️  Test interrupted by user')
        sys.exit(1)
