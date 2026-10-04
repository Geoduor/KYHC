from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.match import Match


class MatchRepository:
    """
    Repository responsible for all database operations
    related to the Match model.
    """

    @staticmethod
    def get_all(
        db: Session,
        *,
        skip: int = 0,
        limit: int = 50,
        team_id: int | None = None,
        status: str | None = None,
        competition: str | None = None,
        upcoming_only: bool = False,
    ) -> tuple[list[Match], int]:
        query = db.query(Match)

        if team_id is not None:
            query = query.filter(
                or_(
                    Match.home_team_id == team_id,
                    Match.away_team_id == team_id,
                )
            )

        if status:
            query = query.filter(Match.status == status)

        if competition:
            query = query.filter(
                Match.competition.ilike(f"%{competition}%")
            )

        if upcoming_only:
            query = query.filter(
                Match.status == "Scheduled"
            )

        total = query.count()

        items = (
            query.order_by(Match.match_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        return items, total

    @staticmethod
    def get_by_id(
        db: Session,
        match_id: int,
    ) -> Match | None:
        return (
            db.query(Match)
            .filter(Match.id == match_id)
            .first()
        )

    @staticmethod
    def create(
        db: Session,
        match: Match,
    ) -> Match:
        db.add(match)
        db.commit()
        db.refresh(match)
        return match

    @staticmethod
    def update(
        db: Session,
        match: Match,
    ) -> Match:
        db.commit()
        db.refresh(match)
        return match

    @staticmethod
    def delete(
        db: Session,
        match: Match,
    ) -> None:
        db.delete(match)
        db.commit()
