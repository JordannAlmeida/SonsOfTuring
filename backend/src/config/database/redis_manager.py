import redis
import os
from redis.backoff import ExponentialBackoff
from redis.retry import Retry

class RedisManager:
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB = int(os.getenv("REDIS_DB", 0))
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

    pool: redis.ConnectionPool\
    
    _instance = None

    def __new__(cls):
        """Singleton pattern to ensure only one instance of RedisManager exists."""
        if cls._instance is None:
            cls._instance = super(RedisManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        retry_strategy = Retry(ExponentialBackoff(cap=10, base=1), 3)
        self.pool = redis.ConnectionPool(
            host=self.REDIS_HOST,
            port=self.REDIS_PORT,
            password=self.REDIS_PASSWORD,
            db=self.REDIS_DB,
            decode_responses=True,
            max_connections=20,
            socket_timeout=5,
            socket_connect_timeout=5,
            retry=retry_strategy,
            retry_on_timeout=True
        )
        self._initialized = True

    def get_redis_client(self):
        """returns a Redis client instance"""
        return redis.Redis(connection_pool=self.pool)
    
redis_manager = RedisManager()