from fastapi.testclient import TestClient


def test_health_check(client: TestClient) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_register_user(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "New User",
            "email": "new@test.com",
            "password": "secret123",
            "role": "COACH",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["email"] == "new@test.com"
    assert data["role"] == "COACH"
    assert "password" not in data
    assert "hashed_password" not in data


def test_register_duplicate_email(
    client: TestClient,
) -> None:
    payload = {
        "full_name": "Duplicate",
        "email": "duplicate@test.com",
        "password": "secret123",
        "role": "PLAYER",
    }

    first = client.post(
        "/api/v1/auth/register",
        json=payload,
    )

    assert first.status_code == 201

    second = client.post(
        "/api/v1/auth/register",
        json=payload,
    )

    assert second.status_code == 400


def test_login_success(client: TestClient) -> None:
    client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Login User",
            "email": "login@test.com",
            "password": "secret123",
            "role": "CLUB_ADMIN",
        },
    )

    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "login@test.com",
            "password": "secret123",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["token_type"] == "bearer"
    assert data["access_token"]


def test_login_wrong_password(
    client: TestClient,
) -> None:
    client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Wrong Pass",
            "email": "wrong@test.com",
            "password": "secret123",
            "role": "PLAYER",
        },
    )

    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "wrong@test.com",
            "password": "not-the-password",
        },
    )

    assert response.status_code == 401


def test_get_current_user(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    response = client.get(
        "/api/v1/users/me",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["email"] == "admin@test.com"


def test_protected_route_requires_token(
    client: TestClient,
) -> None:
    response = client.get("/api/v1/teams/")

    assert response.status_code == 401


def test_protected_route_rejects_bad_token(
    client: TestClient,
) -> None:
    response = client.get(
        "/api/v1/teams/",
        headers={"Authorization": "Bearer not-a-token"},
    )

    assert response.status_code == 401
