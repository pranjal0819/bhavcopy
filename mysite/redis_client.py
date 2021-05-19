import redis
from django.conf import settings


class RedisClient:

    def connect(self, decode_responses=False):
        return redis.StrictRedis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            username=settings.REDIS_USERNAME,
            password=settings.REDIS_PASSWORD,
            decode_responses=decode_responses
        )
