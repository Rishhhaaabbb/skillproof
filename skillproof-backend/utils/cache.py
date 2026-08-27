# Task 1: Thread-safe in-process TTL cache
import threading
import time
from typing import Any, Optional


class TTLCache:
    """Thread-safe in-memory cache with per-entry time-to-live expiration.

    All public methods acquire a single reentrant lock so they are safe to call
    from multiple threads concurrently.

    Usage::

        cache = TTLCache(default_ttl=900)
        cache.set("key", value, ttl=60)
        value = cache.get("key")          # None if expired or missing
        cache.invalidate("key")
        cache.clear()
    """

    def __init__(self, default_ttl: int = 900) -> None:
        """
        Args:
            default_ttl: Seconds before an entry expires when no explicit TTL
                         is passed to :meth:`set`.  Defaults to 900 (15 min).
        """
        self._store: dict[str, tuple[Any, float]] = {}  # key -> (value, expires_at)
        self._lock = threading.RLock()
        self._default_ttl = default_ttl

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get(self, key: str) -> Optional[Any]:
        """Return the cached value for *key*, or ``None`` if absent/expired.

        Expired entries are evicted lazily on access.
        """
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            value, expires_at = entry
            if time.monotonic() > expires_at:
                del self._store[key]
                return None
            return value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Store *value* under *key* with an optional TTL override.

        Args:
            key:   Cache key.
            value: Any picklable Python object.
            ttl:   Seconds until expiry.  Uses ``default_ttl`` when omitted.
        """
        ttl = ttl if ttl is not None else self._default_ttl
        expires_at = time.monotonic() + ttl
        with self._lock:
            self._store[key] = (value, expires_at)

    def invalidate(self, key: str) -> None:
        """Remove a single entry from the cache (no-op if not present)."""
        with self._lock:
            self._store.pop(key, None)

    def clear(self) -> None:
        """Remove all entries from the cache."""
        with self._lock:
            self._store.clear()

    def __len__(self) -> int:
        """Return the number of stored entries (including not-yet-evicted expired ones)."""
        with self._lock:
            return len(self._store)


# Module-level singleton used by services
cache = TTLCache()
