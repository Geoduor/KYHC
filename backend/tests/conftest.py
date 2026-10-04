import os
from collections.abc import Generator

# Provide safe defaults so the suite can run anywhere (including CI)
# before the application settings are imported.
os.environ.setdefault("APP_NAME", "KYHC API")
os.environ.setdefault("APP_VERSION", "1.0.0")
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/kyhc_db",
)
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "60")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.core.security import hash_password
from app.database.base import Base
from app.database.dependencies import get_db
from app.main import app
from app.models.user import User, UserRole


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


def make_user(
    db: Session,
    *,
    email: str,
    role: UserRole,
    password: str = "password123",
    full_name: str = "Test User",
) -> User:
    """
    Create a user directly in the database with the given role.
    """

    user = User(
        full_name=full_name,
        email=email,
        hashed_password=hash_password(password),
        role=role,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def login_token(
    client: TestClient,
    email: str,
    password: str = "password123",
) -> str:
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": email,
            "password": password,
        },
    )

    assert response.status_code == 200, response.text

    return response.json()["access_token"]


@pytest.fixture
def admin_user(db: Session) -> User:
    return make_user(
        db,
        email="admin@test.com",
        role=UserRole.CLUB_ADMIN,
        full_name="Admin User",
    )


@pytest.fixture
def player_user(db: Session) -> User:
    return make_user(
        db,
        email="player@test.com",
        role=UserRole.PLAYER,
        full_name="Player User",
    )


@pytest.fixture
def coach_user(db: Session) -> User:
    return make_user(
        db,
        email="coach@test.com",
        role=UserRole.COACH,
        full_name="Coach User",
    )


@pytest.fixture
def admin_token(
    client: TestClient,
    admin_user: User,
) -> str:
    return login_token(client, "admin@test.com")


@pytest.fixture
def auth_headers(admin_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def player_headers(
    client: TestClient,
    player_user: User,
) -> dict[str, str]:
    token = login_token(client, "player@test.com")

    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def coach_headers(
    client: TestClient,
    coach_user: User,
) -> dict[str, str]:
    token = login_token(client, "coach@test.com")

    return {"Authorization": f"Bearer {token}"}
