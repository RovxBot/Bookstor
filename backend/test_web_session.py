"""
Test web session creation for mobile app
"""
import requests
import sys

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_EMAIL = "sam@cooked.beer"
TEST_PASSWORD = "password"  # Replace with your actual password

def test_web_session_flow():
    """Test the complete web session flow for mobile app"""
    print("\n" + "="*60)
    print("TESTING WEB SESSION FLOW")
    print("="*60)
    
    # Step 1: Login with JWT
    print("\n1. Logging in with JWT...")
    login_data = {
        "username": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    if response.status_code != 200:
        print(f"   ❌ Login failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False
    
    token_data = response.json()
    access_token = token_data.get("access_token")
    print(f"   ✅ Login successful")
    print(f"   Token: {access_token[:20]}...")
    
    # Step 2: Create web session
    print("\n2. Creating web session...")
    response = requests.post(
        f"{BASE_URL}/api/auth/create-web-session",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    if response.status_code != 200:
        print(f"   ❌ Web session creation failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False
    
    print(f"   ✅ Web session created")
    print(f"   Response: {response.json()}")
    print(f"   Cookies: {response.cookies}")
    
    # Extract cookies
    session_token = response.cookies.get("session_token")
    user_id = response.cookies.get("user_id")
    
    if not session_token or not user_id:
        print(f"   ❌ Cookies not set properly")
        print(f"   session_token: {session_token}")
        print(f"   user_id: {user_id}")
        return False
    
    print(f"   session_token: {session_token[:20]}...")
    print(f"   user_id: {user_id}")
    
    # Step 3: Access library page with cookies
    print("\n3. Accessing library page with cookies...")
    cookies = {
        "session_token": session_token,
        "user_id": user_id
    }
    
    response = requests.get(
        f"{BASE_URL}/app/library",
        cookies=cookies,
        allow_redirects=False
    )
    
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 303:
        print(f"   ⚠️  Redirected to: {response.headers.get('Location')}")
        print(f"   This means authentication failed")
        return False
    elif response.status_code == 200:
        print(f"   ✅ Library page loaded successfully")
        print(f"   Page length: {len(response.text)} bytes")
        if "Library" in response.text or "library" in response.text:
            print(f"   ✅ Page contains library content")
        return True
    else:
        print(f"   ❌ Unexpected status code: {response.status_code}")
        return False


def test_direct_cookie_access():
    """Test accessing library with manually set cookies"""
    print("\n" + "="*60)
    print("TESTING DIRECT COOKIE ACCESS")
    print("="*60)
    
    # First, get a valid user ID by logging in
    print("\n1. Getting valid user ID...")
    login_data = {
        "username": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    if response.status_code != 200:
        print(f"   ❌ Login failed")
        return False
    
    token_data = response.json()
    access_token = token_data.get("access_token")
    
    # Get user info
    response = requests.get(
        f"{BASE_URL}/api/auth/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    if response.status_code != 200:
        print(f"   ❌ Failed to get user info")
        return False
    
    user_data = response.json()
    user_id = user_data.get("id")
    print(f"   ✅ User ID: {user_id}")
    
    # Try accessing library with just cookies (no validation)
    print("\n2. Accessing library with cookies...")
    cookies = {
        "session_token": "test_token_12345",  # Any token
        "user_id": str(user_id)
    }
    
    response = requests.get(
        f"{BASE_URL}/app/library",
        cookies=cookies,
        allow_redirects=False
    )
    
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        print(f"   ✅ Library page loaded (session validation is not strict)")
        return True
    elif response.status_code == 303:
        print(f"   ⚠️  Redirected to: {response.headers.get('Location')}")
        return False
    else:
        print(f"   ❌ Unexpected status: {response.status_code}")
        return False


if __name__ == "__main__":
    print("\n" + "="*60)
    print("WEB SESSION TEST SUITE")
    print("="*60)
    
    # Test 1: Full flow
    result1 = test_web_session_flow()
    
    # Test 2: Direct cookie access
    result2 = test_direct_cookie_access()
    
    print("\n" + "="*60)
    print("TEST RESULTS")
    print("="*60)
    print(f"Full web session flow: {'✅ PASS' if result1 else '❌ FAIL'}")
    print(f"Direct cookie access: {'✅ PASS' if result2 else '❌ FAIL'}")
    print("="*60 + "\n")
    
    sys.exit(0 if (result1 and result2) else 1)

