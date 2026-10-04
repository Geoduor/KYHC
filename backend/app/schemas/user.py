from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import UserRole


class UserRegister(BaseModel):
    """
    Public self-registration payload.

    Self-registered accounts are always created with the PLAYER role.
    Staff accounts are created by administrators through POST /users/.
    """

    full_name: str = Field(
        min_length=2,
        max_length=150,
    )
    email: EmailStr
    password: str = Field(
        min_length=8,
        max_length=72,
    )

    model_config = ConfigDict(extra="forbid")


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserCreate(BaseModel):
    """
    Admin payload used to create a user with any role.
    """

    full_name: str = Field(
        min_length=2,
        max_length=150,
    )
    email: EmailStr
    password: str = Field(
        min_length=8,
        max_length=72,
    )
    role: UserRole


class UserUpdate(BaseModel):
    full_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
    )
    email: EmailStr | None = None
    password: str | None = Field(
        default=None,
        min_length=8,
        max_length=72,
    )
    role: UserRole | None = None
    is_active: bool | None = None


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: UserRole
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
