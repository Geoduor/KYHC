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
    ) -> list[Player]:
        return db.query(Player).all()

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