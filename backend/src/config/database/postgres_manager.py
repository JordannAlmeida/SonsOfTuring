import asyncpg
from typing import Optional, AsyncGenerator
import logging
import os
from contextlib import asynccontextmanager

class PostgresManager:
    """
    Manages the PostgreSQL connection pool using asyncpg.
    """
    _pool: Optional[asyncpg.Pool] = None
    _logger = logging.getLogger(__name__)

    async def connect(self):
        """
        Establishes the PostgreSQL connection pool.
        """
        if self._pool is None:
            db_url = os.getenv("DATABASE_URL")
            host = db_url.split('@')[-1] if db_url else "UNKNOWN"
            self._logger.info(f"Attempting to connect to PostgreSQL at {host}...")
            try:
                self._pool = await asyncpg.create_pool(
                    dsn=db_url,
                    min_size=int(os.getenv("DB_POOL_MIN_SIZE", 10)),
                    max_size=int(os.getenv("DB_POOL_MAX_SIZE", 10)),
                    timeout=float(os.getenv("DB_POOL_TIMEOUT", 30)),
                )
                self._logger.info("PostgreSQL connection pool established successfully.")
            except Exception as e:
                self._logger.exception(f"Failed to connect to PostgreSQL: {e}")
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

    @asynccontextmanager
    async def get_connection(self) -> AsyncGenerator[asyncpg.Connection, None]:
        """
        Provides a connection from the pool.
        Usage:
            async with postgres_manager.get_connection() as conn:
                await conn.fetch(...)
        """
        if self._pool is None:
            raise RuntimeError("PostgreSQL pool is not initialized. Call connect() first.")
        
        async with self._pool.acquire() as connection:
            yield connection

postgres_manager = PostgresManager()

async def get_db_connection() -> AsyncGenerator[asyncpg.Connection, None]:
    """
    FastAPI dependency that yields an asyncpg connection from the pool.
    """
    async with postgres_manager.get_connection() as connection:
        yield connection