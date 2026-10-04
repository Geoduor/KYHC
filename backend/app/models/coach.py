from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from app.database.base import Base


class Coach(Base):
    __tablename__ = "coaches"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    first_name = Column(
        String(100),
        nullable=False,
    )

    last_name = Column(
        String(100),
        nullable=False,
    )

    phone = Column(
        String(20),
        nullable=True,
    )

    email = Column(
        String(100),
        unique=True,
        nullable=False,
    )

    qualification = Column(
        String(150),
        nullable=True,
    )

    experience_years = Column(
        Integer,
        default=0,
    )

    is_active = Column(
        Boolean,
        default=True,
    )

    team_id = Column(
        Integer,
        ForeignKey("teams.id"),
        nullable=False,
    )

    team = relationship(
        "Team",
        back_populates="coaches",
    )

    training_sessions = relationship(
        "TrainingSession",
        back_populates="coach",
    )