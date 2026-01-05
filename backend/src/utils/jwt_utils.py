import os
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any


class JWTUtils:
    @staticmethod
    def get_secret_key() -> str:
        secret_key = os.getenv("JWT_SECRET_KEY")
        if not secret_key or len(secret_key) < 32:
            raise ValueError("JWT_SECRET_KEY must be at least 32 characters (256 bits)")
        return secret_key

    @staticmethod
    def get_algorithm() -> str:
        algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        if algorithm != "HS256":
            raise ValueError("Only HS256 algorithm is supported")
        return algorithm

    @staticmethod
    def get_expiration_minutes() -> int:
        expiration = os.getenv("JWT_EXPIRATION_MINUTES", "30")
        return int(expiration)

    @staticmethod
    def create_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=JWTUtils.get_expiration_minutes())
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode,
            JWTUtils.get_secret_key(),
            algorithm=JWTUtils.get_algorithm()
        )
        return encoded_jwt

    @staticmethod
    def decode_token(token: str) -> Optional[Dict[str, Any]]:
        try:
            payload = jwt.decode(
                token,
                JWTUtils.get_secret_key(),
                algorithms=[JWTUtils.get_algorithm()]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token expired")
        except jwt.InvalidTokenError:
            raise ValueError("Could not validate credentials")

    @staticmethod
    def extract_user_id(token: str) -> Optional[str]:
        try:
            payload = JWTUtils.decode_token(token)
            user_id = payload.get("sub")
            if not user_id:
                return None
            return user_id
        except ValueError:
            return None
