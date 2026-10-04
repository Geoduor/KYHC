from sqlalchemy.orm import Session

from app.models.player_statistic import PlayerStatistic
from app.schemas.player_statistic import (
    PlayerStatisticCreate,
    PlayerStatisticUpdate,
)


class PlayerStatisticRepository:

    @staticmethod
    def get_all(
        db: Session,
        *,
        skip: int = 0,
        limit: int = 50,
        player_id: int | None = None,
        match_id: int | None = None,
        mvp_only: bool = False,
    ) -> tuple[list[PlayerStatistic], int]:
        query = db.query(PlayerStatistic)

        if player_id is not None:
            query = query.filter(
                PlayerStatistic.player_id == player_id
            )

        if match_id is not None:
            query = query.filter(
                PlayerStatistic.match_id == match_id
            )

        if mvp_only:
            query = query.filter(PlayerStatistic.mvp.is_(True))

        total = query.count()

        items = (
            query.order_by(
                PlayerStatistic.id.desc(),
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

        return items, total

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
    def get_by_player_and_match(
        db: Session,
        player_id: int,
        match_id: int,
    ):
        return (
            db.query(PlayerStatistic)
            .filter(
                PlayerStatistic.player_id == player_id,
                PlayerStatistic.match_id == match_id,
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
