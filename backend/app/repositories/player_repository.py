from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.player import Player


class PlayerRepository:
    """
    Repository responsible for all database operations
    related to the Player model.
    """

    @staticmethod
    def get_by_id(
        db: Session,
        player_id: int,
    ) -> Player | None:
        return (
            db.query(Player)
            .filter(Player.id == player_id)
            .first()
        )

    @staticmethod
    def get_all(
        db: Session,
        *,
        skip: int = 0,
        limit: int = 50,
        search: str | None = None,
        team_id: int | None = None,
        position: str | None = None,
        is_active: bool | None = None,
    ) -> tuple[list[Player], int]:
        query = db.query(Player)

        if search:
            pattern = f"%{search}%"
            query = query.filter(
                or_(
                    Player.first_name.ilike(pattern),
                    Player.last_name.ilike(pattern),
                )
            )

        if team_id is not None:
            query = query.filter(Player.team_id == team_id)

        if position:
            query = query.filter(Player.position == position)

        if is_active is not None:
            query = query.filter(Player.is_active == is_active)

        total = query.count()

        items = (
            query.order_by(
                Player.last_name,
                Player.first_name,
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

        return items, total

    @staticmethod
    def create(
        db: Session,
        player: Player,
    ) -> Player:
        db.add(player)
        db.commit()
        db.refresh(player)
        return player

    @staticmethod
    def update(
        db: Session,
        player: Player,
    ) -> Player:
        db.commit()
        db.refresh(player)
        return player

    @staticmethod
    def delete(
        db: Session,
        player: Player,
    ) -> None:
        db.delete(player)
        db.commit()
