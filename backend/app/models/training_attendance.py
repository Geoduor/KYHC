from sqlalchemy import (
    Column,
    Enum,
    ForeignKey,
    Integer,
    Text,
    Time,
)
from sqlalchemy.orm import relationship

from app.database.base import Base
from app.models.attendance_status import AttendanceStatus


class TrainingAttendance(Base):
    __tablename__ = "training_attendance"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    training_session_id = Column(
        Integer,
        ForeignKey("training_sessions.id"),
        nullable=False,
    )

    player_id = Column(
        Integer,
        ForeignKey("players.id"),
        nullable=False,
    )

    status = Column(
        Enum(AttendanceStatus),
        nullable=False,
    )

    arrival_time = Column(
        Time,
        nullable=True,
    )

    notes = Column(
        Text,
        nullable=True,
    )

    training_session = relationship(
        "TrainingSession",
        back_populates="attendance",
    )

    player = relationship(
        "Player",
        back_populates="training_attendance",
    )