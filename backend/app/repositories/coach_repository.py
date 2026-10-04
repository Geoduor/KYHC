from sqlalchemy.orm import Session

from app.models.coach import Coach


class CoachRepository:
    """
    Repository responsible for all database operations
    related to the Coach model.
    """

    @staticmethod
    def get_all(db: Session):
        return db.query(Coach).all()

    @staticmethod
    def get_by_id(
        db: Session,
        coach_id: int,
    ):
        return (
            db.query(Coach)
            .filter(Coach.id == coach_id)
            .first()
        )

    @staticmethod
    def create(
        db: Session,
        coach: Coach,
    ):
        db.add(coach)
        db.commit()
        db.refresh(coach)
        return coach

    @staticmethod
    def update(
        db: Session,
        coach: Coach,
    ):
        db.commit()
        db.refresh(coach)
        return coach

    @staticmethod
    def delete(
        db: Session,
        coach: Coach,
    ):
        db.delete(coach)
        db.commit()