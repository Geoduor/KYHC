from sqlalchemy.orm import Session

from app.models.match import Match


class MatchRepository:
    """
    Repository responsible for all database operations
    related to the Match model.
    """

    @staticmethod
    def get_all(db: Session):
        return db.query(Match).all()

    @staticmethod
    def get_by_id(
        db: Session,
        match_id: int,
    ):
        return (
            db.query(Match)
            .filter(Match.id == match_id)
            .first()
        )

    @staticmethod
    def create(
        db: Session,
        match: Match,
    ):
        db.add(match)
        db.commit()
        db.refresh(match)
        return match

    @staticmethod
    def update(
        db: Session,
        match: Match,
    ):
        db.commit()
        db.refresh(match)
        return match

    @staticmethod
    def delete(
        db: Session,
        match: Match,
    ):
        db.delete(match)
        db.commit()