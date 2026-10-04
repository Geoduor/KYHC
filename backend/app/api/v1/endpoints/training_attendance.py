from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.pagination import Pagination
from app.core.roles import COACHING_ROLES
from app.database.dependencies import get_db
from app.dependencies.auth import get_current_user, require_roles
from app.models.attendance_status import AttendanceStatus
from app.models.player import Player
from app.models.training_attendance import TrainingAttendance
from app.models.user import User
from app.repositories.training_attendance_repository import (
    TrainingAttendanceRepository,
)
from app.repositories.training_session_repository import (
    TrainingSessionRepository,
)
from app.schemas.common import Page
from app.schemas.training_attendance import (
    TrainingAttendanceCreate,
    TrainingAttendanceResponse,
    TrainingAttendanceUpdate,
)

router = APIRouter()


@router.get(
    "/",
    response_model=Page[TrainingAttendanceResponse],
)
def get_attendance(
    db: Session = Depends(get_db),
    pagination: Pagination = Depends(),
    training_session_id: int | None = Query(
        None,
        description="Filter by training session",
    ),
    player_id: int | None = Query(
        None,
        description="Filter by player",
    ),
    status_filter: AttendanceStatus | None = Query(
        None,
        alias="status",
        description="Filter by attendance status",
    ),
    current_user: User = Depends(get_current_user),
):
    """
    List attendance records with pagination and filters.
    """

    items, total = TrainingAttendanceRepository.get_all(
        db,
        skip=pagination.skip,
        limit=pagination.limit,
        training_session_id=training_session_id,
        player_id=player_id,
        status=status_filter,
    )

    return Page(
        items=items,
        total=total,
        skip=pagination.skip,
        limit=pagination.limit,
    )


@router.post(
    "/",
    response_model=TrainingAttendanceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_attendance(
    attendance: TrainingAttendanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(*COACHING_ROLES)
    ),
):
    """
    Record attendance for a player.
    """

    session = TrainingSessionRepository.get_by_id(
        db,
        attendance.training_session_id,
    )

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Training session not found",
        )

    player = db.get(Player, attendance.player_id)

    if player is None:
        raise HTTPException(
            status_code=404,
            detail="Player not found",
        )

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
    """
    Get one attendance record.
    """

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
    current_user: User = Depends(
        require_roles(*COACHING_ROLES)
    ),
):
    """
    Update an attendance record.
    """

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
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_attendance(
    attendance_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*COACHING_ROLES)),
):
    """
    Delete an attendance record.
    """

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

    return None
