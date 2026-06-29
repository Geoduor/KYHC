from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, Enum as SqlEnum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base

from sqlalchemy import func


class UserRole(str, Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    CLUB_ADMIN = "CLUB_ADMIN"
    COACH = "COACH"
    ASSISTANT_COACH = "ASSISTANT_COACH"
    TEAM_MANAGER = "TEAM_MANAGER"
    MEDIC = "MEDIC"
    FINANCE = "FINANCE"
    PLAYER = "PLAYER"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    full_name: Mapped[str] = mapped_column(String(150), nullable=False)

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)

    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    role: Mapped[UserRole] = mapped_column(SqlEnum(UserRole), nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    from sqlalchemy.sql import func

created_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    server_default=func.now(),
    nullable=False
)

updated_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    server_default=func.now(),
    onupdate=func.now(),
    nullable=False,
)