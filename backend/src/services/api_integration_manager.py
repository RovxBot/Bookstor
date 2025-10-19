"""
Dynamic API Integration Manager
Handles book metadata fetching from multiple configured APIs based on priority
"""
import httpx
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from ..models import APIIntegration
from ..schemas import GoogleBookInfo
from .google_books import google_books_service
from .openlibrary import openlibrary_service
from .hardcover import HardcoverService


class APIIntegrationManager:
    """Manages dynamic API integrations for book metadata fetching"""

    def __init__(self):
        self.service_map = {
            'google_books': google_books_service,
            'open_library': openlibrary_service
        }
        self.hardcover_service = None  # Will be initialised with API key from DB
    
    def get_enabled_integrations(self, db: Session) -> List[APIIntegration]:
        """Get all enabled API integrations sorted by priority"""
        return db.query(APIIntegration).filter(
            APIIntegration.is_enabled == True
        ).order_by(APIIntegration.priority).all()
    
    async def search_by_isbn(self, isbn: str, db: Session) -> Optional[GoogleBookInfo]:
        """
        Search for a book by ISBN across all enabled APIs in priority order
        Returns merged results with strict ISBN validation
        """
        integrations = self.get_enabled_integrations(db)

        results = []

        for integration in integrations:
            try:
                result = await self._search_isbn_with_integration(isbn, integration)
                if result:
                    # Validate that the result has an ISBN and it matches what we searched for
                    if result.isbn:
                        # Use ISBN matching that handles ISBN-10 to ISBN-13 conversion
                        if self._isbns_match(isbn, result.isbn):
                            print(f"✓ {integration.display_name}: ISBN match ({result.isbn})")
                            results.append(result)
                        else:
                            print(f"✗ {integration.display_name}: ISBN MISMATCH! Searched: {isbn}, Got: {result.isbn} - REJECTING")
                    else:
                        print(f"⚠ {integration.display_name}: Result has no ISBN - REJECTING to prevent data contamination")
            except Exception as e:
                print(f"Error searching {integration.display_name} for ISBN {isbn}: {e}")
                continue

        # Merge results from all APIs to get the most complete data
        if results:
            return self._merge_book_info(results, search_isbn=isbn)

        return None
    
    async def _search_isbn_with_integration(
        self,
        isbn: str,
        integration: APIIntegration
    ) -> Optional[GoogleBookInfo]:
        """Search a specific integration for ISBN"""
        # Handle Hardcover separately (needs API key)
        if integration.name in ['hardcover', 'hardcover_api']:
            if not self.hardcover_service or self.hardcover_service.api_key != integration.api_key:
                self.hardcover_service = HardcoverService(api_key=integration.api_key)
            return await self.hardcover_service.search_by_isbn(isbn)

        service = self.service_map.get(integration.name)

        if service:
            # Use existing service
            result = await service.search_by_isbn(isbn)
            return result
        else:
            # Generic API call for custom integrations
            return await self._generic_isbn_search(isbn, integration)
    
    async def _generic_isbn_search(
        self, 
        isbn: str, 
        integration: APIIntegration
    ) -> Optional[GoogleBookInfo]:
        """
        Generic ISBN search for custom API integrations
        Assumes the API follows a similar pattern to Google Books/Open Library
        """
        if not integration.base_url:
            return None
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Try common ISBN search patterns
                search_urls = [
                    f"{integration.base_url}/isbn/{isbn}",
                    f"{integration.base_url}/search?isbn={isbn}",
                    f"{integration.base_url}/volumes?q=isbn:{isbn}",
                ]
                
                headers = {}
                if integration.api_key:
                    # Try common API key header patterns
                    headers['Authorization'] = f'Bearer {integration.api_key}'
                    headers['X-API-Key'] = integration.api_key
                
                for url in search_urls:
                    try:
                        response = await client.get(url, headers=headers)
                        if response.status_code == 200:
                            data = response.json()
                            # Try to parse the response
                            return self._parse_generic_response(data)
                    except:
                        continue
                
                return None
        except Exception as e:
            print(f"Error in generic ISBN search for {integration.display_name}: {e}")
            return None
    
    async def search_by_title(
        self, 
        query: str, 
        db: Session, 
        max_results: int = 10
    ) -> List[GoogleBookInfo]:
        """
        Search for books by title across all enabled APIs
        Returns combined results from all APIs
        """
        integrations = self.get_enabled_integrations(db)
        
        all_results = []
        for integration in integrations:
            try:
                results = await self._search_title_with_integration(query, integration, max_results)
                if results:
                    all_results.extend(results)
            except Exception as e:
                print(f"Error searching {integration.display_name} for '{query}': {e}")
                continue
        
        # Remove duplicates based on ISBN or title
        unique_results = self._deduplicate_results(all_results)
        
        return unique_results[:max_results]
    
    async def _search_title_with_integration(
        self,
        query: str,
        integration: APIIntegration,
        max_results: int
    ) -> List[GoogleBookInfo]:
        """Search a specific integration for title"""
        # Handle Hardcover separately (needs API key)
        if integration.name in ['hardcover', 'hardcover_api']:
            if not self.hardcover_service or self.hardcover_service.api_key != integration.api_key:
                self.hardcover_service = HardcoverService(api_key=integration.api_key)
            return await self.hardcover_service.search_by_title(query, max_results)

        service = self.service_map.get(integration.name)

        if service and hasattr(service, 'search_by_title'):
            # Use existing service
            return await service.search_by_title(query, max_results)
        else:
            # Generic API call for custom integrations
            return await self._generic_title_search(query, integration, max_results)
    
    async def _generic_title_search(
        self,
        query: str,
        integration: APIIntegration,
        max_results: int
    ) -> List[GoogleBookInfo]:
        """Generic title search for custom API integrations"""
        if not integration.base_url:
            return []
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Try common search patterns
                search_urls = [
                    f"{integration.base_url}/search?q={query}&limit={max_results}",
                    f"{integration.base_url}/volumes?q={query}&maxResults={max_results}",
                ]
                
                headers = {}
                if integration.api_key:
                    headers['Authorization'] = f'Bearer {integration.api_key}'
                    headers['X-API-Key'] = integration.api_key
                
                for url in search_urls:
                    try:
                        response = await client.get(url, headers=headers)
                        if response.status_code == 200:
                            data = response.json()
                            return self._parse_generic_search_results(data)
                    except:
                        continue
                
                return []
        except Exception as e:
            print(f"Error in generic title search for {integration.display_name}: {e}")
            return []
    
    def _merge_book_info(self, results: List[GoogleBookInfo], search_isbn: Optional[str] = None) -> GoogleBookInfo:
        """
        Merge multiple book info results to create the most complete record
        Priority: first result for each field, but prefer non-None values
        ISBN is the source of truth - only merge data from results with matching ISBNs

        Args:
            results: List of book info results from different APIs
            search_isbn: The ISBN that was searched for (used for validation)
        """
        if not results:
            return None

        if len(results) == 1:
            # Convert to GoogleBookInfo if it's not already
            if not isinstance(results[0], GoogleBookInfo):
                return self._convert_to_google_book_info(results[0])
            return results[0]

        # Convert all results to GoogleBookInfo format
        converted_results = []
        for result in results:
            if isinstance(result, GoogleBookInfo):
                converted_results.append(result)
            else:
                converted_results.append(self._convert_to_google_book_info(result))

        # Use search_isbn as the source of truth if provided, otherwise use first result's ISBN
        source_isbn = search_isbn if search_isbn else converted_results[0].isbn

        if not source_isbn:
            print("ERROR: No ISBN available for merge validation - cannot safely merge results")
            # Return first result only to avoid data contamination
            return converted_results[0]

        # Filter ALL results (including first) to only include those with matching ISBN
        # Use ISBN matching that handles ISBN-10 to ISBN-13 conversion
        matching_results = [
            result for result in converted_results
            if result.isbn and self._isbns_match(source_isbn, result.isbn)
        ]

        if not matching_results:
            print(f"ERROR: No results match the source ISBN {source_isbn}")
            return None

        if len(matching_results) < len(converted_results):
            rejected_count = len(converted_results) - len(matching_results)
            print(f"⚠ Rejected {rejected_count} results with non-matching ISBNs")

        print(f"✓ Merging data from {len(matching_results)} results with matching ISBN: {source_isbn}")

        # Start with the first matching result
        merged = matching_results[0].model_copy()

        # Fill in missing fields from other matching results
        for result in matching_results[1:]:
            for field in merged.model_fields:
                current_value = getattr(merged, field)
                new_value = getattr(result, field, None)

                # If current value is None or empty, use new value
                if current_value is None or (isinstance(current_value, (list, str)) and not current_value):
                    if new_value is not None:
                        setattr(merged, field, new_value)

                # For lists, combine and deduplicate
                elif isinstance(current_value, list) and isinstance(new_value, list):
                    combined = list(set(current_value + new_value))
                    setattr(merged, field, combined)

        return merged

    def _normalize_isbn(self, isbn: str) -> str:
        """
        Normalise ISBN by removing hyphens and spaces for comparison
        """
        if not isbn:
            return ""
        return isbn.replace("-", "").replace(" ", "").strip()

    def _isbn10_to_isbn13(self, isbn10: str) -> str:
        """
        Convert ISBN-10 to ISBN-13
        ISBN-13 = 978 + first 9 digits of ISBN-10 + new check digit
        """
        if not isbn10 or len(isbn10) != 10:
            return isbn10

        # Take first 9 digits and prepend 978
        isbn13_base = "978" + isbn10[:9]

        # Calculate check digit for ISBN-13
        check_sum = 0
        for i, digit in enumerate(isbn13_base):
            if i % 2 == 0:
                check_sum += int(digit)
            else:
                check_sum += int(digit) * 3

        check_digit = (10 - (check_sum % 10)) % 10

        return isbn13_base + str(check_digit)

    def _isbns_match(self, isbn1: str, isbn2: str) -> bool:
        """
        Check if two ISBNs match, accounting for ISBN-10 to ISBN-13 conversion
        """
        if not isbn1 or not isbn2:
            return False

        # Normalise both ISBNs
        norm1 = self._normalize_isbn(isbn1)
        norm2 = self._normalize_isbn(isbn2)

        # Direct match
        if norm1 == norm2:
            return True

        # Check if one is ISBN-10 and the other is ISBN-13
        if len(norm1) == 10 and len(norm2) == 13:
            # Convert ISBN-10 to ISBN-13 and compare
            return self._isbn10_to_isbn13(norm1) == norm2
        elif len(norm1) == 13 and len(norm2) == 10:
            # Convert ISBN-10 to ISBN-13 and compare
            return norm1 == self._isbn10_to_isbn13(norm2)

        return False

    def _convert_to_google_book_info(self, book_info: Any) -> GoogleBookInfo:
        """Convert any book info object to GoogleBookInfo"""
        # Extract common fields
        data = {
            'title': getattr(book_info, 'title', None),
            'subtitle': getattr(book_info, 'subtitle', None),
            'authors': getattr(book_info, 'authors', None),
            'description': getattr(book_info, 'description', None),
            'publisher': getattr(book_info, 'publisher', None),
            'published_date': getattr(book_info, 'published_date', None),
            'page_count': getattr(book_info, 'page_count', None),
            'categories': getattr(book_info, 'categories', None),
            'thumbnail': getattr(book_info, 'thumbnail', None),
            'isbn': getattr(book_info, 'isbn', None),
            'series_name': getattr(book_info, 'series_name', None),
            'series_position': getattr(book_info, 'series_position', None),
            'edition': getattr(book_info, 'edition', None),
            'book_format': getattr(book_info, 'book_format', None),
            'google_books_id': getattr(book_info, 'google_books_id', None),
        }
        return GoogleBookInfo(**data)
    
    def _deduplicate_results(self, results: List[GoogleBookInfo]) -> List[GoogleBookInfo]:
        """Remove duplicate books based on ISBN or title+author"""
        seen_isbns = set()
        seen_titles = set()
        unique_results = []
        
        for result in results:
            # Check ISBN first
            if result.isbn:
                if result.isbn in seen_isbns:
                    continue
                seen_isbns.add(result.isbn)
            
            # Check title+author combination
            title_key = f"{result.title}_{result.authors[0] if result.authors else ''}"
            if title_key in seen_titles:
                continue
            seen_titles.add(title_key)
            
            unique_results.append(result)
        
        return unique_results
    
    def _parse_generic_response(self, data: Dict[str, Any]) -> Optional[GoogleBookInfo]:
        """
        Attempt to parse a generic API response into GoogleBookInfo
        This is a best-effort parser for unknown API formats
        """
        try:
            # Try to extract common fields
            book_data = {}
            
            # Handle nested structures (like Google Books)
            if 'volumeInfo' in data:
                data = data['volumeInfo']
            elif 'items' in data and len(data['items']) > 0:
                data = data['items'][0].get('volumeInfo', data['items'][0])
            
            # Map common field names
            field_mappings = {
                'title': ['title', 'name', 'book_title'],
                'subtitle': ['subtitle', 'subTitle'],
                'authors': ['authors', 'author', 'author_name', 'creators'],
                'description': ['description', 'summary', 'synopsis'],
                'publisher': ['publisher', 'publisherName'],
                'published_date': ['publishedDate', 'published_date', 'publication_date', 'publish_date'],
                'page_count': ['pageCount', 'page_count', 'pages', 'number_of_pages'],
                'categories': ['categories', 'genres', 'subjects'],
                'thumbnail': ['thumbnail', 'cover', 'image', 'cover_url', 'imageLinks'],
                'isbn': ['isbn', 'isbn13', 'isbn_13'],
            }
            
            for field, possible_keys in field_mappings.items():
                for key in possible_keys:
                    if key in data and data[key]:
                        book_data[field] = data[key]
                        break
            
            # Handle imageLinks structure
            if 'imageLinks' in data:
                book_data['thumbnail'] = data['imageLinks'].get('thumbnail') or data['imageLinks'].get('smallThumbnail')
            
            # Ensure we have at least a title
            if 'title' not in book_data:
                return None
            
            return GoogleBookInfo(**book_data)
        except Exception as e:
            print(f"Error parsing generic API response: {e}")
            return None
    
    def _parse_generic_search_results(self, data: Dict[str, Any]) -> List[GoogleBookInfo]:
        """Parse generic search results"""
        results = []
        
        # Try to find the results array
        items = data.get('items', data.get('docs', data.get('results', [])))
        
        for item in items:
            parsed = self._parse_generic_response(item)
            if parsed:
                results.append(parsed)
        
        return results


# Global instance
api_integration_manager = APIIntegrationManager()

