from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.database.dependencies import get_db
from app.models.user import User
from app.repositories.training_attendance_repository import (
    TrainingAttendanceRepository,
)
from app.schemas.training_attendance import (
    TrainingAttendanceCreate,
    TrainingAttendanceResponse,
    TrainingAttendanceUpdate,
)

router = APIRouter()


@router.get(
    "/",
    response_model=list[TrainingAttendanceResponse],
)
def get_attendance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return TrainingAttendanceRepository.get_all(db)


@router.post(
    "/",
    response_model=TrainingAttendanceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_attendance(
    attendance: TrainingAttendanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return TrainingAttendanceRepository.create(
        db,
        attendance,
    )


@router.get(
    "/{attendance_id}",
    response_model=TrainingAttendanceResponse,
)
def get_attendance_by_id(
    attendance_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    attendance = TrainingAttendanceRepository.get_by_id(
        db,
        attendance_id,
    )

    if not attendance:
        raise HTTPException(
            status_code=404,
            detail="Attendance not found",
        )

    return attendance


@router.put(
    "/{attendance_id}",
    response_model=TrainingAttendanceResponse,
)
def update_attendance(
    attendance_id: int,
    attendance: TrainingAttendanceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_attendance = TrainingAttendanceRepository.get_by_id(
        db,
        attendance_id,
    )

    if not db_attendance:
        raise HTTPException(
            status_code=404,
            detail="Attendance not found",
        )

    return TrainingAttendanceRepository.update(
        db,
        db_attendance,
        attendance,
    )


@router.delete(
    "/{attendance_id}",
)
def delete_attendance(
    attendance_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_attendance = TrainingAttendanceRepository.get_by_id(
        db,
        attendance_id,
    )

    if not db_attendance:
        raise HTTPException(
            status_code=404,
            detail="Attendance not found",
        )

    TrainingAttendanceRepository.delete(
        db,
        db_attendance,
    )

    return {
        "message": "Attendance deleted successfully"
    }