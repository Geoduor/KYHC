# KYHC API Documentation

Reference notes for the Kisumu Youngsters Hockey Club management API.

Base URL: `http://127.0.0.1:8000/api/v1`

## Authentication

The API uses OAuth2 password flow with JWT access tokens.

1. Register a user with `POST /auth/register`.
2. Exchange credentials for a token at `POST /auth/login` (form encoded:
   `username` = email, `password`).
3. Send `Authorization: Bearer <token>` on every other request.

Tokens expire after `ACCESS_TOKEN_EXPIRE_MINUTES` (default 60 minutes).

### Roles

| Role            | Intended use                        |
| --------------- | ----------------------------------- |
| SUPER_ADMIN     | Full system control                 |
| CLUB_ADMIN      | Club-wide management                |
| COACH           | Team coaching and training          |
| ASSISTANT_COACH | Assists the head coach              |
| TEAM_MANAGER    | Team logistics and registration     |
| MEDIC           | Medical and injury records          |
| FINANCE         | Financial records                   |
| PLAYER          | Player self-service                 |

## Data Model

```
Team 1─* Player 1─* TrainingAttendance *─1 TrainingSession *─1 Coach
 │                 └─* PlayerStatistic *─1 Match
 ├─* Coach
 ├─* Match (home / away)
 │     └─* MatchEvent (player, assisting player)
 └─* Player
```

### Match events

`event_type` accepts: `GOAL`, `ASSIST`, `GREEN_CARD`, `YELLOW_CARD`,
`RED_CARD`, `PENALTY_CORNER`, `PENALTY_STROKE`, `SAVE`, `SUBSTITUTION_IN`,
`SUBSTITUTION_OUT`, `INJURY`.

An assist is counted for a player when they are linked as
`assisting_player_id` on an event, or when an explicit `ASSIST` event was
recorded with them as the acting player.

### Attendance statuses

`PRESENT`, `LATE`, `ABSENT`, `EXCUSED`, `INJURED`, `AWAY`.

### Match statuses

Free-form text; the default is `Scheduled`. Suggested values: `Scheduled`,
`Completed`, `Postponed`, `Cancelled`.

## Statistics

`GET /statistics/player/{player_id}` returns an aggregate built from match
events:

```json
{
  "player_id": 2,
  "player_name": "John Doe",
  "goals": 1,
  "assists": 0,
  "cards": { "green": 0, "yellow": 1, "red": 0 }
}
```

`GET /statistics/team/{team_id}` returns an aggregate built from completed
matches and the team's player events:

```json
{
  "team_id": 1,
  "team_name": "Men's Team",
  "played": 4,
  "wins": 3,
  "draws": 0,
  "losses": 1,
  "goals_for": 9,
  "goals_against": 4,
  "goal_difference": 5,
  "goal_events": 9,
  "yellow_cards": 2,
  "red_cards": 0
}
```

Per-match detailed statistics (shots, passes, tackles, rating, MVP, ...)
are stored through the `player-statistics` endpoints. A player can have
only one statistics record per match.

## Pagination and Filtering

Every list endpoint returns a page envelope:

```json
{
  "items": [ ... ],
  "total": 42,
  "skip": 0,
  "limit": 25
}
```

- `skip` (default 0, min 0) and `limit` (default 50, 1–200).
- Entity-specific filters, for example:
  - Teams: `search`, `category`, `is_active`
  - Players: `search`, `team_id`, `position`, `is_active`
  - Coaches: `search`, `team_id`, `is_active`
  - Matches: `team_id`, `status`, `competition`, `upcoming_only`
  - Match events: `match_id`, `player_id`, `event_type`
  - Training sessions: `coach_id`, `is_completed`
  - Attendance: `training_session_id`, `player_id`, `status`
  - Player statistics: `player_id`, `match_id`, `mvp_only`
  - Users (admin): `search`, `role`, `is_active`

## Permissions

| Area                             | Allowed roles                          |
| -------------------------------- | -------------------------------------- |
| Reading anything                 | Any authenticated user                 |
| Teams / players / coaches / matches writes | SUPER_ADMIN, CLUB_ADMIN, TEAM_MANAGER |
| Match events / training / statistics writes | SUPER_ADMIN, CLUB_ADMIN, COACH, ASSISTANT_COACH |
| User management                  | SUPER_ADMIN, CLUB_ADMIN                |

Public registration always creates a `PLAYER`. Administrators create staff
accounts via `POST /users/`.

## Error Responses

| Status | Meaning                                       |
| ------ | --------------------------------------------- |
| 400    | Business rule violation (e.g. duplicate team) |
| 401    | Missing, invalid or expired token             |
| 403    | Authenticated but not permitted               |
| 404    | Referenced record does not exist              |
| 422    | Request validation error                      |

## Project Conventions

- **Models** define database tables (`app/models`).
- **Schemas** define request/response shapes (`app/schemas`).
- **Repositories** own database access (`app/repositories`).
- **Services** hold business logic (`app/services`).
- **Endpoints** stay thin: resolve dependencies, call repository/service,
  return schemas (`app/api/v1/endpoints`).
