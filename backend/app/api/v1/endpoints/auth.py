from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.database.dependencies import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserResponse

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    user: UserCreate,
    db: Session = Depends(get_db),
):

    existing = UserRepository.get_by_email(
        db,
        user.email,
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Email already registered",
        )

    db_user = User(
        full_name=user.full_name,
        email=user.email,
        hashed_password=hash_password(user.password),
        role=user.role,
    )

    return UserRepository.create(
        db,
        db_user,
    )