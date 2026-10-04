from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.coach import Coach


class CoachRepository:
    """
    Repository responsible for all database operations
    related to the Coach model.
    """

    @staticmethod
    def get_all(
        db: Session,
        *,
        skip: int = 0,
        limit: int = 50,
        search: str | None = None,
        team_id: int | None = None,
        is_active: bool | None = None,
    ) -> tuple[list[Coach], int]:
        query = db.query(Coach)

        if search:
            pattern = f"%{search}%"
            query = query.filter(
                or_(
                    Coach.first_name.ilike(pattern),
                    Coach.last_name.ilike(pattern),
                    Coach.email.ilike(pattern),
                )
            )

        if team_id is not None:
            query = query.filter(Coach.team_id == team_id)

        if is_active is not None:
            query = query.filter(Coach.is_active == is_active)

        total = query.count()

        items = (
            query.order_by(
                Coach.last_name,
                Coach.first_name,
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

        return items, total

    @staticmethod
    def get_by_id(
        db: Session,
        coach_id: int,
    ) -> Coach | None:
        return (
            db.query(Coach)
            .filter(Coach.id == coach_id)
            .first()
        )

    @staticmethod
    def get_by_email(
        db: Session,
        email: str,
    ) -> Coach | None:
        return (
            db.query(Coach)
            .filter(Coach.email == email)
            .first()
        )

    @staticmethod
    def create(
        db: Session,
        coach: Coach,
    ) -> Coach:
        db.add(coach)
        db.commit()
        db.refresh(coach)
        return coach

    @staticmethod
    def update(
        db: Session,
        coach: Coach,
    ) -> Coach:
        db.commit()
        db.refresh(coach)
        return coach

    @staticmethod
    def delete(
        db: Session,
        coach: Coach,
    ) -> None:
        db.delete(coach)
        db.commit()
