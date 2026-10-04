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
    def get_all(
        db: Session,
        *,
        skip: int = 0,
        limit: int = 50,
        match_id: int | None = None,
        player_id: int | None = None,
        event_type: MatchEventType | None = None,
    ) -> tuple[list[MatchEvent], int]:
        query = db.query(MatchEvent)

        if match_id is not None:
            query = query.filter(MatchEvent.match_id == match_id)

        if player_id is not None:
            query = query.filter(
                or_(
                    MatchEvent.player_id == player_id,
                    MatchEvent.assisting_player_id == player_id,
                )
            )

        if event_type is not None:
            query = query.filter(MatchEvent.event_type == event_type)

        total = query.count()

        items = (
            query.order_by(
                MatchEvent.match_id.asc(),
                MatchEvent.minute.asc(),
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

        return items, total

    @staticmethod
    def get_by_id(
        db: Session,
        event_id: int,
    ) -> MatchEvent | None:
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
    ) -> MatchEvent:
        db.add(event)
        db.commit()
        db.refresh(event)
        return event

    @staticmethod
    def update(
        db: Session,
        event: MatchEvent,
    ) -> MatchEvent:
        db.commit()
        db.refresh(event)
        return event

    @staticmethod
    def delete(
        db: Session,
        event: MatchEvent,
    ) -> None:
        db.delete(event)
        db.commit()
