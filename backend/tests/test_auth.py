import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from src.utils.password_utils import PasswordUtils
from src.utils.jwt_utils import JWTUtils
from src.services.auth_service import AuthService
from src.repository.user_repository import UserRepository
from datetime import datetime, timedelta


class TestPasswordUtils:
    def test_hash_password(self):
        password = "test_password_123"
        hashed = PasswordUtils.hash_password(password)
        assert hashed != password
        assert len(hashed) > 0

    def test_verify_password_correct(self):
        password = "test_password_123"
        hashed = PasswordUtils.hash_password(password)
        assert PasswordUtils.verify_password(password, hashed)

    def test_verify_password_incorrect(self):
        password = "test_password_123"
        wrong_password = "wrong_password"
        hashed = PasswordUtils.hash_password(password)
        assert not PasswordUtils.verify_password(wrong_password, hashed)


class TestJWTUtils:
    @patch.dict('os.environ', {'JWT_SECRET_KEY': 'test_secret_key_at_least_32_characters_long_1234567890'})
    def test_create_token(self):
        data = {"sub": "test_user_id"}
        token = JWTUtils.create_token(data)
        assert token is not None
        assert isinstance(token, str)

    @patch.dict('os.environ', {'JWT_SECRET_KEY': 'test_secret_key_at_least_32_characters_long_1234567890'})
    def test_decode_token_valid(self):
        data = {"sub": "test_user_id"}
        token = JWTUtils.create_token(data)
        decoded = JWTUtils.decode_token(token)
        assert decoded["sub"] == "test_user_id"

    @patch.dict('os.environ', {'JWT_SECRET_KEY': 'test_secret_key_at_least_32_characters_long_1234567890'})
    def test_decode_token_expired(self):
        with patch('src.utils.jwt_utils.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value = datetime.utcnow()
            data = {"sub": "test_user_id"}
            token = JWTUtils.create_token(data, timedelta(seconds=-1))
            
            with pytest.raises(ValueError, match="Token expired"):
                JWTUtils.decode_token(token)

    @patch.dict('os.environ', {'JWT_SECRET_KEY': 'test_secret_key_at_least_32_characters_long_1234567890'})
    def test_extract_user_id_valid(self):
        data = {"sub": "test_user_id"}
        token = JWTUtils.create_token(data)
        user_id = JWTUtils.extract_user_id(token)
        assert user_id == "test_user_id"

    @patch.dict('os.environ', {'JWT_SECRET_KEY': 'test_secret_key_at_least_32_characters_long_1234567890'})
    def test_extract_user_id_invalid(self):
        user_id = JWTUtils.extract_user_id("invalid_token")
        assert user_id is None


class TestAuthService:
    @pytest.fixture
    def mock_repository(self):
        return AsyncMock(spec=UserRepository)

    @pytest.fixture
    def auth_service(self, mock_repository):
        return AuthService(mock_repository)

    @pytest.mark.asyncio
    @patch.dict('os.environ', {'JWT_SECRET_KEY': 'test_secret_key_at_least_32_characters_long_1234567890'})
    async def test_register_success(self, auth_service, mock_repository):
        mock_repository.get_user_by_email.return_value = None
        mock_repository.create_user.return_value = {
            'id': 'test-uuid',
            'email': 'test@example.com',
            'name': 'Test User',
            'is_active': True,
            'created_at': datetime.now()
        }

        result = await auth_service.register('test@example.com', 'Test User', 'password123')
        
        assert result.email == 'test@example.com'
        assert result.name == 'Test User'
        mock_repository.create_user.assert_called_once()

    @pytest.mark.asyncio
    async def test_register_invalid_email(self, auth_service, mock_repository):
        with pytest.raises(ValueError, match="Invalid email format"):
            await auth_service.register('invalid-email', 'Test User', 'password123')

    @pytest.mark.asyncio
    async def test_register_short_password(self, auth_service, mock_repository):
        with pytest.raises(ValueError, match="Password must be at least 8 characters"):
            await auth_service.register('test@example.com', 'Test User', 'short')

    @pytest.mark.asyncio
    async def test_register_email_exists(self, auth_service, mock_repository):
        mock_repository.get_user_by_email.return_value = {
            'id': 'test-uuid',
            'email': 'test@example.com'
        }

        with pytest.raises(ValueError, match="Email already registered"):
            await auth_service.register('test@example.com', 'Test User', 'password123')

    @pytest.mark.asyncio
    @patch.dict('os.environ', {'JWT_SECRET_KEY': 'test_secret_key_at_least_32_characters_long_1234567890'})
    async def test_login_success(self, auth_service, mock_repository):
        hashed_password = PasswordUtils.hash_password('password123')
        mock_repository.get_user_by_email.return_value = {
            'id': 'test-uuid',
            'email': 'test@example.com',
            'name': 'Test User',
            'hashed_password': hashed_password,
            'is_active': True
        }

        result = await auth_service.login('test@example.com', 'password123')
        
        assert result.access_token is not None
        assert result.token_type == "bearer"

    @pytest.mark.asyncio
    async def test_login_user_not_found(self, auth_service, mock_repository):
        mock_repository.get_user_by_email.return_value = None

        with pytest.raises(ValueError, match="Invalid credentials"):
            await auth_service.login('test@example.com', 'password123')

    @pytest.mark.asyncio
    async def test_login_user_inactive(self, auth_service, mock_repository):
        mock_repository.get_user_by_email.return_value = {
            'id': 'test-uuid',
            'email': 'test@example.com',
            'is_active': False
        }

        with pytest.raises(ValueError, match="User account is inactive"):
            await auth_service.login('test@example.com', 'password123')

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, auth_service, mock_repository):
        hashed_password = PasswordUtils.hash_password('password123')
        mock_repository.get_user_by_email.return_value = {
            'id': 'test-uuid',
            'email': 'test@example.com',
            'hashed_password': hashed_password,
            'is_active': True
        }

        with pytest.raises(ValueError, match="Invalid credentials"):
            await auth_service.login('test@example.com', 'wrongpassword')

    @pytest.mark.asyncio
    @patch.dict('os.environ', {'JWT_SECRET_KEY': 'test_secret_key_at_least_32_characters_long_1234567890'})
    async def test_get_current_user_success(self, auth_service, mock_repository):
        user_id = 'test-uuid'
        data = {"sub": user_id}
        token = JWTUtils.create_token(data)
        
        mock_repository.get_user_by_id.return_value = {
            'id': user_id,
            'email': 'test@example.com',
            'name': 'Test User',
            'is_active': True,
            'created_at': datetime.now()
        }

        result = await auth_service.get_current_user(token)
        
        assert result.id == user_id
        assert result.email == 'test@example.com'

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, auth_service, mock_repository):
        with pytest.raises(ValueError, match="Could not validate credentials"):
            await auth_service.get_current_user('invalid_token')

    @pytest.mark.asyncio
    @patch.dict('os.environ', {'JWT_SECRET_KEY': 'test_secret_key_at_least_32_characters_long_1234567890'})
    async def test_get_current_user_not_found(self, auth_service, mock_repository):
        user_id = 'nonexistent-uuid'
        data = {"sub": user_id}
        token = JWTUtils.create_token(data)
        
        mock_repository.get_user_by_id.return_value = None

        with pytest.raises(ValueError, match="User not found"):
            await auth_service.get_current_user(token)
