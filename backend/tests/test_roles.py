from fastapi.testclient import TestClient


def make_team_payload(name: str = "Role Team"):
    return {
        "name": name,
        "category": "Youth",
    }


def test_player_cannot_write(client: TestClient, player_headers) -> None:
    create = client.post(
        "/api/v1/teams/",
        headers=player_headers,
        json=make_team_payload("Player Cannot Create"),
    )

    assert create.status_code == 403

    admin_created = client.post(
        "/api/v1/teams/",
        headers=player_headers,
        json=make_team_payload("Still 403"),
    )

    assert admin_created.status_code == 403


def test_player_can_read(
    client: TestClient,
    auth_headers,
    player_headers,
) -> None:
    client.post(
        "/api/v1/teams/",
        headers=auth_headers,
        json=make_team_payload("Readable Team"),
    )

    response = client.get(
        "/api/v1/teams/",
        headers=player_headers,
    )

    assert response.status_code == 200
    assert response.json()["total"] >= 1


def test_coach_can_manage_matches(
    client: TestClient,
    auth_headers,
    coach_headers,
) -> None:
    home = client.post(
        "/api/v1/teams/",
        headers=auth_headers,
        json=make_team_payload("Coach Home"),
    ).json()

    away = client.post(
        "/api/v1/teams/",
        headers=auth_headers,
        json=make_team_payload("Coach Away"),
    ).json()

    response = client.post(
        "/api/v1/matches/",
        headers=coach_headers,
        json={
            "home_team_id": home["id"],
            "away_team_id": away["id"],
            "competition": "League",
            "venue": "Stadium",
            "match_date": "2026-08-01T15:00:00",
        },
    )

    assert response.status_code == 403


def test_coach_can_manage_match_events(
    client: TestClient,
    auth_headers,
    coach_headers,
) -> None:
    home = client.post(
        "/api/v1/teams/",
        headers=auth_headers,
        json=make_team_payload("Event Home"),
    ).json()

    away = client.post(
        "/api/v1/teams/",
        headers=auth_headers,
        json=make_team_payload("Event Away"),
    ).json()

    player = client.post(
        "/api/v1/players/",
        headers=auth_headers,
        json={
            "first_name": "Event",
            "last_name": "Player",
            "date_of_birth": "2000-01-01",
            "gender": "Male",
            "position": "Forward",
            "jersey_number": 5,
            "team_id": home["id"],
        },
    ).json()

    match = client.post(
        "/api/v1/matches/",
        headers=auth_headers,
        json={
            "home_team_id": home["id"],
            "away_team_id": away["id"],
            "competition": "League",
            "venue": "Stadium",
            "match_date": "2026-08-01T15:00:00",
        },
    ).json()

    response = client.post(
        "/api/v1/match-events/",
        headers=coach_headers,
        json={
            "minute": 5,
            "event_type": "GOAL",
            "match_id": match["id"],
            "player_id": player["id"],
        },
    )

    assert response.status_code == 201


def test_coach_cannot_manage_teams(
    client: TestClient,
    coach_headers,
) -> None:
    response = client.post(
        "/api/v1/teams/",
        headers=coach_headers,
        json=make_team_payload("Coach Team"),
    )

    assert response.status_code == 403


def test_player_cannot_manage_training(
    client: TestClient,
    auth_headers,
    player_headers,
) -> None:
    team = client.post(
        "/api/v1/teams/",
        headers=auth_headers,
        json=make_team_payload("Training Role Team"),
    ).json()

    coach = client.post(
        "/api/v1/coaches/",
        headers=auth_headers,
        json={
            "first_name": "Role",
            "last_name": "Coach",
            "email": "rolecoach@test.com",
            "team_id": team["id"],
        },
    ).json()

    response = client.post(
        "/api/v1/training-sessions/",
        headers=player_headers,
        json={
            "title": "No Permission",
            "venue": "Stadium",
            "session_date": "2026-08-02T09:00:00",
            "duration_minutes": 60,
            "focus_area": "None",
            "coach_id": coach["id"],
        },
    )

    assert response.status_code == 403


def test_player_cannot_access_user_admin(
    client: TestClient,
    player_headers,
) -> None:
    list_response = client.get(
        "/api/v1/users/",
        headers=player_headers,
    )

    assert list_response.status_code == 403

    create_response = client.post(
        "/api/v1/users/",
        headers=player_headers,
        json={
            "full_name": "Sneaky",
            "email": "sneaky2@test.com",
            "password": "password123",
            "role": "SUPER_ADMIN",
        },
    )

    assert create_response.status_code == 403


def test_admin_can_create_staff_user(
    client: TestClient,
    auth_headers,
) -> None:
    response = client.post(
        "/api/v1/users/",
        headers=auth_headers,
        json={
            "full_name": "New Coach",
            "email": "newcoach@test.com",
            "password": "password123",
            "role": "COACH",
        },
    )

    assert response.status_code == 201
    assert response.json()["role"] == "COACH"


def test_admin_cannot_delete_self(
    client: TestClient,
    auth_headers,
) -> None:
    me = client.get(
        "/api/v1/users/me",
        headers=auth_headers,
    ).json()

    response = client.delete(
        f"/api/v1/users/{me['id']}",
        headers=auth_headers,
    )

    assert response.status_code == 400


def test_admin_cannot_change_own_role(
    client: TestClient,
    auth_headers,
) -> None:
    me = client.get(
        "/api/v1/users/me",
        headers=auth_headers,
    ).json()

    response = client.put(
        f"/api/v1/users/{me['id']}",
        headers=auth_headers,
        json={"role": "PLAYER"},
    )

    assert response.status_code == 400


def test_admin_can_edit_and_deactivate_user(
    client: TestClient,
    auth_headers,
) -> None:
    created = client.post(
        "/api/v1/users/",
        headers=auth_headers,
        json={
            "full_name": "Temp User",
            "email": "temp@test.com",
            "password": "password123",
            "role": "MEDIC",
        },
    ).json()

    updated = client.put(
        f"/api/v1/users/{created['id']}",
        headers=auth_headers,
        json={
            "full_name": "Renamed User",
            "is_active": False,
        },
    )

    assert updated.status_code == 200

    body = updated.json()

    assert body["full_name"] == "Renamed User"
    assert body["is_active"] is False

    # The user list can filter by active status.
    active = client.get(
        "/api/v1/users/",
        headers=auth_headers,
        params={"is_active": True},
    ).json()

    assert all(user["is_active"] for user in active["items"])


def test_admin_user_search(
    client: TestClient,
    auth_headers,
) -> None:
    client.post(
        "/api/v1/users/",
        headers=auth_headers,
        json={
            "full_name": "Searchable Person",
            "email": "searchable@test.com",
            "password": "password123",
            "role": "FINANCE",
        },
    )

    response = client.get(
        "/api/v1/users/",
        headers=auth_headers,
        params={"search": "searchable"},
    )

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["items"][0]["email"] == "searchable@test.com"
