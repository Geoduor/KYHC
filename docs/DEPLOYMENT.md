# Deployment Guide

KYHC deploys as three managed pieces — no Docker required:

| Piece     | Host                    | Purpose                        |
| --------- | ----------------------- | ------------------------------ |
| Database  | Supabase (PostgreSQL)   | Managed Postgres + pooler      |
| Backend   | Render (web service)    | FastAPI application            |
| Frontend  | Vercel (static hosting) | React single-page app          |

```
Vercel (React SPA)  ──HTTPS──>  Render (FastAPI)  ──SSL──>  Supabase (Postgres)
```

## 1. Supabase (database)

1. Create a project at [supabase.com/dashboard](https://supabase.com/dashboard).
2. Save the database password when prompted.
3. Open **Connect** and copy a connection string.

### Which connection string to use

| Scenario                                   | Mode           | Port | Prepared statements |
| ------------------------------------------ | -------------- | ---- | ------------------- |
| Render connecting over IPv4 (typical)      | Transaction pooler | 6543 | must be disabled |
| Render on a paid plan with IPv4 add-on     | Session pooler | 5432 | supported        |

Supabase's direct connection (`db.[ref].supabase.co:5432`) is IPv6-only on
free plans, which does not work from Render. Use the **shared pooler**.

### Converting the string for SQLAlchemy

Supabase gives you a plain `postgresql://` URL. The backend needs the
psycopg driver prefix and an explicit SSL mode:

```
postgresql+psycopg://postgres.[PROJECT-REF]:[PASSWORD]@[POOLER-HOST]:6543/postgres?sslmode=require
```

Notes:

- Percent-encode reserved characters in the password (`@`, `#`, `?`, `&`).
- `sslmode=require` encrypts the connection. To also verify the server
  certificate, download the CA from Supabase's database settings and use
  `sslmode=verify-full&sslrootcert=/path/to/prod-ca.crt`.
- **Do not** add `prepare_threshold` to the URL. psycopg receives URL
  parameters as strings and fails at query time. Use
  `DATABASE_PREPARE_STATEMENTS=false` instead (see below).

### Transaction pooler setting

Running through the transaction pooler (port 6543) requires prepared
statements to be disabled. Set this on the Render service:

```
DATABASE_PREPARE_STATEMENTS=false
```

The backend turns this into `prepare_threshold=None` for psycopg, which
disables prepared statements entirely.

## 2. Render (backend)

1. In the [Render Dashboard](https://dashboard.render.com), choose
   **New → Blueprint** and connect the `KYHC` repository.
2. Render reads `render.yaml` from the repo root and proposes the
   `kyhc-api` web service. Apply it.
3. Fill in the values marked `sync: false`:

   | Variable                 | Value                                              |
   | ------------------------ | -------------------------------------------------- |
   | `DATABASE_URL`           | Supabase pooler URL from step 1                    |
   | `BACKEND_CORS_ORIGINS`   | Your Vercel URL, e.g. `https://kyhc.vercel.app`    |

   `SECRET_KEY` is generated automatically. Set `BACKEND_CORS_ORIGINS` to
   a comma-separated list if you need several origins.

4. Deploy. Migrations run automatically: the start command is
   `alembic upgrade head && uvicorn app.main:app ...` (pre-deploy commands
   need a paid plan, and Alembic is safe to re-run).

5. Verify:

   ```bash
   curl https://kyhc-api.onrender.com/
   # {"status":"healthy",...}
   ```

### Create the first super admin

Render free instances have no shell access. Either:

- **Locally against Supabase** (recommended) — run one command from the
  `backend` directory with `DATABASE_URL` pointed at Supabase:

  ```bash
  python -m app.database.init_db
  ```

  Or register through the API and promote the account in the Supabase SQL
  editor:

  ```sql
  update users set role = 'SUPER_ADMIN' where email = 'you@example.com';
  ```

### Free plan behaviour

- The service **spins down after 15 minutes** of inactivity and takes
  roughly a minute to wake on the next request.
- Free instances have no shell access and no pre-deploy commands.
- Free services restart occasionally; nothing is stored on the
  filesystem, so all state lives in Supabase.

## 3. Vercel (frontend)

1. In [Vercel](https://vercel.com/new), import the `KYHC` repository.
2. Set **Root Directory** to `frontend`. Vercel detects Vite
   automatically; `vercel.json` supplies the SPA rewrite rule so React
   Router deep links work.
3. Add an environment variable:

   | Variable       | Value                                          |
   | -------------- | ---------------------------------------------- |
   | `VITE_API_URL` | `https://kyhc-api.onrender.com/api/v1`         |

   Vite inlines this at build time — redeploy after changing it.

4. Deploy, then copy the Vercel URL into `BACKEND_CORS_ORIGINS` on Render
   and redeploy the backend.

## Checklist

- [ ] Supabase project created, password saved
- [ ] Pooler connection string converted to `postgresql+psycopg://...?sslmode=require`
- [ ] Render blueprint applied with `DATABASE_URL` and `BACKEND_CORS_ORIGINS`
- [ ] `DATABASE_PREPARE_STATEMENTS=false` when using port 6543
- [ ] Backend health check returns healthy
- [ ] Super admin account created and role promoted
- [ ] Vercel project built with `VITE_API_URL` pointing at Render
- [ ] Signed in through the deployed frontend
- [ ] CI passing on `main` (Render auto-deploys after checks pass)

## Troubleshooting

| Symptom                                          | Cause / fix                                                        |
| ------------------------------------------------ | ------------------------------------------------------------------ |
| `prepared statement "_pg3_0" already exists`     | Pooler without `DATABASE_PREPARE_STATEMENTS=false`.                |
| `TypeError: '>=' not supported ... int and str`  | `prepare_threshold` added to the URL. Remove it; use the env flag. |
| `password authentication failed`                 | Wrong password or missing project ref in the pooler username.      |
| `Network is unreachable` / connect timeout       | Using the IPv6 direct connection. Switch to the shared pooler.     |
| CORS error in the browser                        | `BACKEND_CORS_ORIGINS` missing the exact Vercel origin.            |
| First request takes ~1 minute                     | Render free instance waking from spin-down.                        |
| Frontend calls `127.0.0.1` in production         | `VITE_API_URL` unset at build time; set it and redeploy.           |

## Migrations in production

The start command applies migrations on every boot. To run them manually,
use the Supabase SQL editor for small changes, or run Alembic locally
against the Supabase URL:

```bash
cd backend
DATABASE_URL="postgresql+psycopg://...?sslmode=require" alembic upgrade head
```
