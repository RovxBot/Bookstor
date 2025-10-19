"""
Test Open Library raw API response
"""
import asyncio
import httpx
import json

async def main():
    query = "Ship of Magic Robin Hobb"
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        params = {'q': query, 'limit': 3}
        response = await client.get("https://openlibrary.org/search.json", params=params)
        
        if response.status_code == 200:
            data = response.json()
            docs = data.get('docs', [])
            
            print(f"\nFound {len(docs)} results\n")
            
            for i, doc in enumerate(docs, 1):
                print(f"Result {i}:")
                print(f"  Title: {doc.get('title')}")
                print(f"  Authors: {doc.get('author_name')}")
                print(f"  ISBN field: {doc.get('isbn')}")
                print(f"  ISBN-13: {doc.get('isbn_13')}")
                print(f"  ISBN-10: {doc.get('isbn_10')}")
                print()

if __name__ == "__main__":
    asyncio.run(main())
