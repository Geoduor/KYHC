from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.dependencies.auth import get_current_user

from app.models.match import Match
from app.models.player import Player
from app.models.match_event import MatchEvent

from app.repositories.match_event_repository import MatchEventRepository

from app.schemas.match_event import (
    MatchEventCreate,
    MatchEventUpdate,
    MatchEventResponse,
)

router = APIRouter()


@router.get(
    "/",
    response_model=list[MatchEventResponse],
)
def get_match_events(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Get all match events.
    """
    return MatchEventRepository.get_all(db)


@router.post(
    "/",
    response_model=MatchEventResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_match_event(
    event: MatchEventCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Create a new match event.
    """

    match = db.get(Match, event.match_id)

    if match is None:
        raise HTTPException(
            status_code=404,
            detail="Match not found",
        )

    player = db.get(Player, event.player_id)

    if player is None:
        raise HTTPException(
            status_code=404,
            detail="Player not found",
        )

    db_event = MatchEvent(**event.model_dump())

    return MatchEventRepository.create(
        db,
        db_event,
    )


@router.get(
    "/{event_id}",
    response_model=MatchEventResponse,
)
def get_match_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Get one match event.
    """

    event = MatchEventRepository.get_by_id(
        db,
        event_id,
    )

    if event is None:
        raise HTTPException(
            status_code=404,
            detail="Match event not found",
        )

    return event


@router.put(
    "/{event_id}",
    response_model=MatchEventResponse,
)
def update_match_event(
    event_id: int,
    updated_event: MatchEventUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Update a match event.
    """

    event = MatchEventRepository.get_by_id(
        db,
        event_id,
    )

    if event is None:
        raise HTTPException(
            status_code=404,
            detail="Match event not found",
        )

    update_data = updated_event.model_dump(
        exclude_unset=True,
    )

    for key, value in update_data.items():
        setattr(
            event,
            key,
            value,
        )

    return MatchEventRepository.update(
        db,
        event,
    )


@router.delete(
    "/{event_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_match_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Delete a match event.
    """

    event = MatchEventRepository.get_by_id(
        db,
        event_id,
    )

    if event is None:
        raise HTTPException(
            status_code=404,
            detail="Match event not found",
        )

    MatchEventRepository.delete(
        db,
        event,
    )