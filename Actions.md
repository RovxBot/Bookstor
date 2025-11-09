# Actionable Roadmap Checklist

## Security & Auth

- [ ] Implement refresh token + short-lived access token pattern
- [ ] Add server-side session store (Redis) mapping session_token to user
- [ ] Add rate limiting (e.g., slowapi) for login/register endpoints
- [ ] Integrate CSRF tokens for HTML forms (admin & user portals)
- [ ] Enforce secure/HTTPOnly cookies in production (when behind TLS)

## Data Integrity

- [x] Add unique constraint (user_id, isbn) to books to prevent race duplicates
- [x] Validate ISBN checksum before processing (server-side; mobile pending)
- [ ] Add stricter field constraints (length caps, positive ints) in models/Pydantic schemas

## Performance & Caching

- [x] Use concurrency (asyncio.gather) for integration API calls
- [ ] Cache successful ISBN merges (Redis TTL)
- [ ] Cache per-series missing books computations

## Logging / Monitoring

- [x] Replace print with logging configuration (centralized)
- [ ] Add structured JSON logging output option
- [ ] Add Prometheus metrics (latency, success/failure counts per integration)

## Error Handling

- [ ] Retry/backoff wrapper for external API GET calls
- [ ] Standard error schema with codes for front-end (scanner UX improvements)

## API Integration Enhancements

- [ ] Encrypted storage for api_key (Fernet + master key from env)
- [ ] Extend schema: custom headers, query params, JMESPath mappings
- [ ] "Test Connection" button in admin integrations UI

## Testing

- [ ] Unit tests: ISBN normalization/conversion edge cases (partial done but expand)
- [x] Unit tests: merge logic with conflicting sources
- [ ] Unit tests: series normalization
- [ ] Unit tests: generic API parsing fallbacks
- [ ] Integration tests: registration toggle & session bridging

## Database / Migrations

- [ ] Adopt Alembic for versioned migrations (currently raw SQL)
- [ ] Index (user_id, added_at) and partial index WHERE is_wishlist = true
- [ ] Store reading_status as PostgreSQL ENUM or add check constraint

## Mobile Improvements

- [ ] Offline scan queue (persist ISBNs until online)
- [ ] Local ISBN checksum validation (mod 10 / mod 11)
- [ ] Deep link handling to open specific book detail
- [ ] Native quick actions (update reading status) outside WebView

## UX / UI

- [ ] Pagination or infinite scroll for large libraries
- [ ] Collections: show completion %, bulk add missing to wishlist
- [ ] Cover selection UI (choose preferred cover variant)

## Security Hardening

- [ ] Content Security Policy headers
- [ ] Verify/ensure Jinja autoescape and audit template contexts
- [ ] Dependency scanning (pip-audit) in CI

## Dev Experience

- [ ] Makefile or task runner (test, lint, run)
- [ ] Pre-commit hooks (black, isort, ruff)
- [x] Document environment variables & deployment tips in README
- [ ] OpenAPI security scheme docs & example requests
- [x] Introduce requirements lock workflow (requirements.in / requirements.lock)

## Future Extensions

- [ ] Dedicated user collections/wishlist endpoints
- [ ] Background job queue (Celery/Redis) for bulk metadata refresh
- [ ] Optional GraphQL gateway for flexible querying

## Status Legend

- [x] Completed
- [ ] Pending / Planned
