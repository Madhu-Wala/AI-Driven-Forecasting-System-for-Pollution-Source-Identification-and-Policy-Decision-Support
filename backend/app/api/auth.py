from fastapi import APIRouter, HTTPException, Depends, status

from app.schemas.auth import (
    SignupRequest,
    LoginRequest,
    AuthResponse,
    UserResponse
)

from app.auth.service import (
    create_policy_maker,
    authenticate_user
)

from app.auth.dependencies import get_current_user

router = APIRouter(tags=["Authentication"])


@router.post(
    "/signup",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED
)
def signup(data: SignupRequest):
    result, error = create_policy_maker(data)

    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )

    return result


@router.post("/login", response_model=AuthResponse)
def login(data: LoginRequest):
    result = authenticate_user(
        data.identifier,
        data.password
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password"
        )

    return result


@router.get("/me", response_model=UserResponse)
def get_me(current_user=Depends(get_current_user)):
    return current_user