from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.pagination import Pagination
from app.core.roles import COACHING_ROLES
from app.database.dependencies import get_db
from app.dependencies.auth import get_current_user, require_roles

from app.models.match import Match
from app.models.player import Player
from app.models.match_event import MatchEvent
from app.models.enums import MatchEventType
from app.models.user import User

from app.repositories.match_event_repository import MatchEventRepository

from app.schemas.common import Page
from app.schemas.match_event import (
    MatchEventCreate,
    MatchEventUpdate,
    MatchEventResponse,
)

router = APIRouter()


@router.get(
    "/",
    response_model=Page[MatchEventResponse],
)
def get_match_events(
    db: Session = Depends(get_db),
    pagination: Pagination = Depends(),
    match_id: int | None = Query(
        None,
        description="Filter by match",
    ),
    player_id: int | None = Query(
        None,
        description="Filter by player (actor or assister)",
    ),
    event_type: MatchEventType | None = Query(
        None,
        description="Filter by event type",
    ),
    current_user: User = Depends(get_current_user),
):
    """
    List match events with pagination and filters.
    """

    items, total = MatchEventRepository.get_all(
        db,
        skip=pagination.skip,
        limit=pagination.limit,
        match_id=match_id,
        player_id=player_id,
        event_type=event_type,
    )

    return Page(
        items=items,
        total=total,
        skip=pagination.skip,
        limit=pagination.limit,
    )


@router.post(
    "/",
    response_model=MatchEventResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_match_event(
    event: MatchEventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(*COACHING_ROLES)
    ),
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

    if event.assisting_player_id is not None:
        assistant = db.get(Player, event.assisting_player_id)

        if assistant is None:
            raise HTTPException(
                status_code=404,
                detail="Assisting player not found",
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
    current_user: User = Depends(get_current_user),
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
    current_user: User = Depends(
        require_roles(*COACHING_ROLES)
    ),
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

    player_id = update_data.get("player_id")

    if player_id is not None:
        if db.get(Player, player_id) is None:
            raise HTTPException(
                status_code=404,
                detail="Player not found",
            )

    assisting_player_id = update_data.get(
        "assisting_player_id",
    )

    if assisting_player_id is not None:
        if db.get(Player, assisting_player_id) is None:
            raise HTTPException(
                status_code=404,
                detail="Assisting player not found",
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
    current_user: User = Depends(require_roles(*COACHING_ROLES)),
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
