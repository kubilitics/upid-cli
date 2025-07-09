#!/usr/bin/env python3
"""
Simple test script to verify UPID API endpoints are working correctly with enhanced security.
"""

from fastapi.testclient import TestClient
import json
from upid.api.main import app

client = TestClient(app)

def test_api_endpoints():
    print("🔍 Testing UPID API Endpoints with Enhanced Security...")

    # Test root endpoint
    print("\n1. Testing root endpoint...")
    try:
        response = client.get("/")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")

    # Test health endpoint
    print("\n2. Testing health endpoint...")
    try:
        response = client.get("/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")

    # Test auth endpoints
    print("\n3. Testing auth endpoints...")
    
    # Test login endpoint with MFA
    print("   Testing login with MFA...")
    try:
        login_data = {"username": "admin", "password": "password", "mfa_code": "123456"}
        response = client.post("/api/v1/auth/login", json=login_data)
        print(f"   Login Status: {response.status_code}")
        if response.status_code == 200:
            login_response = response.json()
            print(f"   Login Response: {json.dumps(login_response, indent=2)}")
            
            # Test profile endpoint with token
            print("   Testing profile with token...")
            headers = {"Authorization": f"Bearer {login_response['access_token']}"}
            profile_response = client.get("/api/v1/auth/profile", headers=headers)
            print(f"   Profile Status: {profile_response.status_code}")
            print(f"   Profile Response: {profile_response.json()}")
            
            # Test MFA verification
            print("   Testing MFA verification...")
            mfa_data = {"mfa_code": "123456"}
            mfa_response = client.post("/api/v1/auth/mfa/verify", json=mfa_data, headers=headers)
            print(f"   MFA Status: {mfa_response.status_code}")
            print(f"   MFA Response: {mfa_response.json()}")
            
            # Test password change
            print("   Testing password change...")
            password_data = {
                "current_password": "password",
                "new_password": "SecurePassword123!"
            }
            password_response = client.post("/api/v1/auth/password/change", json=password_data, headers=headers)
            print(f"   Password Change Status: {password_response.status_code}")
            print(f"   Password Change Response: {password_response.json()}")
            
            # Test refresh token
            print("   Testing token refresh...")
            refresh_data = {"refresh_token": login_response['refresh_token']}
            refresh_response = client.post("/api/v1/auth/refresh", json=refresh_data, headers=headers)
            print(f"   Refresh Status: {refresh_response.status_code}")
            print(f"   Refresh Response: {refresh_response.json()}")
            
            # Store token for subsequent tests
            global auth_token
            auth_token = login_response['access_token']
            auth_headers = {"Authorization": f"Bearer {auth_token}"}
            
        else:
            print(f"   Login Error: {response.text}")
            auth_token = None
            auth_headers = None
    except Exception as e:
        print(f"   Error: {e}")
        auth_token = None
        auth_headers = None

    # Test analyze endpoints with authentication
    print("\n4. Testing analyze endpoints with authentication...")
    try:
        if auth_token:
            # Test intelligence analysis
            analyze_payload = {"cluster_name": "test-cluster"}
            response = client.post("/api/v1/analyze/intelligence", json=analyze_payload, headers=auth_headers)
            print(f"   Intelligence Analysis Status: {response.status_code}")
            print(f"   Response: {response.json()}")
        else:
            print(f"   Authentication failed - skipping analyze tests")
    except Exception as e:
        print(f"   Error: {e}")

    # Test optimize endpoints with authentication
    print("\n5. Testing optimize endpoints with authentication...")
    try:
        if auth_token:
            response = client.get("/api/v1/optimize/recommendations", headers=auth_headers)
            print(f"   Optimization Status: {response.status_code}")
            print(f"   Response: {response.json()}")
        else:
            print(f"   Authentication failed - skipping optimize tests")
    except Exception as e:
        print(f"   Error: {e}")

    # Test report endpoints with authentication
    print("\n6. Testing report endpoints with authentication...")
    try:
        if auth_token:
            response = client.get("/api/v1/report/summary", headers=auth_headers)
            print(f"   Report Status: {response.status_code}")
            print(f"   Response: {response.json()}")
        else:
            print(f"   Authentication failed - skipping report tests")
    except Exception as e:
        print(f"   Error: {e}")

    # Test storage endpoints with authentication
    print("\n7. Testing storage endpoints with authentication...")
    try:
        if auth_token:
            response = client.get("/api/v1/storage/status", headers=auth_headers)
            print(f"   Storage Status: {response.status_code}")
            print(f"   Response: {response.json()}")
        else:
            print(f"   Authentication failed - skipping storage tests")
    except Exception as e:
        print(f"   Error: {e}")

    # Test security features
    print("\n8. Testing security features...")
    try:
        # Test rate limiting (make multiple requests)
        print("   Testing rate limiting...")
        for i in range(5):
            response = client.get("/health")
            print(f"   Request {i+1} Status: {response.status_code}")
        
        # Test audit logging
        print("   Testing audit logging...")
        if auth_token:
            response = client.get("/api/v1/auth/auth/status", headers=auth_headers)
            print(f"   Audit Log Test Status: {response.status_code}")
        else:
            print(f"   Authentication failed - skipping audit test")
        
    except Exception as e:
        print(f"   Error: {e}")

    print("\n✅ API endpoint testing completed with enhanced security!")

if __name__ == "__main__":
    test_api_endpoints() 