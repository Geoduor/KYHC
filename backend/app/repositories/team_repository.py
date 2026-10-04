from sqlalchemy.orm import Session

from app.models.team import Team


class TeamRepository:
    """
    Repository responsible for all database operations
    related to Team.
    """

    @staticmethod
    def get_all(
        db: Session,
        *,
        skip: int = 0,
        limit: int = 50,
        search: str | None = None,
        category: str | None = None,
        is_active: bool | None = None,
    ) -> tuple[list[Team], int]:
        query = db.query(Team)

        if search:
            query = query.filter(
                Team.name.ilike(f"%{search}%")
            )

        if category:
            query = query.filter(Team.category == category)

        if is_active is not None:
            query = query.filter(Team.is_active == is_active)

        total = query.count()

        items = (
            query.order_by(Team.name)
            .offset(skip)
            .limit(limit)
            .all()
        )

        return items, total

    @staticmethod
    def get_by_id(
        db: Session,
        team_id: int,
    ) -> Team | None:
        return (
            db.query(Team)
            .filter(Team.id == team_id)
            .first()
        )

    @staticmethod
    def get_by_name(
        db: Session,
        name: str,
    ) -> Team | None:
        return (
            db.query(Team)
            .filter(Team.name == name)
            .first()
        )

    @staticmethod
    def create(
        db: Session,
        team: Team,
    ) -> Team:
        db.add(team)
        db.commit()
        db.refresh(team)
        return team

    @staticmethod
    def update(
        db: Session,
        team: Team,
    ) -> Team:
        db.commit()
        db.refresh(team)
        return team

    @staticmethod
    def delete(
        db: Session,
        team: Team,
    ) -> None:
        db.delete(team)
        db.commit()
