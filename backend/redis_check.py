"""Simple script to verify Redis caching connectivity inside container."""
from src.services.cache import get_client, isbn_cache_key
import asyncio


async def main():
    client = get_client()
    if not client:
        print("Redis client: NOT INITIALISED (library missing or REDIS_URL unset)")
        return
    try:
        pong = await client.ping()
        print("Redis PING:", pong)
        key = isbn_cache_key("9780547928227")
        val = await client.get(key)
        print(f"Sample key '{key}' present?", bool(val))
    except Exception as e:  # pragma: no cover
        print("Redis operation failed:", e)
    finally:
        try:
            await client.aclose()
        except Exception as e:
            print("Error during Redis client cleanup:", e)


if __name__ == "__main__":
    asyncio.run(main())