from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.match_event import MatchEvent
from app.models.enums import MatchEventType


class MatchEventRepository:
    """
    Repository responsible for all database operations
    related to MatchEvent.
    """

    @staticmethod
    def get_all(db: Session):
        return (
            db.query(MatchEvent)
            .order_by(
                MatchEvent.match_id.asc(),
                MatchEvent.minute.asc(),
            )
            .all()
        )

    @staticmethod
    def get_by_id(
        db: Session,
        event_id: int,
    ):
        return (
            db.query(MatchEvent)
            .filter(MatchEvent.id == event_id)
            .first()
        )

    @staticmethod
    def get_by_match(
        db: Session,
        match_id: int,
    ):
        return (
            db.query(MatchEvent)
            .filter(MatchEvent.match_id == match_id)
            .order_by(MatchEvent.minute.asc())
            .all()
        )

    @staticmethod
    def get_by_player(
        db: Session,
        player_id: int,
    ):
        return (
            db.query(MatchEvent)
            .filter(MatchEvent.player_id == player_id)
            .order_by(MatchEvent.minute.asc())
            .all()
        )

    @staticmethod
    def get_by_event_type(
        db: Session,
        event_type: MatchEventType,
    ):
        return (
            db.query(MatchEvent)
            .filter(MatchEvent.event_type == event_type)
            .all()
        )

    @staticmethod
    def get_goals_by_player(
        db: Session,
        player_id: int,
    ):
        return (
            db.query(MatchEvent)
            .filter(
                MatchEvent.player_id == player_id,
                MatchEvent.event_type == MatchEventType.GOAL,
            )
            .all()
        )

    @staticmethod
    def get_assists_by_player(
        db: Session,
        player_id: int,
    ):
        """
        Return events that count as an assist for the player.

        An assist is counted when the player is linked through
        ``assisting_player_id`` on any event, or when an explicit
        ASSIST event was recorded with the player as the actor.
        """

        return (
            db.query(MatchEvent)
            .filter(
                or_(
                    MatchEvent.assisting_player_id == player_id,
                    (
                        (MatchEvent.player_id == player_id)
                        & (MatchEvent.event_type == MatchEventType.ASSIST)
                    ),
                )
            )
            .all()
        )

    @staticmethod
    def create(
        db: Session,
        event: MatchEvent,
    ):
        db.add(event)
        db.commit()
        db.refresh(event)
        return event

    @staticmethod
    def update(
        db: Session,
        event: MatchEvent,
    ):
        db.commit()
        db.refresh(event)
        return event

    @staticmethod
    def delete(
        db: Session,
        event: MatchEvent,
    ):
        db.delete(event)
        db.commit()