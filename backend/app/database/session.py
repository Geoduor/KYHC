from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# psycopg accepts prepare_threshold only as a keyword argument with a
# real value (None disables prepared statements). Passing it through the
# connection URL would deliver a string and fail at query time, so it is
# configured here instead.
connect_args: dict = {}

if not settings.DATABASE_PREPARE_STATEMENTS:
    connect_args["prepare_threshold"] = None

# pool_pre_ping and pool_recycle keep connections healthy when the
# database sits behind a connection pooler (Supabase) or when the host
# idles connections out (e.g. Render free instances).
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.SQL_ECHO,
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(
    autoflush=False,
    autocommit=False,
    bind=engine,
)
