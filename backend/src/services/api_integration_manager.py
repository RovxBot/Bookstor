"""Dynamic API Integration Manager for book metadata aggregation."""

import logging
import re
from typing import Any, Dict, List, Optional, Tuple

import httpx
from sqlalchemy.orm import Session

from ..models import APIIntegration
from ..schemas import GoogleBookInfo
from .google_books import google_books_service
from .openlibrary import openlibrary_service
from .hardcover import HardcoverService
from .cache import cache_get_isbn, cache_set_isbn

logger = logging.getLogger("bookstor.api_integration")


class APIIntegrationManager:
    """Orchestrates enabled integrations to fetch and merge book metadata."""

    def __init__(self) -> None:
        self.service_map = {
            "google_books": google_books_service,
            "open_library": openlibrary_service,
        }
        self.hardcover_service: Optional[HardcoverService] = None

    # ------------------------------------------------------------------
    # Integration registry helpers
    # ------------------------------------------------------------------
    def get_enabled_integrations(self, db: Session) -> List[APIIntegration]:
        return (
            db.query(APIIntegration)
            .filter(APIIntegration.is_enabled == True)  # noqa: E712
            .order_by(APIIntegration.priority)
            .all()
        )

    # ------------------------------------------------------------------
    # Public search methods
    # ------------------------------------------------------------------
    async def search_by_isbn(self, isbn: str, db: Session) -> Optional[GoogleBookInfo]:
        """Concurrent ISBN search across enabled integrations.

        Safer merge semantics:
        - Only merge results whose ISBN matches the searched ISBN (existing behaviour)
        - Use the highest priority integration result as canonical
        - Only accept data from other integrations if title & author similarity threshold passes
        - Never overwrite canonical non-empty critical fields (title, authors, publisher, published_date)
        - Never union authors/categories if similarity check fails (prevents cross‑book mashups)
        """
        import asyncio
        # Try cache first (normalized form)
        norm = self._normalize_isbn(isbn)
        cached = await cache_get_isbn(norm)
        if cached:
            try:
                return GoogleBookInfo(**cached)
            except Exception:  # pragma: no cover
                logger.warning("Cached payload invalid for ISBN %s; ignoring", isbn)
        integrations = self.get_enabled_integrations(db)
        if not integrations:
            return None
        # Launch all searches concurrently
        tasks = [self._search_isbn_with_integration(isbn, i) for i in integrations]
        raw_results = await asyncio.gather(*tasks, return_exceptions=True)
        results: List[Tuple[APIIntegration, GoogleBookInfo]] = []
        for integration, result in zip(integrations, raw_results):
            if isinstance(result, BaseException):  # pragma: no cover
                logger.error("Error querying %s: %s", integration.display_name, result)
                continue
            if result and isinstance(getattr(result, "isbn", None), str):
                if self._isbns_match(isbn, result.isbn or ""):
                    logger.debug("ISBN match %s from %s", result.isbn, integration.display_name)
                    results.append((integration, result))
                else:
                    logger.warning(
                        "ISBN mismatch searched=%s got=%s from %s (discard)",
                        isbn,
                        result.isbn,
                        integration.display_name,
                    )
            elif result:
                logger.info("Discarded result without ISBN from %s", integration.display_name)
        if not results:
            return None
        # Perform safe merge
        merged = self._merge_book_info_safe(results, search_isbn=isbn)
        if merged and merged.isbn:
            try:
                await cache_set_isbn(norm, merged.model_dump(exclude_none=True))
            except Exception:  # pragma: no cover
                logger.debug("Failed to cache ISBN %s", norm)
        return merged

    async def search_by_title(self, query: str, db: Session, max_results: int = 10) -> List[GoogleBookInfo]:
        """Concurrent title search across enabled integrations, deduplicated."""
        import asyncio
        integrations = self.get_enabled_integrations(db)
        if not integrations:
            return []
        tasks = [self._search_title_with_integration(query, i, max_results) for i in integrations]
        raw_batches = await asyncio.gather(*tasks, return_exceptions=True)
        collected: List[GoogleBookInfo] = []
        for integration, batch in zip(integrations, raw_batches):
            if isinstance(batch, BaseException):  # pragma: no cover
                logger.error("Title search error for %s: %s", integration.display_name, batch)
                continue
            if batch:
                collected.extend(list(batch))
        return self._deduplicate_results(collected)[:max_results]

    # ------------------------------------------------------------------
    # Per‑integration dispatch
    # ------------------------------------------------------------------
    async def _search_isbn_with_integration(
        self, isbn: str, integration: APIIntegration
    ) -> Optional[GoogleBookInfo]:
        if integration.name in ["hardcover", "hardcover_api"]:
            if (
                not self.hardcover_service
                or self.hardcover_service.api_key != integration.api_key
            ):
                self.hardcover_service = HardcoverService(api_key=integration.api_key)
            return await self.hardcover_service.search_by_isbn(isbn)
        service = self.service_map.get(integration.name)
        if service:
            return await service.search_by_isbn(isbn)
        return await self._generic_isbn_search(isbn, integration)

    async def _search_title_with_integration(
        self, query: str, integration: APIIntegration, max_results: int
    ) -> List[GoogleBookInfo]:
        if integration.name in ["hardcover", "hardcover_api"]:
            if (
                not self.hardcover_service
                or self.hardcover_service.api_key != integration.api_key
            ):
                self.hardcover_service = HardcoverService(api_key=integration.api_key)
            return await self.hardcover_service.search_by_title(query, max_results)
        service = self.service_map.get(integration.name)
        if service and hasattr(service, "search_by_title"):
            return await service.search_by_title(query, max_results)
        return await self._generic_title_search(query, integration, max_results)

    # ------------------------------------------------------------------
    # Generic (best‑effort) HTTP queries for unknown integrations
    # ------------------------------------------------------------------
    async def _generic_isbn_search(
        self, isbn: str, integration: APIIntegration
    ) -> Optional[GoogleBookInfo]:
        if not integration.base_url:
            return None
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                search_urls = [
                    f"{integration.base_url}/isbn/{isbn}",
                    f"{integration.base_url}/search?isbn={isbn}",
                    f"{integration.base_url}/volumes?q=isbn:{isbn}",
                ]
                headers: Dict[str, str] = {}
                if integration.api_key:
                    headers["Authorization"] = f"Bearer {integration.api_key}"
                    headers["X-API-Key"] = integration.api_key
                for url in search_urls:
                    try:
                        resp = await client.get(url, headers=headers)
                        if resp.status_code == 200:
                            parsed = self._parse_generic_response(resp.json())
                            if parsed:
                                return parsed
                    except Exception:
                        continue
        except Exception as e:  # pragma: no cover
            logger.error(
                "Generic ISBN search error for %s: %s", integration.display_name, e
            )
        return None

    async def _generic_title_search(
        self, query: str, integration: APIIntegration, max_results: int
    ) -> List[GoogleBookInfo]:
        if not integration.base_url:
            return []
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                search_urls = [
                    f"{integration.base_url}/search?q={query}&limit={max_results}",
                    f"{integration.base_url}/volumes?q={query}&maxResults={max_results}",
                ]
                headers: Dict[str, str] = {}
                if integration.api_key:
                    headers["Authorization"] = f"Bearer {integration.api_key}"
                    headers["X-API-Key"] = integration.api_key
                for url in search_urls:
                    try:
                        resp = await client.get(url, headers=headers)
                        if resp.status_code == 200:
                            parsed_list = self._parse_generic_search_results(
                                resp.json()
                            )
                            if parsed_list:
                                return parsed_list
                    except Exception:
                        continue
        except Exception as e:  # pragma: no cover
            logger.error(
                "Generic title search error for %s: %s", integration.display_name, e
            )
        return []

    # ------------------------------------------------------------------
    # Merge & normalisation helpers
    # ------------------------------------------------------------------
    def _merge_book_info_safe(
        self,
        results: List[Tuple[APIIntegration, GoogleBookInfo]],
        search_isbn: Optional[str] = None,
    ) -> Optional[GoogleBookInfo]:
        """Merge with strict consistency rules to avoid cross-book data contamination.

        Args:
            results: list of (integration, book_info) in priority order
            search_isbn: original searched ISBN (raw)
        """
        if not results:
            return None
        # Canonical = first (highest priority) result
        canonical_integration, canonical = results[0]
        source_isbn = search_isbn or canonical.isbn
        if not source_isbn:
            return canonical
        safe_merge = canonical.model_copy(deep=True)
        kept = 0
        skipped = 0
        for integration, book in results[1:]:
            # ISBN already matched earlier; reinforce
            if not (book.isbn and self._isbns_match(source_isbn, book.isbn)):
                skipped += 1
                continue
            if not self._is_consistent_with_canonical(canonical, book):
                logger.warning(
                    "Discarding result from %s due to low similarity (title/authors)",
                    integration.display_name,
                )
                skipped += 1
                continue
            # Merge only non-conflicting, empty fields or extend lists safely
            for field in safe_merge.model_fields:
                if field in {"title", "authors", "publisher", "published_date"}:
                    # Never overwrite canonical critical fields
                    continue
                current = getattr(safe_merge, field)
                new_val = getattr(book, field, None)
                if current in (None, [], "") and new_val not in (None, [], ""):
                    setattr(safe_merge, field, new_val)
                elif (
                    isinstance(current, list)
                    and isinstance(new_val, list)
                    and new_val
                ):
                    # Union lists without duplicates
                    unioned = list(dict.fromkeys(current + new_val))  # preserve order
                    setattr(safe_merge, field, unioned)
            kept += 1
        if safe_merge.series_name:
            safe_merge.series_name = self.normalise_series_name(safe_merge.series_name)
        logger.info(
            "Merged %d supplementary result(s); discarded %d for inconsistency",
            kept,
            skipped,
        )
        return safe_merge

    @staticmethod
    def normalise_series_name(series_name: Optional[str]) -> Optional[str]:  # type: ignore[override]
        if not series_name:
            return None
        normalised = series_name.strip()
        normalised = re.sub(r"^(The|A|An)\s+", "", normalised, flags=re.IGNORECASE)
        normalised = re.sub(r",\s*(Book|Vol\.?|Volume)\s*$", "", normalised, flags=re.IGNORECASE)
        normalised = re.sub(r"\s+(Series|Saga|Trilogy)$", "", normalised, flags=re.IGNORECASE)
        normalised = re.sub(r"\s+", " ", normalised).strip()
        return normalised or None

    # ------------------------------------------------------------------
    # ISBN utilities
    # ------------------------------------------------------------------
    def _normalize_isbn(self, isbn: str) -> str:
        return isbn.replace("-", "").replace(" ", "").strip() if isbn else ""

    def _isbn10_to_isbn13(self, isbn10: str) -> str:
        if not isbn10 or len(isbn10) != 10:
            return isbn10
        base = "978" + isbn10[:9]
        checksum = 0
        for i, d in enumerate(base):
            checksum += int(d) * (1 if i % 2 == 0 else 3)
        check_digit = (10 - (checksum % 10)) % 10
        return base + str(check_digit)

    def _isbns_match(self, isbn1: str, isbn2: str) -> bool:
        n1, n2 = self._normalize_isbn(isbn1), self._normalize_isbn(isbn2)
        if not n1 or not n2:
            return False
        if n1 == n2:
            return True
        if len(n1) == 10 and len(n2) == 13:
            return self._isbn10_to_isbn13(n1) == n2
        if len(n1) == 13 and len(n2) == 10:
            return n1 == self._isbn10_to_isbn13(n2)
        return False

    # ------------------------------------------------------------------
    # Consistency / similarity helpers
    # ------------------------------------------------------------------
    def _normalize_text(self, text: Optional[str]) -> str:
        if not text:
            return ""
        return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()

    def _token_set_similarity(self, a: str, b: str) -> float:
        if not a or not b:
            return 0.0
        sa = set(a.split())
        sb = set(b.split())
        if not sa or not sb:
            return 0.0
        inter = len(sa & sb)
        union = len(sa | sb)
        return inter / union if union else 0.0

    def _authors_similarity(self, a_list: Optional[List[str]], b_list: Optional[List[str]]) -> float:
        if not a_list or not b_list:
            return 0.0
        # Normalize each author name to lower tokens; use intersection / union
        na = {self._normalize_text(a) for a in a_list if a}
        nb = {self._normalize_text(b) for b in b_list if b}
        if not na or not nb:
            return 0.0
        inter = len(na & nb)
        union = len(na | nb)
        return inter / union if union else 0.0

    def _is_consistent_with_canonical(self, canonical: GoogleBookInfo, other: GoogleBookInfo) -> bool:
        title_sim = self._token_set_similarity(
            self._normalize_text(canonical.title), self._normalize_text(other.title)
        )
        if title_sim < 0.6:
            return False
        # If either has authors, require some overlap (>=0.5) when both present
        if canonical.authors and other.authors:
            if self._authors_similarity(canonical.authors, other.authors) < 0.5:
                return False
        return True

    # ------------------------------------------------------------------
    # Generic parsing helpers
    # ------------------------------------------------------------------
    def _parse_generic_response(self, data: Dict[str, Any]) -> Optional[GoogleBookInfo]:
        try:
            if "volumeInfo" in data:
                data = data["volumeInfo"]
            elif "items" in data and data["items"]:
                data = data["items"][0].get("volumeInfo", data["items"][0])
            mappings = {
                "title": ["title", "name"],
                "subtitle": ["subtitle", "subTitle"],
                "authors": ["authors", "author", "author_name"],
                "description": ["description", "summary", "synopsis"],
                "publisher": ["publisher", "publisherName"],
                "published_date": ["publishedDate", "published_date", "publish_date"],
                "page_count": ["pageCount", "page_count", "pages"],
                "categories": ["categories", "genres", "subjects"],
                "thumbnail": ["thumbnail", "cover", "image", "cover_url", "imageLinks"],
                "isbn": ["isbn", "isbn13", "isbn_13"],
            }
            book_data: Dict[str, Any] = {}
            for field, keys in mappings.items():
                for k in keys:
                    if k in data and data[k]:
                        book_data[field] = data[k]
                        break
            if "imageLinks" in data:
                book_data["thumbnail"] = data["imageLinks"].get("thumbnail") or data[
                    "imageLinks"
                ].get("smallThumbnail")
            if "title" not in book_data:
                return None
            return GoogleBookInfo(**book_data)
        except Exception as e:  # pragma: no cover
            logger.error("Generic response parse error: %s", e)
            return None

    def _parse_generic_search_results(self, data: Dict[str, Any]) -> List[GoogleBookInfo]:
        items = data.get("items", data.get("docs", data.get("results", [])))
        out: List[GoogleBookInfo] = []
        for item in items:
            parsed = self._parse_generic_response(item)
            if parsed:
                out.append(parsed)
        return out

    # ------------------------------------------------------------------
    # Deduplication
    # ------------------------------------------------------------------
    def _deduplicate_results(self, results: List[GoogleBookInfo]) -> List[GoogleBookInfo]:
        seen_isbns = set()
        seen_titles = set()
        unique: List[GoogleBookInfo] = []
        for r in results:
            if r.isbn:
                if r.isbn in seen_isbns:
                    continue
                seen_isbns.add(r.isbn)
            title_key = f"{r.title}_{r.authors[0] if r.authors else ''}"
            if title_key in seen_titles:
                continue
            seen_titles.add(title_key)
            unique.append(r)
        return unique


# Global instance used by routes
api_integration_manager = APIIntegrationManager()

