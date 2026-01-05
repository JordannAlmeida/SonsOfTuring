import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient
from src.main import app
from src.services.auth_service import AuthService
from src.repository.user_repository import UserRepository
from src.utils.password_utils import PasswordUtils
from src.utils.jwt_utils import JWTUtils
from datetime import datetime


@pytest.fixture
def async_client():
    return AsyncClient(app=app, base_url="http://test")


@pytest.mark.asyncio
@patch.dict('os.environ', {'JWT_SECRET_KEY': 'test_secret_key_at_least_32_characters_long_1234567890'})
async def test_register_endpoint_success(async_client):
    with patch('src.controllers.auth_controller.get_auth_service') as mock_get_service:
        mock_service = AsyncMock(spec=AuthService)
        mock_service.register.return_value = type('UserResponse', (), {
            'id': 'test-uuid',
            'email': 'test@example.com',
            'name': 'Test User',
            'is_active': True,
            'created_at': datetime.now(),
            'model_dump': lambda: {
                'id': 'test-uuid',
                'email': 'test@example.com',
                'name': 'Test User',
                'is_active': True,
                'created_at': datetime.now()
            }
        })()
        mock_get_service.return_value = mock_service

        response = await async_client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "name": "Test User",
                "password": "password123"
            }
        )
        
        assert response.status_code in [201, 200]


@pytest.mark.asyncio
async def test_register_endpoint_invalid_email(async_client):
    response = await async_client.post(
        "/auth/register",
        json={
            "email": "invalid-email",
            "name": "Test User",
            "password": "password123"
        }
    )
    
    assert response.status_code in [400, 422]


@pytest.mark.asyncio
@patch.dict('os.environ', {'JWT_SECRET_KEY': 'test_secret_key_at_least_32_characters_long_1234567890'})
async def test_login_endpoint_success(async_client):
    with patch('src.controllers.auth_controller.get_auth_service') as mock_get_service:
        mock_service = AsyncMock(spec=AuthService)
        mock_service.login.return_value = type('TokenResponse', (), {
            'access_token': 'test_token',
            'token_type': 'bearer',
            'model_dump': lambda: {
                'access_token': 'test_token',
                'token_type': 'bearer'
            }
        })()
        mock_get_service.return_value = mock_service

        response = await async_client.post(
            "/auth/login",
            json={
                "email": "test@example.com",
                "password": "password123"
            }
        )
        
        assert response.status_code == 200


@pytest.mark.asyncio
@patch.dict('os.environ', {'JWT_SECRET_KEY': 'test_secret_key_at_least_32_characters_long_1234567890'})
async def test_get_current_user_endpoint_success(async_client):
    user_id = 'test-uuid'
    data = {"sub": user_id}
    token = JWTUtils.create_token(data)

    with patch('src.dependencies.auth_dependency.get_current_user') as mock_get_user:
        mock_get_user.return_value = type('UserResponse', (), {
            'id': user_id,
            'email': 'test@example.com',
            'name': 'Test User',
            'is_active': True,
            'created_at': datetime.now(),
            'model_dump': lambda: {
                'id': user_id,
                'email': 'test@example.com',
                'name': 'Test User',
                'is_active': True,
                'created_at': datetime.now()
            }
        })()

        response = await async_client.get(
            "/auth/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_current_user_endpoint_no_token(async_client):
    response = await async_client.get("/auth/users/me")
    
    assert response.status_code == 401
