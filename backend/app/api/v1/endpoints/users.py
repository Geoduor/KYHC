from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.pagination import Pagination
from app.core.roles import ADMIN_ROLES
from app.core.security import hash_password
from app.database.dependencies import get_db
from app.dependencies.auth import get_current_user, require_roles
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository
from app.schemas.common import Page
from app.schemas.user import UserCreate, UserResponse, UserUpdate

router = APIRouter()


@router.get(
    "/me",
    response_model=UserResponse,
)
def get_profile(
    current_user: User = Depends(get_current_user),
):
    """
    Return the currently authenticated user.
    """

    return current_user


@router.get(
    "/",
    response_model=Page[UserResponse],
)
def get_users(
    db: Session = Depends(get_db),
    pagination: Pagination = Depends(),
    search: str | None = Query(
        None,
        description="Search by name or email",
    ),
    role: UserRole | None = Query(
        None,
        description="Filter by role",
    ),
    is_active: bool | None = Query(
        None,
        description="Filter by active status",
    ),
    current_user: User = Depends(require_roles(*ADMIN_ROLES)),
):
    """
    List users with pagination and filters. Admin only.
    """

    items, total = UserRepository.get_all(
        db,
        skip=pagination.skip,
        limit=pagination.limit,
        search=search,
        role=role,
        is_active=is_active,
    )

    return Page(
        items=items,
        total=total,
        skip=pagination.skip,
        limit=pagination.limit,
    )


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*ADMIN_ROLES)),
):
    """
    Create a staff or player account with any role. Admin only.
    """

    existing_user = UserRepository.get_by_email(
        db,
        user.email,
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
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


@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*ADMIN_ROLES)),
):
    """
    Get a user by ID. Admin only.
    """

    user = UserRepository.get_by_id(
        db,
        user_id,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


@router.put(
    "/{user_id}",
    response_model=UserResponse,
)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*ADMIN_ROLES)),
):
    """
    Update a user. Admin only.
    """

    user = UserRepository.get_by_id(
        db,
        user_id,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    update_data = user_data.model_dump(
        exclude_unset=True,
    )

    password = update_data.pop("password", None)

    if password is not None:
        user.hashed_password = hash_password(password)

    new_email = update_data.get("email")

    if new_email and new_email != user.email:
        existing_user = UserRepository.get_by_email(
            db,
            new_email,
        )

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

    if user.id == current_user.id:
        if update_data.get("is_active") is False:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot deactivate your own account",
            )

        if (
            "role" in update_data
            and update_data["role"] != user.role
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot change your own role",
            )

    for key, value in update_data.items():
        setattr(user, key, value)

    return UserRepository.update(
        db,
        user,
    )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*ADMIN_ROLES)),
):
    """
    Delete a user. Admin only. You cannot delete your own account.
    """

    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete your own account",
        )

    user = UserRepository.get_by_id(
        db,
        user_id,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    UserRepository.delete(
        db,
        user,
    )

    return None
