# KYHC — Kisumu Youngsters Hockey Club Management System

A club management backend for **Kisumu Youngsters Hockey Club**.

The system tracks teams, players, coaches, matches, match events, training
sessions, attendance, and player statistics — with JWT authentication and
role-based access control.

## Tech Stack

| Layer      | Technology                                |
| ---------- | ----------------------------------------- |
| API        | FastAPI + Uvicorn                         |
| Database   | PostgreSQL 18 (SQLAlchemy 2.0 + psycopg)  |
| Migrations | Alembic                                   |
| Auth       | OAuth2 password flow with JWT (python-jose) |
| Passwords  | pwdlib (Argon2)                           |
| Tests      | pytest + FastAPI TestClient (SQLite)      |

## Project Layout

```
KYHC/
├── backend/
│   ├── alembic/               # Database migrations
│   ├── app/
│   │   ├── api/v1/            # API routes (auth, teams, players, ...)
│   │   ├── core/              # Settings and security helpers
│   │   ├── database/          # Engine, session, init/seed helpers
│   │   ├── dependencies/      # Auth dependencies (current user, roles)
│   │   ├── models/            # SQLAlchemy models
│   │   ├── repositories/      # Database access layer
│   │   ├── schemas/           # Pydantic request/response models
│   │   └── services/          # Business logic (statistics)
│   ├── tests/                 # pytest suite
│   └── requirements*.txt
├── docs/                      # Project documentation
├── docker/                    # (planned) container setup
├── frontend/                  # (planned) web client
└── scripts/                   # (planned) utility scripts
```

## Getting Started

### 1. Prerequisites

- Python 3.12+
- PostgreSQL 15+

### 2. Set up the backend

```bash
cd backend

python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt

cp .env.example .env   # then edit DATABASE_URL and SECRET_KEY
```

### 3. Create the database

```bash
createdb kyhc_db
```

### 4. Apply migrations

```bash
alembic upgrade head
```

### 5. Seed the first super admin (optional)

```bash
python -m app.database.init_db
```

### 6. Run the API

```bash
uvicorn app.main:app --reload
```

- API: http://127.0.0.1:8000
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## Running the Tests

```bash
cd backend
pip install -r requirements-dev.txt
pytest -q
```

The suite runs against an in-memory SQLite database, so no PostgreSQL is
needed for tests.

## API Overview

All routes are prefixed with `/api/v1`. Everything except `auth/register`
and `auth/login` requires a bearer token.

| Area                | Routes                                                     |
| ------------------- | ---------------------------------------------------------- |
| Authentication      | `POST /auth/register`, `POST /auth/login`                  |
| Users               | `GET /users/me`                                            |
| Teams               | `GET/POST /teams/`, `GET/PUT/DELETE /teams/{id}`           |
| Players             | `GET/POST /players/`, `GET/PUT/DELETE /players/{id}`       |
| Coaches             | `GET/POST /coaches/`, `GET/PUT/DELETE /coaches/{id}`       |
| Matches             | `GET/POST /matches/`, `GET/PUT/DELETE /matches/{id}`       |
| Match events        | `GET/POST /match-events/`, `GET/PUT/DELETE /match-events/{id}` |
| Training sessions   | `GET/POST /training-sessions/`, `GET/PUT/DELETE /training-sessions/{id}` |
| Training attendance | `GET/POST /training-attendance/`, `GET/PUT/DELETE /training-attendance/{id}` |
| Player statistics   | `GET/POST /player-statistics/`, `GET/PUT/DELETE /player-statistics/{id}` |
| Statistics summary  | `GET /statistics/player/{player_id}`                       |

### Authentication

```bash
# Register
curl -X POST http://127.0.0.1:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Jane Doe","email":"jane@kyhc.local","password":"secret123","role":"CLUB_ADMIN"}'

# Login (OAuth2 password form)
curl -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -d "username=jane@kyhc.local&password=secret123"
```

Use the returned token on all other requests:

```bash
curl http://127.0.0.1:8000/api/v1/teams/ \
  -H "Authorization: Bearer <access_token>"
```

### Roles

`SUPER_ADMIN`, `CLUB_ADMIN`, `COACH`, `ASSISTANT_COACH`, `TEAM_MANAGER`,
`MEDIC`, `FINANCE`, `PLAYER`.

Role-restricted dependencies are available through
`app.dependencies.auth.require_roles(...)`.

## Database Migrations

```bash
# Create a migration after changing models
alembic revision --autogenerate -m "describe the change"

# Apply migrations
alembic upgrade head

# Roll back one revision
alembic downgrade -1
```

## Roadmap

- [x] Authentication (register/login, JWT)
- [x] Teams, players and coaches CRUD
- [x] Matches and match events CRUD
- [x] Training sessions and attendance
- [x] Player match statistics and summary endpoint
- [x] Automated test suite
- [ ] Role restrictions on write endpoints
- [ ] Pagination and filtering on list endpoints
- [ ] Frontend web client
- [ ] Docker Compose setup
- [ ] CI pipeline

## License

See [LICENSE](LICENSE).
