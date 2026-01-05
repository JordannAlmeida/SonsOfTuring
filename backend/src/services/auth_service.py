from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from repository.user_repository import IUserRepository
from utils.jwt_utils import JWTUtils
from utils.password_utils import PasswordUtils
from models.ui.auth.auth_schemas import TokenResponse, UserResponse
import re


class IAuthService(ABC):
    @abstractmethod
    async def register(self, email: str, name: str, password: str) -> UserResponse:
        pass

    @abstractmethod
    async def login(self, email: str, password: str) -> TokenResponse:
        pass

    @abstractmethod
    async def get_current_user(self, token: str) -> UserResponse:
        pass


class AuthService(IAuthService):
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository

    @staticmethod
    def _validate_email(email: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    @staticmethod
    def _validate_password(password: str) -> bool:
        return len(password) >= 8

    async def register(self, email: str, name: str, password: str) -> UserResponse:
        if not self._validate_email(email):
            raise ValueError("Invalid email format")
        
        if not self._validate_password(password):
            raise ValueError("Password must be at least 8 characters")

        existing_user = await self.user_repository.get_user_by_email(email)
        if existing_user:
            raise ValueError("Email already registered")

        hashed_password = PasswordUtils.hash_password(password)
        user_data = await self.user_repository.create_user(email, name, hashed_password)
        
        if not user_data:
            raise RuntimeError("Failed to create user")

        return UserResponse(
            id=user_data['id'],
            email=user_data['email'],
            name=user_data['name'],
            is_active=user_data['is_active'],
            created_at=user_data['created_at']
        )

    async def login(self, email: str, password: str) -> TokenResponse:
        user_data = await self.user_repository.get_user_by_email(email)
        
        if not user_data:
            raise ValueError("Invalid credentials")

        if not user_data.get('is_active'):
            raise ValueError("User account is inactive")

        if not PasswordUtils.verify_password(password, user_data['hashed_password']):
            raise ValueError("Invalid credentials")

        token = JWTUtils.create_token(data={
            "sub": str(user_data['id']),
            "email": user_data['email'],
            "name": user_data['name']
        })
        return TokenResponse(access_token=token, token_type="bearer")

    async def get_current_user(self, token: str) -> UserResponse:
        try:
            payload = JWTUtils.decode_token(token)
            user_id = payload.get("sub")
            
            if not user_id:
                raise ValueError("Could not validate credentials")

            user_data = await self.user_repository.get_user_by_id(user_id)
            
            if not user_data:
                raise ValueError("User not found")

            return UserResponse(
                id=user_data['id'],
                email=user_data['email'],
                name=user_data['name'],
                is_active=user_data['is_active'],
                created_at=user_data['created_at']
            )
        except ValueError as e:
            if "Token expired" in str(e):
                raise ValueError("Token expired")
            raise
