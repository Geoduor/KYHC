from sqlalchemy import (
    Boolean,
    Column,
    Float,
    ForeignKey,
    Integer,
)
from sqlalchemy.orm import relationship

from app.database.base import Base


class PlayerStatistic(Base):
    __tablename__ = "player_statistics"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    player_id = Column(
        Integer,
        ForeignKey("players.id"),
        nullable=False,
    )

    match_id = Column(
        Integer,
        ForeignKey("matches.id"),
        nullable=False,
    )

    goals = Column(
        Integer,
        default=0,
    )

    assists = Column(
        Integer,
        default=0,
    )

    shots = Column(
        Integer,
        default=0,
    )

    shots_on_target = Column(
        Integer,
        default=0,
    )

    passes = Column(
        Integer,
        default=0,
    )

    successful_passes = Column(
        Integer,
        default=0,
    )

    interceptions = Column(
        Integer,
        default=0,
    )

    tackles = Column(
        Integer,
        default=0,
    )

    green_cards = Column(
        Integer,
        default=0,
    )

    yellow_cards = Column(
        Integer,
        default=0,
    )

    red_cards = Column(
        Integer,
        default=0,
    )

    minutes_played = Column(
        Integer,
        default=0,
    )

    rating = Column(
        Float,
        default=0.0,
    )

    mvp = Column(
        Boolean,
        default=False,
    )

    player = relationship(
        "Player",
        back_populates="statistics",
    )

    match = relationship(
        "Match",
        back_populates="statistics",
    )