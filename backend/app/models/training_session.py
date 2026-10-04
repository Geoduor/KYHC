from datetime import UTC, datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database.base import Base


def utc_now() -> datetime:
    """
    Return the current UTC time as a naive datetime.

    The database columns use DateTime without timezone information,
    so values are stored as naive UTC timestamps.
    """

    return datetime.now(UTC).replace(tzinfo=None)


class TrainingSession(Base):
    __tablename__ = "training_sessions"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    title = Column(
        String(100),
        nullable=False,
    )

    description = Column(
        Text,
        nullable=True,
    )

    venue = Column(
        String(150),
        nullable=False,
    )

    session_date = Column(
        DateTime,
        nullable=False,
    )

    duration_minutes = Column(
        Integer,
        nullable=False,
    )

    focus_area = Column(
        String(100),
        nullable=False,
    )

    coach_id = Column(
        Integer,
        ForeignKey("coaches.id"),
        nullable=False,
    )

    is_completed = Column(
        Boolean,
        default=False,
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=utc_now,
    )

    coach = relationship(
        "Coach",
        back_populates="training_sessions",
    )

    attendance = relationship(
        "TrainingAttendance",
        back_populates="training_session",
        cascade="all, delete",
    )