from pydantic import BaseModel, EmailStr

from app.models.user import UserRole


class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: UserRole


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: UserRole
    is_active: bool

    model_config = {
        "from_attributes": True
    }