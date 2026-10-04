from sqlalchemy.orm import Session

from app.models.training_session import TrainingSession
from app.schemas.training_session import (
    TrainingSessionCreate,
    TrainingSessionUpdate,
)


class TrainingSessionRepository:

    @staticmethod
    def get_all(db: Session):
        return db.query(TrainingSession).all()

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