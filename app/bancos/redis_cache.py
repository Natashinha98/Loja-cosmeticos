import os
import redis

host_redis = os.getenv("REDIS_HOST", "localhost")

cache_redis = redis.Redis(
    host=host_redis,
    port=6379,
    db=0,
    decode_responses=True
)
