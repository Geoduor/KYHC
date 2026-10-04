from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.enums import MatchEventType
from app.models.match import Match
from app.models.match_event import MatchEvent
from app.models.player import Player
from app.models.team import Team
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

    @staticmethod
    def team_summary(
        db: Session,
        team: Team,
    ) -> dict:
        """
        Build an aggregated summary for a team from match events.

        Goals for and against are derived from the recorded match
        scores for every match the team played.
        """

        matches = (
            db.query(Match)
            .filter(
                or_(
                    Match.home_team_id == team.id,
                    Match.away_team_id == team.id,
                )
            )
            .all()
        )

        played = 0
        wins = 0
        draws = 0
        losses = 0
        goals_for = 0
        goals_against = 0

        for match in matches:
            if match.status != "Completed":
                continue

            played += 1

            if match.home_team_id == team.id:
                team_score = match.home_score or 0
                opponent_score = match.away_score or 0
            else:
                team_score = match.away_score or 0
                opponent_score = match.home_score or 0

            goals_for += team_score
            goals_against += opponent_score

            if team_score > opponent_score:
                wins += 1
            elif team_score == opponent_score:
                draws += 1
            else:
                losses += 1

        # Card and event totals for the team's players.
        goal_events = (
            db.query(func.count(MatchEvent.id))
            .join(
                Player,
                MatchEvent.player_id == Player.id,
            )
            .filter(Player.team_id == team.id)
            .filter(MatchEvent.event_type == MatchEventType.GOAL)
            .scalar()
        ) or 0

        yellow_cards = (
            db.query(func.count(MatchEvent.id))
            .join(
                Player,
                MatchEvent.player_id == Player.id,
            )
            .filter(Player.team_id == team.id)
            .filter(MatchEvent.event_type == MatchEventType.YELLOW_CARD)
            .scalar()
        ) or 0

        red_cards = (
            db.query(func.count(MatchEvent.id))
            .join(
                Player,
                MatchEvent.player_id == Player.id,
            )
            .filter(Player.team_id == team.id)
            .filter(MatchEvent.event_type == MatchEventType.RED_CARD)
            .scalar()
        ) or 0

        return {
            "team_id": team.id,
            "team_name": team.name,
            "played": played,
            "wins": wins,
            "draws": draws,
            "losses": losses,
            "goals_for": goals_for,
            "goals_against": goals_against,
            "goal_difference": goals_for - goals_against,
            "goal_events": goal_events,
            "yellow_cards": yellow_cards,
            "red_cards": red_cards,
        }
