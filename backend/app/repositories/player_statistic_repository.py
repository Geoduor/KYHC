from sqlalchemy.orm import Session

from app.models.player_statistic import PlayerStatistic
from app.schemas.player_statistic import (
    PlayerStatisticCreate,
    PlayerStatisticUpdate,
)


class PlayerStatisticRepository:

    @staticmethod
    def get_all(db: Session):
        return db.query(PlayerStatistic).all()

    @staticmethod
    def get_by_id(
        db: Session,
        statistic_id: int,
    ):
        return (
            db.query(PlayerStatistic)
            .filter(
                PlayerStatistic.id == statistic_id
            )
            .first()
        )

    @staticmethod
    def create(
        db: Session,
        statistic: PlayerStatisticCreate,
    ):
        db_statistic = PlayerStatistic(
            **statistic.model_dump()
        )

        db.add(db_statistic)
        db.commit()
        db.refresh(db_statistic)

        return db_statistic

    @staticmethod
    def update(
        db: Session,
        db_statistic: PlayerStatistic,
        statistic: PlayerStatisticUpdate,
    ):
        update_data = statistic.model_dump(
            exclude_unset=True
        )

        for key, value in update_data.items():
            setattr(
                db_statistic,
                key,
                value,
            )

        db.commit()
        db.refresh(db_statistic)

        return db_statistic

    @staticmethod
    def delete(
        db: Session,
        db_statistic: PlayerStatistic,
    ):
        db.delete(db_statistic)
        db.commit()