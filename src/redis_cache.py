import pickle
from pydantic import BaseModel
import aioredis
from config import settings
import logging


class RedisCache:
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.redis = None

    async def connect(self):
        self.redis = await aioredis.from_url(self.redis_url)
        logging.info("Redis connected!")

    async def disconnect(self):
        if self.redis:
            await self.redis.close()
            logging.info("Redis disconnected!")

    async def get(self, key: int):
        data = await self.redis.get(key)
        if data:
            logging.info("Redis found key %s", key)
            return pickle.loads(data)
        logging.info("Redis didnt found key %s", key)
        return None
    
    async def set(self, key: int, value: dict):
        await self.redis.set(key, pickle.dumps(value))
        await self.redis.expire(key, 15)
        logging.info("Redis set key %s value %s", key, value)

    async def delete(self, key: int):
        await self.redis.delete(key)
        logging.info("Redis delete key %s", key)


# Функция для зависимостей FastAPI
async def get_redis_helper():
    redis_helper = RedisCache(
        redis_url=f"redis://{settings.redis.host}:{settings.redis.port}/{settings.redis.second_db}"
    )
    await redis_helper.connect()
    try:
        yield redis_helper
    finally:
        await redis_helper.disconnect()