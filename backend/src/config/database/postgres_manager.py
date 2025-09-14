import asyncpg
from asyncpg.pool import Pool
from typing import Optional, AsyncGenerator
import logging
import os
from typing import AsyncGenerator

class PostgresManager:
    """
    Manages the PostgreSQL connection pool using asyncpg.
    """
    _pool: Optional[Pool] = None
    _logger = logging.getLogger(__name__)

    async def connect(self):
        """
        Establishes the PostgreSQL connection pool.
        """
        if self._pool is None:
            self._logger.info(f"Attempting to connect to PostgreSQL at {os.getenv("DATABASE_URL").split('@')[-1]}...")
            try:
                self._pool = await asyncpg.create_pool(
                    dsn=os.getenv("DATABASE_URL"),
                    min_size=os.getenv("DB_POOL_MIN_SIZE"),
                    max_size=os.getenv("DB_POOL_MAX_SIZE"),
                    timeout=os.getenv("DB_POOL_TIMEOUT"),
                )
                self._logger.info("PostgreSQL connection pool established successfully.")
            except Exception as e:
                self._logger.exception(f"Failed to connect to PostgreSQL: {e}") # Use exception for full traceback
                raise

    async def disconnect(self):
        """
        Closes the PostgreSQL connection pool.
        """
        if self._pool:
            self._logger.info("Closing PostgreSQL connection pool...")
            await self._pool.close()
            self._pool = None
            self._logger.info("PostgreSQL connection pool closed.")

    async def get_connection(self) -> AsyncGenerator[asyncpg.Connection, None]:
        """
        Provides a connection from the pool.
        This method is intended to be used as a FastAPI dependency.
        """
        if self._pool is None:
            raise RuntimeError("PostgreSQL pool is not initialized. Call connect() first.")
        async with self._pool.acquire() as connection:
            yield connection

postgres_manager = PostgresManager()

async def get_db_connection() -> AsyncGenerator[asyncpg.Connection, None]:
    """
    FastAPI dependency that yields an asyncpg connection from the pool.
    The connection is automatically released back to the pool when the
    request is finished.
    """
    async for connection in postgres_manager.get_connection():
        yield connection