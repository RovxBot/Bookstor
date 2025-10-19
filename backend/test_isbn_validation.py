"""
Test ISBN validation to ensure all data collected matches the searched ISBN
"""
import asyncio
import sys
sys.path.insert(0, '/app')

from src.services.api_integration_manager import APIIntegrationManager
from src.database import SessionLocal

async def test_isbn(isbn: str, expected_title: str):
    """Test a single ISBN and validate results"""
    print(f"\n{'='*80}")
    print(f"Testing ISBN: {isbn}")
    print(f"Expected Title: {expected_title}")
    print(f"{'='*80}\n")
    
    db = SessionLocal()
    try:
        manager = APIIntegrationManager()
        result = await manager.search_by_isbn(isbn, db)
        
        if result:
            print(f"\n✓ Result found!")
            print(f"  Title: {result.title}")
            print(f"  Subtitle: {result.subtitle}")
            print(f"  Authors: {result.authors}")
            print(f"  ISBN: {result.isbn}")
            print(f"  Publisher: {result.publisher}")
            print(f"  Published Date: {result.published_date}")
            print(f"  Page Count: {result.page_count}")
            print(f"  Categories: {result.categories}")
            print(f"  Series: {result.series_name} #{result.series_position}" if result.series_name else "  Series: None")
            
            # Validate ISBN matches
            normalized_search = isbn.replace("-", "").replace(" ", "").strip()
            normalized_result = result.isbn.replace("-", "").replace(" ", "").strip() if result.isbn else ""
            
            if normalized_search == normalized_result:
                print(f"\n✅ ISBN VALIDATION PASSED: {isbn} == {result.isbn}")
            else:
                print(f"\n❌ ISBN VALIDATION FAILED: {isbn} != {result.isbn}")
                return False
            
            # Check if title seems reasonable
            if expected_title.lower() in result.title.lower():
                print(f"✅ TITLE VALIDATION PASSED: '{expected_title}' found in '{result.title}'")
            else:
                print(f"⚠️  TITLE WARNING: Expected '{expected_title}' but got '{result.title}'")
                print(f"   (This might be okay if it's an alternate title)")
            
            return True
        else:
            print(f"\n❌ No result found for ISBN {isbn}")
            return False
            
    finally:
        db.close()

async def main():
    """Run tests on 3 different ISBNs"""
    
    test_cases = [
        # Test 1: Fallout Vault Hunter's Guide
        ("9780744016307", "Fallout"),
        
        # Test 2: Dragon Haven by Robin Hobb
        ("9780061561658", "Dragon Haven"),
        
        # Test 3: The Hobbit by J.R.R. Tolkien
        ("9780547928227", "Hobbit"),
    ]
    
    results = []
    for isbn, expected_title in test_cases:
        success = await test_isbn(isbn, expected_title)
        results.append((isbn, expected_title, success))
        await asyncio.sleep(1)  # Brief pause between tests
    
    # Summary
    print(f"\n{'='*80}")
    print("TEST SUMMARY")
    print(f"{'='*80}\n")
    
    passed = sum(1 for _, _, success in results if success)
    total = len(results)
    
    for isbn, title, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {isbn} ({title})")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! ISBN validation is working correctly.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. ISBN validation needs attention.")

if __name__ == "__main__":
    asyncio.run(main())
