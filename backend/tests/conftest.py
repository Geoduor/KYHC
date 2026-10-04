from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.database.base import Base
from app.database.dependencies import get_db
from app.main import app


# Fall back to SQLite for tests unless TEST_DATABASE_URL is provided.
TEST_DATABASE_URL = getattr(
    settings,
    "TEST_DATABASE_URL",
    "sqlite://",
)

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args=(
        {"check_same_thread": False}
        if TEST_DATABASE_URL.startswith("sqlite")
        else {}
    ),
    poolclass=StaticPool if TEST_DATABASE_URL == "sqlite://" else None,
)

TestingSessionLocal = sessionmaker(
    autoflush=False,
    autocommit=False,
    bind=engine,
)


@pytest.fixture(scope="session", autouse=True)
def setup_database() -> Generator[None, None, None]:
    import app.models  # noqa: F401

    Base.metadata.create_all(bind=engine)

    yield

    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db() -> Generator[Session, None, None]:
    connection = engine.connect()
    transaction = connection.begin()

    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db: Session) -> Generator[TestClient, None, None]:
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def admin_token(client: TestClient) -> str:
    client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Admin User",
            "email": "admin@test.com",
            "password": "adminpass123",
            "role": "CLUB_ADMIN",
        },
    )

    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "admin@test.com",
            "password": "adminpass123",
        },
    )

    return response.json()["access_token"]


@pytest.fixture
def auth_headers(admin_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {admin_token}"}
