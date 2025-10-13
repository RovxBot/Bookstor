#!/usr/bin/env python3
"""
Test script to verify admin panel setup is correct
Run this from the project root: python3 test_admin_startup.py
"""

import sys
from pathlib import Path

def test_file_structure():
    """Test that all required files exist"""
    print("🔍 Checking file structure...")
    
    required_files = [
        "backend/src/routes/admin.py",
        "backend/src/static/admin.css",
        "backend/src/static/admin.js",
        "backend/src/templates/admin/base.html",
        "backend/src/templates/admin/login.html",
        "backend/src/templates/admin/dashboard.html",
        "backend/src/templates/admin/users.html",
        "backend/src/templates/admin/settings.html",
    ]
    
    all_exist = True
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} - MISSING!")
            all_exist = False
    
    return all_exist

def test_imports():
    """Test that required packages are installed"""
    print("\n🔍 Checking Python packages...")
    
    packages = {
        "fastapi": "FastAPI",
        "jinja2": "Jinja2",
        "itsdangerous": "itsdangerous",
        "sqlalchemy": "SQLAlchemy",
    }
    
    all_installed = True
    for package, name in packages.items():
        try:
            __import__(package)
            print(f"  ✅ {name}")
        except ImportError:
            print(f"  ❌ {name} - NOT INSTALLED!")
            all_installed = False
    
    return all_installed

def test_requirements():
    """Check requirements.txt has new dependencies"""
    print("\n🔍 Checking requirements.txt...")
    
    req_file = Path("backend/requirements.txt")
    if not req_file.exists():
        print("  ❌ requirements.txt not found!")
        return False
    
    content = req_file.read_text()
    required = ["jinja2", "itsdangerous"]
    
    all_present = True
    for dep in required:
        if dep in content:
            print(f"  ✅ {dep}")
        else:
            print(f"  ❌ {dep} - MISSING!")
            all_present = False
    
    return all_present

def test_main_py():
    """Check main.py has admin router"""
    print("\n🔍 Checking main.py configuration...")
    
    main_file = Path("backend/src/main.py")
    if not main_file.exists():
        print("  ❌ main.py not found!")
        return False
    
    content = main_file.read_text()
    checks = {
        "admin import": "from .routes import auth, books, admin",
        "StaticFiles import": "from fastapi.staticfiles import StaticFiles",
        "static mount": "app.mount(\"/static\"",
        "admin router": "app.include_router(admin.router)",
    }
    
    all_present = True
    for name, check in checks.items():
        if check in content:
            print(f"  ✅ {name}")
        else:
            print(f"  ❌ {name} - MISSING!")
            all_present = False
    
    return all_present

def main():
    print("=" * 60)
    print("Bookstor Admin Panel Setup Test")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("File Structure", test_file_structure()))
    results.append(("Requirements", test_requirements()))
    results.append(("Main.py Config", test_main_py()))
    
    # Try to test imports (may fail if not in venv)
    try:
        results.append(("Python Packages", test_imports()))
    except Exception as e:
        print(f"\n⚠️  Could not test Python packages: {e}")
        print("   (This is OK if you're not in a virtual environment)")
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ All checks passed! Admin panel should work.")
        print("\nNext steps:")
        print("1. Start Docker: docker-compose up -d --build")
        print("2. Create admin user: curl -X POST http://localhost:8000/api/auth/register \\")
        print("     -H 'Content-Type: application/json' \\")
        print("     -d '{\"email\": \"admin@example.com\", \"password\": \"SecurePass123!\"}'")
        print("3. Access admin panel: http://localhost:8000/admin/login")
    else:
        print("❌ Some checks failed. Please review the errors above.")
        sys.exit(1)
    print("=" * 60)

if __name__ == "__main__":
    main()

