from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from utils.jwt_utils import JWTUtils
from services.auth_service import AuthService, IAuthService
from repository.user_repository import UserRepository, IUserRepository
from models.ui.auth.auth_schemas import UserResponse

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login",
    scopes={},
    auto_error=False
)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    service: IAuthService = Depends(lambda: AuthService(UserRepository()))
) -> UserResponse:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        return await service.get_current_user(token)
    except ValueError as e:
        error_message = str(e)
        if "Token expired" in error_message:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
