from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.user import User, UserRole


class UserRepository:
    """
    Repository responsible for all database operations
    related to the User model.
    """

    @staticmethod
    def get_by_id(
        db: Session,
        user_id: int,
    ) -> User | None:
        return (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

    @staticmethod
    def get_by_email(
        db: Session,
        email: str,
    ) -> User | None:
        return (
            db.query(User)
            .filter(User.email == email)
            .first()
        )

    @staticmethod
    def get_all(
        db: Session,
        *,
        skip: int = 0,
        limit: int = 50,
        search: str | None = None,
        role: UserRole | None = None,
        is_active: bool | None = None,
    ) -> tuple[list[User], int]:
        query = db.query(User)

        if search:
            pattern = f"%{search}%"
            query = query.filter(
                or_(
                    User.full_name.ilike(pattern),
                    User.email.ilike(pattern),
                )
            )

        if role is not None:
            query = query.filter(User.role == role)

        if is_active is not None:
            query = query.filter(User.is_active == is_active)

        total = query.count()

        items = (
            query.order_by(User.full_name)
            .offset(skip)
            .limit(limit)
            .all()
        )

        return items, total

    @staticmethod
    def create(
        db: Session,
        user: User,
    ) -> User:
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def update(
        db: Session,
        user: User,
    ) -> User:
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def delete(
        db: Session,
        user: User,
    ) -> None:
        db.delete(user)
        db.commit()
