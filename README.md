# KYHC — Kisumu Youngstars Hockey Club Management System

A club management system for **Kisumu Youngstars Hockey Club**.

The system tracks teams, players, coaches, matches, match events, training
sessions, attendance, and player statistics — with JWT authentication and
role-based access control.

## Tech Stack

| Layer      | Technology                                  |
| ---------- | ------------------------------------------- |
| Backend    | FastAPI + Uvicorn                           |
| Database   | PostgreSQL 18 (SQLAlchemy 2.0 + psycopg)    |
| Migrations | Alembic                                     |
| Auth       | OAuth2 password flow with JWT (python-jose) |
| Passwords  | pwdlib (Argon2)                             |
| Frontend   | React 19 + Vite + TypeScript + Tailwind CSS |
| Backend tests | pytest + FastAPI TestClient (SQLite)     |
| CI         | GitHub Actions (backend tests + frontend build) |

## Project Layout

```
KYHC/
├── backend/
│   ├── alembic/               # Database migrations
│   ├── app/
│   │   ├── api/v1/            # API routes (auth, users, teams, ...)
│   │   ├── core/              # Settings, security, roles, pagination
│   │   ├── database/          # Engine, session, init/seed helpers
│   │   ├── dependencies/      # Auth dependencies (current user, roles)
│   │   ├── models/            # SQLAlchemy models
│   │   ├── repositories/      # Database access layer
│   │   ├── schemas/           # Pydantic request/response models
│   │   └── services/          # Business logic (statistics)
│   ├── tests/                 # pytest suite
│   └── requirements*.txt
├── frontend/
│   └── src/
│       ├── components/        # Layout, table, modal, UI primitives
│       ├── context/           # Auth provider
│       ├── hooks/             # List/pagination hook
│       ├── lib/               # API client, formatters
│       ├── pages/             # Login, dashboard, teams, players, ...
│       └── types/             # Shared TypeScript types
├── docs/                      # Project documentation
└── .github/workflows/         # CI pipeline
```

## Getting Started

### Backend

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

Create the database and apply migrations:

```bash
createdb kyhc_db
alembic upgrade head
```

Seed the first super admin (optional):

```bash
python -m app.database.init_db
```

Run the API:

```bash
uvicorn app.main:app --reload
```

- API: http://127.0.0.1:8000
- Swagger UI: http://127.0.0.1:8000/docs

### Frontend

```bash
cd frontend
npm install

cp .env.example .env   # adjust VITE_API_URL if needed
npm run dev
```

- Web app: http://localhost:5173

Sign in with the super admin account created during backend setup, or a
staff account created by an administrator through the Users page.

## Running the Tests

```bash
cd backend
pip install -r requirements-dev.txt
pytest -q
```

The suite runs against an in-memory SQLite database, so no PostgreSQL is
needed for tests. It also works without a `.env` file (CI-safe defaults).

Frontend checks:

```bash
cd frontend
npm run build   # typecheck + production build
```

## API Overview

All routes are prefixed with `/api/v1`. Everything except `auth/register`
and `auth/login` requires a bearer token.

| Area                | Routes                                                     |
| ------------------- | ---------------------------------------------------------- |
| Authentication      | `POST /auth/register`, `POST /auth/login`                  |
| Users               | `GET /users/me`; admin CRUD under `/users/`                |
| Teams               | `GET/POST /teams/`, `GET/PUT/DELETE /teams/{id}`           |
| Players             | `GET/POST /players/`, `GET/PUT/DELETE /players/{id}`       |
| Coaches             | `GET/POST /coaches/`, `GET/PUT/DELETE /coaches/{id}`       |
| Matches             | `GET/POST /matches/`, `GET/PUT/DELETE /matches/{id}`       |
| Match events        | `GET/POST /match-events/`, `GET/PUT/DELETE /match-events/{id}` |
| Training sessions   | `GET/POST /training-sessions/`, `GET/PUT/DELETE /training-sessions/{id}` |
| Training attendance | `GET/POST /training-attendance/`, `GET/PUT/DELETE /training-attendance/{id}` |
| Player statistics   | `GET/POST /player-statistics/`, `GET/PUT/DELETE /player-statistics/{id}` |
| Statistics summary  | `GET /statistics/player/{id}`, `GET /statistics/team/{id}` |

### Pagination and filters

List endpoints return a page envelope and accept filters:

```json
{
  "items": [ ... ],
  "total": 42,
  "skip": 0,
  "limit": 25
}
```

Common query parameters: `skip`, `limit`, plus per-entity filters such as
`search`, `team_id`, `status`, `is_active`, `event_type`, etc.

### Roles and permissions

| Role            | Read | Manage teams/players/coaches/matches | Manage events/training/statistics | Manage users |
| --------------- | ---- | ------------------------------------ | --------------------------------- | ------------ |
| SUPER_ADMIN     | ✓    | ✓                                    | ✓                                 | ✓            |
| CLUB_ADMIN      | ✓    | ✓                                    | ✓                                 | ✓            |
| TEAM_MANAGER    | ✓    | ✓                                    | —                                 | —            |
| COACH           | ✓    | —                                    | ✓                                 | —            |
| ASSISTANT_COACH | ✓    | —                                    | ✓                                 | —            |
| MEDIC / FINANCE | ✓    | —                                    | —                                 | —            |
| PLAYER          | ✓    | —                                    | —                                 | —            |

Public registration always creates a `PLAYER` account; staff accounts are
created by administrators through `POST /users/`.

### Authentication

```bash
# Register (creates a PLAYER account)
curl -X POST http://127.0.0.1:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Jane Doe","email":"jane@kyhc.local","password":"secret123"}'

# Login (OAuth2 password form)
curl -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -d "username=jane@kyhc.local&password=secret123"
```

Use the returned token on all other requests:

```bash
curl http://127.0.0.1:8000/api/v1/teams/ \
  -H "Authorization: Bearer <access_token>"
```

## Database Migrations

```bash
# Create a migration after changing models
alembic revision --autogenerate -m "describe the change"

# Apply migrations
alembic upgrade head

# Roll back one revision
alembic downgrade -1
```

## Deployment

KYHC is deployed without containers:

| Piece     | Host                    |
| --------- | ----------------------- |
| Database  | Supabase (PostgreSQL)   |
| Backend   | Render (web service)    |
| Frontend  | Vercel (static hosting) |

The complete walkthrough lives in [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).
In short:

1. **Supabase** — create a project and copy the shared pooler connection
   string, converting it to `postgresql+psycopg://...?sslmode=require`.
2. **Render** — apply `render.yaml` (New → Blueprint). Provide
   `DATABASE_URL` and `BACKEND_CORS_ORIGINS`; `SECRET_KEY` is generated.
   Migrations run automatically at start.
3. **Vercel** — import the repo with `frontend` as the root directory and
   set `VITE_API_URL` to the Render URL.
4. Set `DATABASE_PREPARE_STATEMENTS=false` when connecting through
   Supabase's transaction pooler (port 6543).

## Continuous Integration

`.github/workflows/ci.yml` runs on every push and pull request to `main`:

- **Backend**: installs `requirements-dev.txt` and runs the pytest suite.
- **Frontend**: installs npm dependencies and runs the production build
  (which includes TypeScript typechecking).

## Roadmap

- [x] Authentication (register/login, JWT)
- [x] Teams, players and coaches CRUD
- [x] Matches and match events CRUD
- [x] Training sessions and attendance
- [x] Player match statistics and summary endpoints
- [x] Role restrictions on write endpoints
- [x] Pagination and filtering on list endpoints
- [x] React web client (dashboard, CRUD, statistics)
- [x] CI pipeline
- [x] Render + Vercel + Supabase deployment setup
- [ ] Match event entry and attendance UI refinements
- [ ] Email notifications for upcoming sessions
- [ ] Docker setup (deferred — developing on Windows for now)

## License

See [LICENSE](LICENSE).
