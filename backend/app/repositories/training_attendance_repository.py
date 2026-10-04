from sqlalchemy.orm import Session

from app.models.training_attendance import TrainingAttendance
from app.schemas.training_attendance import (
    TrainingAttendanceCreate,
    TrainingAttendanceUpdate,
)


class TrainingAttendanceRepository:

    @staticmethod
    def get_all(db: Session):
        return db.query(TrainingAttendance).all()

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