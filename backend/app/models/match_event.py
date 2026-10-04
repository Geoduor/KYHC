from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from app.database.base import Base


class MatchEvent(Base):
    __tablename__ = "match_events"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    minute = Column(
        Integer,
        nullable=False,
    )

    event_type = Column(
        String(50),
        nullable=False,
    )

    description = Column(
        String(255),
        nullable=True,
    )

    match_id = Column(
        Integer,
        ForeignKey("matches.id"),
        nullable=False,
    )

    player_id = Column(
        Integer,
        ForeignKey("players.id"),
        nullable=False,
    )

    assisting_player_id = Column(
        Integer,
        ForeignKey("players.id"),
        nullable=True,
    )

    match = relationship(
        "Match",
        back_populates="events",
    )

    player = relationship(
        "Player",
        foreign_keys=[player_id],
        back_populates="match_events",
    )

    assisting_player = relationship(
        "Player",
        foreign_keys=[assisting_player_id],
        back_populates="assists",
    )