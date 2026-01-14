"""
Redis caching service with specialized methods for RAG, sessions, and rate limiting.
"""
import hashlib
import json
from typing import Any, Optional, Dict, List

import redis.asyncio as redis
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class CacheService:
    """Enhanced Redis caching service with specialized methods."""

    # Cache key prefixes
    PREFIX_RAG = "rag:"
    PREFIX_SESSION = "session:"
    PREFIX_USER = "user:"
    PREFIX_RATE = "rate:"
    PREFIX_PLAN = "plan:"

    # Default TTLs (in seconds)
    TTL_RAG = 3600  # 1 hour for RAG responses
    TTL_SESSION = 86400  # 24 hours for sessions
    TTL_PLAN = 7200  # 2 hours for plan data
    TTL_RATE = 60  # 1 minute for rate limiting

    def __init__(self, redis_url: Optional[str] = None):
        """
        Initialize cache service.

        Args:
            redis_url: Redis connection URL
        """
        self.redis_url = redis_url or settings.redis_url
        self.redis_client: Optional[redis.Redis] = None
        self.default_ttl = settings.redis_cache_ttl
        self._connected = False

    async def connect(self) -> None:
        """Connect to Redis."""
        try:
            self.redis_client = redis.from_url(
                self.redis_url, encoding="utf-8", decode_responses=True
            )
            await self.redis_client.ping()
            self._connected = True
            logger.info("Connected to Redis", url=self.redis_url)
        except Exception as e:
            logger.warning("Failed to connect to Redis - caching disabled", error=str(e))
            self._connected = False
            self.redis_client = None

    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        if self.redis_client:
            await self.redis_client.close()
            self._connected = False
            logger.info("Disconnected from Redis")

    def is_available(self) -> bool:
        """Check if Redis is available."""
        return self._connected and self.redis_client is not None

    # ==========================================================================
    # Base Cache Operations
    # ==========================================================================

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.is_available():
            return None

        try:
            value = await self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error("Cache get failed", key=key, error=str(e))
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        if not self.is_available():
            return False

        try:
            ttl = ttl or self.default_ttl
            serialized = json.dumps(value)
            await self.redis_client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            logger.error("Cache set failed", key=key, error=str(e))
            return False

    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        if not self.is_available():
            return False

        try:
            await self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error("Cache delete failed", key=key, error=str(e))
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        if not self.is_available():
            return False

        try:
            return await self.redis_client.exists(key) > 0
        except Exception as e:
            logger.error("Cache exists check failed", key=key, error=str(e))
            return False

    # ==========================================================================
    # RAG Response Caching
    # ==========================================================================

    def _get_rag_cache_key(self, query: str) -> str:
        """Generate cache key for RAG query."""
        # Normalize query: lowercase, strip whitespace
        normalized = query.lower().strip()
        # Hash for consistent key length
        query_hash = hashlib.md5(normalized.encode()).hexdigest()[:16]
        return f"{self.PREFIX_RAG}{query_hash}"

    async def get_rag_response(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Get cached RAG response for a query.
        
        Args:
            query: User query string
            
        Returns:
            Cached response dict with 'response', 'context', 'documents' or None
        """
        key = self._get_rag_cache_key(query)
        cached = await self.get(key)
        if cached:
            logger.info("RAG cache hit", query=query[:50])
        return cached

    async def cache_rag_response(
        self,
        query: str,
        response: str,
        context: Optional[str] = None,
        documents: Optional[List[Dict]] = None,
        ttl: int = None
    ) -> bool:
        """
        Cache a RAG response.
        
        Args:
            query: User query string
            response: LLM response
            context: RAG context used
            documents: Retrieved documents
            ttl: Time to live in seconds (default: 1 hour)
        """
        key = self._get_rag_cache_key(query)
        value = {
            "response": response,
            "context": context,
            "documents": documents or [],
            "cached_at": json.dumps({"$date": "now"})
        }
        result = await self.set(key, value, ttl or self.TTL_RAG)
        if result:
            logger.info("RAG response cached", query=query[:50])
        return result

    async def invalidate_rag_cache(self) -> int:
        """Invalidate all RAG cache entries."""
        return await self.invalidate_pattern(f"{self.PREFIX_RAG}*")

    # ==========================================================================
    # Session Caching
    # ==========================================================================

    async def cache_session(
        self,
        session_token: str,
        session_data: Dict[str, Any],
        ttl: int = None
    ) -> bool:
        """Cache session data for fast auth lookups."""
        key = f"{self.PREFIX_SESSION}{session_token}"
        return await self.set(key, session_data, ttl or self.TTL_SESSION)

    async def get_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Get cached session data."""
        key = f"{self.PREFIX_SESSION}{session_token}"
        return await self.get(key)

    async def invalidate_session(self, session_token: str) -> bool:
        """Invalidate a session cache."""
        key = f"{self.PREFIX_SESSION}{session_token}"
        return await self.delete(key)

    # ==========================================================================
    # User Data Caching
    # ==========================================================================

    async def cache_user(self, user_id: int, user_data: Dict[str, Any], ttl: int = None) -> bool:
        """Cache user data."""
        key = f"{self.PREFIX_USER}{user_id}"
        return await self.set(key, user_data, ttl or self.TTL_SESSION)

    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get cached user data."""
        key = f"{self.PREFIX_USER}{user_id}"
        return await self.get(key)

    async def invalidate_user(self, user_id: int) -> bool:
        """Invalidate user cache."""
        key = f"{self.PREFIX_USER}{user_id}"
        return await self.delete(key)

    # ==========================================================================
    # Rate Limiting
    # ==========================================================================

    async def check_rate_limit(
        self,
        identifier: str,
        max_requests: int = 60,
        window_seconds: int = 60
    ) -> Dict[str, Any]:
        """
        Check and update rate limit for an identifier.
        
        Args:
            identifier: User ID, IP address, or session token
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds
            
        Returns:
            Dict with 'allowed', 'remaining', 'reset_in' keys
        """
        if not self.is_available():
            # Allow all requests if Redis is unavailable
            return {"allowed": True, "remaining": max_requests, "reset_in": 0}

        key = f"{self.PREFIX_RATE}{identifier}"
        
        try:
            # Get current count
            current = await self.redis_client.get(key)
            
            if current is None:
                # First request in window
                await self.redis_client.setex(key, window_seconds, "1")
                return {"allowed": True, "remaining": max_requests - 1, "reset_in": window_seconds}
            
            count = int(current)
            ttl = await self.redis_client.ttl(key)
            
            if count >= max_requests:
                # Rate limit exceeded
                return {"allowed": False, "remaining": 0, "reset_in": ttl}
            
            # Increment counter
            await self.redis_client.incr(key)
            return {"allowed": True, "remaining": max_requests - count - 1, "reset_in": ttl}
            
        except Exception as e:
            logger.error("Rate limit check failed", error=str(e))
            return {"allowed": True, "remaining": max_requests, "reset_in": 0}

    # ==========================================================================
    # Plan Caching
    # ==========================================================================

    async def cache_plans(self, category: str, plans: List[Dict[str, Any]], ttl: int = None) -> bool:
        """Cache plan data by category."""
        key = f"{self.PREFIX_PLAN}{category}"
        return await self.set(key, plans, ttl or self.TTL_PLAN)

    async def get_cached_plans(self, category: str) -> Optional[List[Dict[str, Any]]]:
        """Get cached plans by category."""
        key = f"{self.PREFIX_PLAN}{category}"
        return await self.get(key)

    async def invalidate_plans_cache(self) -> int:
        """Invalidate all plan cache entries."""
        return await self.invalidate_pattern(f"{self.PREFIX_PLAN}*")

    # ==========================================================================
    # Utility Methods
    # ==========================================================================

    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching pattern."""
        if not self.is_available():
            return 0

        try:
            keys = []
            async for key in self.redis_client.scan_iter(match=pattern):
                keys.append(key)

            if keys:
                deleted = await self.redis_client.delete(*keys)
                logger.info("Invalidated cache keys", pattern=pattern, count=deleted)
                return deleted
            return 0
        except Exception as e:
            logger.error("Cache pattern invalidation failed", pattern=pattern, error=str(e))
            return 0

    async def check_health(self) -> bool:
        """Check if Redis is healthy."""
        if not self.is_available():
            return False

        try:
            await self.redis_client.ping()
            return True
        except Exception:
            return False

    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        if not self.is_available():
            return {"available": False}

        try:
            info = await self.redis_client.info("memory")
            return {
                "available": True,
                "used_memory": info.get("used_memory_human", "unknown"),
                "connected_clients": info.get("connected_clients", 0),
            }
        except Exception as e:
            return {"available": False, "error": str(e)}


# Global cache service instance
cache_service = CacheService()
