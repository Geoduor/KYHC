from sqlalchemy import Boolean, Column, Integer, String

from app.database.base import Base
from sqlalchemy.orm import relationship


class Team(Base):
    """
    Represents a hockey team within the club.
    """

    __tablename__ = "teams"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    name = Column(
        String(100),
        unique=True,
        nullable=False,
    )

    category = Column(
        String(50),
        nullable=False,
    )

    description = Column(
        String(255),
        nullable=True,
    )

    coach_name = Column(
        String(100),
        nullable=True,
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
    )
    
    players = relationship(
    "Player",
    back_populates="team",
    cascade="all, delete",
)
    home_matches = relationship(
    "Match",
    foreign_keys="Match.home_team_id",
    back_populates="home_team",
)

    away_matches = relationship(
    "Match",
    foreign_keys="Match.away_team_id",
    back_populates="away_team",
)
    coaches = relationship(
    "Coach",
    back_populates="team",
    cascade="all, delete",
)