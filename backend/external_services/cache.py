import json
import os
from typing import Any

from redis.asyncio import Redis


class RedisCache:
    def __init__(
        self,
        redis_url: str | None = None,
        ttl: int = 300,
    ):
        self.redis_url = redis_url or os.getenv(
            "REDIS_URL",
            "redis://redis:6379/0",
        )

        self.ttl = ttl

        self.client = Redis.from_url(
            self.redis_url,
            decode_responses=True,
        )

    async def get(
        self,
        key: str,
    ) -> list[dict[str, Any]] | None:
        value = await self.client.get(key)

        if value is None:
            return None

        return json.loads(value)

    async def set(
        self,
        key: str,
        value: list[dict[str, Any]],
    ) -> None:
        await self.client.setex(
            key,
            self.ttl,
            json.dumps(value),
        )


redis_cache = RedisCache()
# import json
# import os
# from typing import Any

# import redis


# class RedisCache:
#     def __init__(self, redis_url: str | None = None, ttl: int = 300,):
#         self.redis_url = redis_url or os.getenv("REDIS_URL","redis://redis:6379/0",)

#         self.ttl = ttl

#         self.client = redis.Redis.from_url(self.redis_url,decode_responses=True,)

#     def get(self, key: str,) -> list[dict[str, Any]] | None:
#         value = self.client.get(key)

#         if value is None:
#             return None

#         return json.loads(value)

#     def set(self, key: str, value: list[dict[str, Any]],) -> None:
#         self.client.setex(key,self.ttl,json.dumps(value),)


# redis_cache = RedisCache()
