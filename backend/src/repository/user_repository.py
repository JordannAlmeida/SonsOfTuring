from config.database.postgres_manager import postgres_manager
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod


class IUserRepository(ABC):
    @abstractmethod
    async def create_user(self, email: str, name: str, hashed_password: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        pass


class UserRepository(IUserRepository):
    async def create_user(self, email: str, name: str, hashed_password: str) -> Optional[Dict[str, Any]]:
        query = """
            INSERT INTO users (email, name, hashed_password, is_active, created_at)
            VALUES ($1, $2, $3, true, CURRENT_TIMESTAMP)
            RETURNING id, email, name, is_active, created_at
        """
        async with postgres_manager.get_connection() as conn:
            result = await conn.fetchrow(query, email, name, hashed_password)
        return dict(result) if result else None

    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        query = """
            SELECT id, email, name, hashed_password, is_active, created_at
            FROM users
            WHERE email = $1
        """
        async with postgres_manager.get_connection() as conn:
            result = await conn.fetchrow(query, email)
        return dict(result) if result else None

    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        query = """
            SELECT id, email, name, is_active, created_at
            FROM users
            WHERE id = $1
        """
        async with postgres_manager.get_connection() as conn:
            result = await conn.fetchrow(query, user_id)
        return dict(result) if result else None
