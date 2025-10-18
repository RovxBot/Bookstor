"""
Test ISBN API endpoint
"""
import requests

BASE_URL = "http://localhost:8000"
TEST_EMAIL = "sam@cooked.beer"
TEST_PASSWORD = "password"  # Update with your actual password

def test_isbn_endpoint():
    """Test the ISBN endpoint"""
    print("\n" + "="*60)
    print("TESTING ISBN API ENDPOINT")
    print("="*60)
    
    # Step 1: Login
    print("\n1. Logging in...")
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        data={"username": TEST_EMAIL, "password": TEST_PASSWORD},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    if response.status_code != 200:
        print(f"   ❌ Login failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False
    
    token = response.json()["access_token"]
    print(f"   ✅ Login successful")
    
    # Step 2: Test ISBN lookup
    print("\n2. Testing ISBN lookup...")
    isbn = "9780316769174"
    print(f"   ISBN: {isbn}")
    
    response = requests.post(
        f"{BASE_URL}/api/books/isbn/",
        json={
            "isbn": isbn,
            "reading_status": "want_to_read",
            "is_wishlist": False
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 201:
        book = response.json()
        print(f"   ✅ Book added successfully!")
        print(f"   Title: {book['title']}")
        print(f"   Authors: {book['authors']}")
        print(f"   ISBN: {book['isbn']}")
        return True
    elif response.status_code == 400:
        error = response.json()
        if "already exists" in error.get("detail", ""):
            print(f"   ⚠️  Book already in library (this is OK)")
            return True
        else:
            print(f"   ❌ Error: {error}")
            return False
    else:
        print(f"   ❌ Failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False

if __name__ == "__main__":
    result = test_isbn_endpoint()
    print("\n" + "="*60)
    print(f"TEST RESULT: {'✅ PASS' if result else '❌ FAIL'}")
    print("="*60 + "\n")

