from sqlalchemy import (
    Boolean,
    Column,
    Date,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.database.base import Base


class Player(Base):
    __tablename__ = "players"

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

    date_of_birth = Column(
        Date,
        nullable=False,
    )

    gender = Column(
        String(20),
        nullable=False,
    )

    position = Column(
        String(50),
        nullable=False,
    )

    jersey_number = Column(
        Integer,
        nullable=False,
    )

    phone = Column(
        String(20),
        nullable=True,
    )

    email = Column(
        String(100),
        nullable=True,
    )

    emergency_contact = Column(
        String(100),
        nullable=True,
    )

    medical_notes = Column(
        Text,
        nullable=True,
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
    )

    team_id = Column(
        Integer,
        ForeignKey("teams.id"),
        nullable=False,
    )

    team = relationship(
        "Team",
        back_populates="players",
    )

    match_events = relationship(
        "MatchEvent",
        foreign_keys="MatchEvent.player_id",
        back_populates="player",
    )

    assists = relationship(
        "MatchEvent",
        foreign_keys="MatchEvent.assisting_player_id",
        back_populates="assisting_player",
    )

    training_attendance = relationship(
        "TrainingAttendance",
        back_populates="player",
    )

    statistics = relationship(
        "PlayerStatistic",
        back_populates="player",
    )