from fastapi import APIRouter, Depends, HTTPException, status
from models.ui.auth.auth_schemas import RegisterRequest, LoginRequest, TokenResponse, UserResponse
from services.auth_service import IAuthService, AuthService
from repository.user_repository import IUserRepository, UserRepository
from dependencies.auth_dependency import oauth2_scheme, get_current_user

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={401: {"description": "Unauthorized"}, 400: {"description": "Bad Request"}},
)


async def get_auth_service() -> IAuthService:
    repository: IUserRepository = UserRepository()
    return AuthService(repository)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    service: IAuthService = Depends(get_auth_service)
):
    try:
        return await service.register(request.email, request.name, request.password)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    service: IAuthService = Depends(get_auth_service)
):
    try:
        return await service.login(request.email, request.password)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get("/users/me", response_model=UserResponse)
async def get_current_user_endpoint(
    current_user: UserResponse = Depends(get_current_user)
):
    return current_user
