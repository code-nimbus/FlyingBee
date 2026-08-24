import json
from typing import Any

from redis.asyncio import Redis


class RedisUserBookingCache:
    """
    Redis cache for user booking pages.

    The caller supplies the complete cache key.

    Example:
        user_bookings:{user_id}:first:20:0
    """

    def __init__(
        self,
        redis: Redis,
        ttl_seconds: int = 3600,
    ):
        self.redis = redis
        self.ttl_seconds = ttl_seconds

    async def get(
        self,
        cache_key: str,
    ) -> dict[str, Any] | None:
        """
        Get cached booking page.
        """

        value = await self.redis.get(cache_key)

        if value is None:
            return None

        if isinstance(value, bytes):
            value = value.decode("utf-8")

        return json.loads(value)

    async def set(
        self,
        cache_key: str,
        value: dict[str, Any],
        ttl_seconds: int | None = None,
    ) -> None:
        """
        Store booking page in Redis.
        """

        await self.redis.set(
            cache_key,
            json.dumps(value),
            ex=(ttl_seconds if ttl_seconds is not None else self.ttl_seconds),
        )

    async def delete(
        self,
        cache_key: str,
    ) -> None:
        """
        Delete a cache entry.
        """

        await self.redis.delete(cache_key)

    async def exists(
        self,
        cache_key: str,
    ) -> bool:
        """
        Check whether a cache entry exists.
        """

        return bool(await self.redis.exists(cache_key))

    async def refresh(
        self,
        cache_key: str,
        ttl_seconds: int | None = None,
    ) -> bool:
        """
        Refresh TTL of an existing cache entry.
        """

        return bool(
            await self.redis.expire(
                cache_key,
                ttl_seconds if ttl_seconds is not None else self.ttl_seconds,
            )
        )


# import json
# from typing import Any

# from redis.asyncio import Redis


# class RedisUserBookingCache:
#     """
#     Redis cache for storing/retrieving a user's booking data.

#     Key format:
#         booking:user:{user_id}

#     Example:
#         booking:user:123
#     """

#     def __init__(
#         self,
#         redis: Redis,
#         ttl_seconds: int = 3600,
#     ):
#         self.redis = redis
#         self.ttl_seconds = ttl_seconds

#     def _key(self, user_id: str | int) -> str:
#         return f"booking:user:{user_id}"

#     async def get(
#         self,
#         # user_id: str | int,
#         cache_key: str,
#     ) -> dict[str, Any] | None:
#         """
#         Get cached booking data for a user.
#         """
#         # key = self._key(user_id)

#         value = await self.redis.get(cache_key)

#         if value is None:
#             return None

#         if isinstance(value, bytes):
#             value = value.decode("utf-8")

#         return json.loads(value)

#     async def set(
#         self,
#         # user_id: str | int,
#         cache_key: str,
#         booking_data: dict[str, Any],
#         ttl_seconds: int | None = None,
#     ) -> None:
#         """
#         Store booking data in Redis.
#         """
#         key = self._key(cache_key)

#         await self.redis.set(
#             key,
#             json.dumps(booking_data),
#             ex=ttl_seconds if ttl_seconds is not None else self.ttl_seconds,
#         )

#     async def delete(
#         self,
#         # user_id: str | int,
#         cache_key: str,
#     ) -> None:
#         """
#         Delete cached booking data for a user.
#         """
#         key = self._key(cache_key)

#         await self.redis.delete(key)

#     async def invalidate_user_bookings(
#         self,
#         # user_id: str | int,
#         cache_key: str,
#     ) -> None:
#         await self.delete(cache_key)

#     async def exists(
#         self,
#         # user_id: str | int,
#         cache_key: str,
#     ) -> bool:
#         """
#         Check whether booking data exists in Redis.
#         """
#         key = self._key(cache_key)

#         return bool(await self.redis.exists(key))

#     async def refresh(
#         self,
#         # user_id: str | int,
#         cache_key: str,
#         ttl_seconds: int | None = None,
#     ) -> bool:
#         """
#         Refresh the TTL of an existing cache entry.
#         """
#         key = self._key(cache_key)

#         return bool(
#             await self.redis.expire(
#                 key,
#                 ttl_seconds or self.ttl_seconds,
#             )
#         )
