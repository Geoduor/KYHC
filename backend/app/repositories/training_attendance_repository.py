from sqlalchemy.orm import Session

from app.models.training_attendance import TrainingAttendance
from app.schemas.training_attendance import (
    TrainingAttendanceCreate,
    TrainingAttendanceUpdate,
)


class TrainingAttendanceRepository:

    @staticmethod
    def get_all(
        db: Session,
        *,
        skip: int = 0,
        limit: int = 50,
        training_session_id: int | None = None,
        player_id: int | None = None,
        status=None,
    ) -> tuple[list[TrainingAttendance], int]:
        query = db.query(TrainingAttendance)

        if training_session_id is not None:
            query = query.filter(
                TrainingAttendance.training_session_id
                == training_session_id
            )

        if player_id is not None:
            query = query.filter(
                TrainingAttendance.player_id == player_id
            )

        if status is not None:
            query = query.filter(
                TrainingAttendance.status == status
            )

        total = query.count()

        items = (
            query.order_by(
                TrainingAttendance.training_session_id.desc(),
                TrainingAttendance.player_id,
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

        return items, total

    @staticmethod
    def get_by_id(
        db: Session,
        attendance_id: int,
    ):
        return (
            db.query(TrainingAttendance)
            .filter(
                TrainingAttendance.id == attendance_id
            )
            .first()
        )

    @staticmethod
    def create(
        db: Session,
        attendance: TrainingAttendanceCreate,
    ):
        db_attendance = TrainingAttendance(
            **attendance.model_dump()
        )

        db.add(db_attendance)
        db.commit()
        db.refresh(db_attendance)

        return db_attendance

    @staticmethod
    def update(
        db: Session,
        db_attendance: TrainingAttendance,
        attendance: TrainingAttendanceUpdate,
    ):
        update_data = attendance.model_dump(
            exclude_unset=True
        )

        for key, value in update_data.items():
            setattr(
                db_attendance,
                key,
                value,
            )

        db.commit()
        db.refresh(db_attendance)

        return db_attendance

    @staticmethod
    def delete(
        db: Session,
        db_attendance: TrainingAttendance,
    ):
        db.delete(db_attendance)
        db.commit()
