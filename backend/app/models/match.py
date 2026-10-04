from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database.base import Base


class Match(Base):
    __tablename__ = "matches"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    home_team_id = Column(
        Integer,
        ForeignKey("teams.id"),
        nullable=False,
    )

    away_team_id = Column(
        Integer,
        ForeignKey("teams.id"),
        nullable=False,
    )

    competition = Column(
        String(100),
        nullable=False,
    )

    venue = Column(
        String(150),
        nullable=False,
    )

    match_date = Column(
        DateTime,
        nullable=False,
    )

    status = Column(
        String(30),
        default="Scheduled",
    )

    home_score = Column(
        Integer,
        default=0,
    )

    away_score = Column(
        Integer,
        default=0,
    )

    notes = Column(
        String(255),
        nullable=True,
    )
    home_team = relationship(
        "Team",
        foreign_keys=[home_team_id],
        back_populates="home_matches",
    )

    away_team = relationship(
        "Team",
        foreign_keys=[away_team_id],
        back_populates="away_matches",
    )
    
    events = relationship(
        "MatchEvent",
        back_populates="match",
        cascade="all, delete",
    )

    statistics = relationship(
        "PlayerStatistic",
        back_populates="match",
    )