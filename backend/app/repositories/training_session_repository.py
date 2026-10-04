from sqlalchemy.orm import Session

from app.models.training_session import TrainingSession
from app.schemas.training_session import (
    TrainingSessionCreate,
    TrainingSessionUpdate,
)


class TrainingSessionRepository:

    @staticmethod
    def get_all(
        db: Session,
        *,
        skip: int = 0,
        limit: int = 50,
        coach_id: int | None = None,
        is_completed: bool | None = None,
    ) -> tuple[list[TrainingSession], int]:
        query = db.query(TrainingSession)

        if coach_id is not None:
            query = query.filter(
                TrainingSession.coach_id == coach_id
            )

        if is_completed is not None:
            query = query.filter(
                TrainingSession.is_completed == is_completed
            )

        total = query.count()

        items = (
            query.order_by(TrainingSession.session_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        return items, total

    @staticmethod
    def get_by_id(db: Session, session_id: int):
        return (
            db.query(TrainingSession)
            .filter(TrainingSession.id == session_id)
            .first()
        )

    @staticmethod
    def create(
        db: Session,
        session: TrainingSessionCreate,
    ):
        db_session = TrainingSession(
            **session.model_dump()
        )

        db.add(db_session)
        db.commit()
        db.refresh(db_session)

        return db_session

    @staticmethod
    def update(
        db: Session,
        db_session: TrainingSession,
        session: TrainingSessionUpdate,
    ):
        update_data = session.model_dump(
            exclude_unset=True
        )

        for key, value in update_data.items():
            setattr(
                db_session,
                key,
                value,
            )

        db.commit()
        db.refresh(db_session)

        return db_session

    @staticmethod
    def delete(
        db: Session,
        db_session: TrainingSession,
    ):
        db.delete(db_session)
        db.commit()
