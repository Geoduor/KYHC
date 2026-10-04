from fastapi.testclient import TestClient


def create_training_context(
    client: TestClient,
    auth_headers: dict[str, str],
    slug: str = "",
):
    team = client.post(
        "/api/v1/teams/",
        headers=auth_headers,
        json={
            "name": f"Training Team {slug}".strip(),
            "category": "Youth",
        },
    ).json()

    coach = client.post(
        "/api/v1/coaches/",
        headers=auth_headers,
        json={
            "first_name": "Train",
            "last_name": "Er",
            "email": f"trainer{slug}@test.com",
            "team_id": team["id"],
        },
    ).json()

    player = client.post(
        "/api/v1/players/",
        headers=auth_headers,
        json={
            "first_name": "Attend",
            "last_name": "Ee",
            "date_of_birth": "2010-02-02",
            "gender": "Female",
            "position": "Midfield",
            "jersey_number": 8,
            "team_id": team["id"],
        },
    ).json()

    session = client.post(
        "/api/v1/training-sessions/",
        headers=auth_headers,
        json={
            "title": "Speed & Agility",
            "venue": "Kisumu Stadium",
            "session_date": "2026-08-02T09:00:00",
            "duration_minutes": 90,
            "focus_area": "Conditioning",
            "coach_id": coach["id"],
        },
    ).json()

    return team, coach, player, session


def test_create_training_session(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    _, _, _, session = create_training_context(
        client,
        auth_headers,
    )

    assert session["title"] == "Speed & Agility"
    assert session["is_completed"] is False


def test_create_training_session_unknown_coach(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    response = client.post(
        "/api/v1/training-sessions/",
        headers=auth_headers,
        json={
            "title": "Ghost Session",
            "venue": "Nowhere",
            "session_date": "2026-08-02T09:00:00",
            "duration_minutes": 60,
            "focus_area": "None",
            "coach_id": 9999,
        },
    )

    assert response.status_code == 404


def test_list_training_sessions(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    create_training_context(client, auth_headers)

    response = client.get(
        "/api/v1/training-sessions/",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["total"] >= 1
    assert isinstance(body["items"], list)


def test_filter_training_sessions(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    _, coach, _, session = create_training_context(
        client,
        auth_headers,
    )

    client.put(
        f"/api/v1/training-sessions/{session['id']}",
        headers=auth_headers,
        json={"is_completed": True},
    )

    by_coach = client.get(
        "/api/v1/training-sessions/",
        headers=auth_headers,
        params={"coach_id": coach["id"]},
    ).json()

    assert by_coach["total"] == 1

    completed = client.get(
        "/api/v1/training-sessions/",
        headers=auth_headers,
        params={"is_completed": True},
    ).json()

    assert completed["total"] == 1

    pending = client.get(
        "/api/v1/training-sessions/",
        headers=auth_headers,
        params={"is_completed": False},
    ).json()

    assert pending["total"] == 0


def test_complete_training_session(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    _, _, _, session = create_training_context(
        client,
        auth_headers,
    )

    response = client.put(
        f"/api/v1/training-sessions/{session['id']}",
        headers=auth_headers,
        json={"is_completed": True},
    )

    assert response.status_code == 200
    assert response.json()["is_completed"] is True


def test_delete_training_session(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    _, _, _, session = create_training_context(
        client,
        auth_headers,
    )

    response = client.delete(
        f"/api/v1/training-sessions/{session['id']}",
        headers=auth_headers,
    )

    assert response.status_code == 204

    fetched = client.get(
        f"/api/v1/training-sessions/{session['id']}",
        headers=auth_headers,
    )

    assert fetched.status_code == 404


def test_record_attendance(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    _, _, player, session = create_training_context(
        client,
        auth_headers,
    )

    response = client.post(
        "/api/v1/training-attendance/",
        headers=auth_headers,
        json={
            "training_session_id": session["id"],
            "player_id": player["id"],
            "status": "PRESENT",
            "arrival_time": "09:02:00",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["status"] == "PRESENT"
    assert data["player_id"] == player["id"]


def test_attendance_unknown_session(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    _, _, player, _ = create_training_context(
        client,
        auth_headers,
    )

    response = client.post(
        "/api/v1/training-attendance/",
        headers=auth_headers,
        json={
            "training_session_id": 9999,
            "player_id": player["id"],
            "status": "PRESENT",
        },
    )

    assert response.status_code == 404


def test_invalid_attendance_status(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    _, _, player, session = create_training_context(
        client,
        auth_headers,
    )

    response = client.post(
        "/api/v1/training-attendance/",
        headers=auth_headers,
        json={
            "training_session_id": session["id"],
            "player_id": player["id"],
            "status": "ON_HOLIDAY",
        },
    )

    assert response.status_code == 422


def test_filter_attendance(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    _, _, player, session = create_training_context(
        client,
        auth_headers,
    )

    client.post(
        "/api/v1/training-attendance/",
        headers=auth_headers,
        json={
            "training_session_id": session["id"],
            "player_id": player["id"],
            "status": "LATE",
        },
    )

    response = client.get(
        "/api/v1/training-attendance/",
        headers=auth_headers,
        params={
            "training_session_id": session["id"],
            "status": "LATE",
        },
    ).json()

    assert response["total"] == 1
    assert response["items"][0]["status"] == "LATE"

    present = client.get(
        "/api/v1/training-attendance/",
        headers=auth_headers,
        params={"status": "PRESENT"},
    ).json()

    assert present["total"] == 0
