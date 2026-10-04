from sqlalchemy.orm import Session

from app.models.enums import MatchEventType
from app.repositories.match_event_repository import MatchEventRepository


class StatisticsService:
    """
    Service responsible for calculating player and team statistics.
    """

    @staticmethod
    def player_goals(
        db: Session,
        player_id: int,
    ) -> int:
        goals = MatchEventRepository.get_goals_by_player(
            db,
            player_id,
        )

        return len(goals)

    @staticmethod
    def player_assists(
        db: Session,
        player_id: int,
    ) -> int:
        assists = MatchEventRepository.get_assists_by_player(
            db,
            player_id,
        )

        return len(assists)

    @staticmethod
    def player_cards(
        db: Session,
        player_id: int,
    ):
        events = MatchEventRepository.get_by_player(
            db,
            player_id,
        )

        yellow = 0
        green = 0
        red = 0

        for event in events:

            if event.event_type == MatchEventType.YELLOW_CARD:
                yellow += 1

            elif event.event_type == MatchEventType.GREEN_CARD:
                green += 1

            elif event.event_type == MatchEventType.RED_CARD:
                red += 1

        return {
            "green": green,
            "yellow": yellow,
            "red": red,
        }