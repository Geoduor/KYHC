from fastapi.testclient import TestClient


def setup_match_context(
    client: TestClient,
    auth_headers: dict[str, str],
):
    home = client.post(
        "/api/v1/teams/",
        headers=auth_headers,
        json={"name": "Home Team", "category": "Senior"},
    ).json()

    away = client.post(
        "/api/v1/teams/",
        headers=auth_headers,
        json={"name": "Away Team", "category": "Senior"},
    ).json()

    player = client.post(
        "/api/v1/players/",
        headers=auth_headers,
        json={
            "first_name": "Goal",
            "last_name": "Scorer",
            "date_of_birth": "2000-01-01",
            "gender": "Male",
            "position": "Forward",
            "jersey_number": 11,
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
            "venue": "Kisumu Stadium",
            "match_date": "2026-08-01T15:00:00",
        },
    ).json()

    return home, away, player, match


def test_create_match(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    _, _, _, match = setup_match_context(
        client,
        auth_headers,
    )

    assert match["status"] == "Scheduled"
    assert match["home_score"] == 0
    assert match["away_score"] == 0


def test_match_same_team_rejected(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    team = client.post(
        "/api/v1/teams/",
        headers=auth_headers,
        json={"name": "Only Team", "category": "Senior"},
    ).json()

    response = client.post(
        "/api/v1/matches/",
        headers=auth_headers,
        json={
            "home_team_id": team["id"],
            "away_team_id": team["id"],
            "competition": "League",
            "venue": "Stadium",
            "match_date": "2026-08-01T15:00:00",
        },
    )

    assert response.status_code == 400


def test_match_unknown_team_rejected(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    team = client.post(
        "/api/v1/teams/",
        headers=auth_headers,
        json={"name": "Known Team", "category": "Senior"},
    ).json()

    response = client.post(
        "/api/v1/matches/",
        headers=auth_headers,
        json={
            "home_team_id": team["id"],
            "away_team_id": 9999,
            "competition": "League",
            "venue": "Stadium",
            "match_date": "2026-08-01T15:00:00",
        },
    )

    assert response.status_code == 404


def test_update_match_score(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    _, _, _, match = setup_match_context(
        client,
        auth_headers,
    )

    response = client.put(
        f"/api/v1/matches/{match['id']}",
        headers=auth_headers,
        json={
            "status": "Completed",
            "home_score": 3,
            "away_score": 1,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "Completed"
    assert data["home_score"] == 3
    assert data["away_score"] == 1


def test_update_match_same_team_rejected(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    _, away, _, match = setup_match_context(
        client,
        auth_headers,
    )

    response = client.put(
        f"/api/v1/matches/{match['id']}",
        headers=auth_headers,
        json={"away_team_id": match["home_team_id"]},
    )

    assert response.status_code == 400


def test_filter_matches_by_team_and_status(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    home, away, _, match = setup_match_context(
        client,
        auth_headers,
    )

    client.put(
        f"/api/v1/matches/{match['id']}",
        headers=auth_headers,
        json={"status": "Completed"},
    )

    by_team = client.get(
        "/api/v1/matches/",
        headers=auth_headers,
        params={"team_id": home["id"]},
    ).json()

    assert by_team["total"] == 1

    by_status = client.get(
        "/api/v1/matches/",
        headers=auth_headers,
        params={"status": "Completed"},
    ).json()

    assert by_status["total"] == 1

    no_match = client.get(
        "/api/v1/matches/",
        headers=auth_headers,
        params={"status": "Cancelled"},
    ).json()

    assert no_match["total"] == 0


def test_create_match_event(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    _, _, player, match = setup_match_context(
        client,
        auth_headers,
    )

    response = client.post(
        "/api/v1/match-events/",
        headers=auth_headers,
        json={
            "minute": 12,
            "event_type": "GOAL",
            "match_id": match["id"],
            "player_id": player["id"],
        },
    )

    assert response.status_code == 201
    assert response.json()["event_type"] == "GOAL"


def test_match_event_unknown_match(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    _, _, player, _ = setup_match_context(
        client,
        auth_headers,
    )

    response = client.post(
        "/api/v1/match-events/",
        headers=auth_headers,
        json={
            "minute": 12,
            "event_type": "GOAL",
            "match_id": 9999,
            "player_id": player["id"],
        },
    )

    assert response.status_code == 404


def test_match_event_unknown_assisting_player(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    _, _, player, match = setup_match_context(
        client,
        auth_headers,
    )

    response = client.post(
        "/api/v1/match-events/",
        headers=auth_headers,
        json={
            "minute": 12,
            "event_type": "GOAL",
            "match_id": match["id"],
            "player_id": player["id"],
            "assisting_player_id": 9999,
        },
    )

    assert response.status_code == 404


def test_filter_match_events_by_match(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    _, _, player, match = setup_match_context(
        client,
        auth_headers,
    )

    client.post(
        "/api/v1/match-events/",
        headers=auth_headers,
        json={
            "minute": 12,
            "event_type": "GOAL",
            "match_id": match["id"],
            "player_id": player["id"],
        },
    )

    response = client.get(
        "/api/v1/match-events/",
        headers=auth_headers,
        params={"match_id": match["id"]},
    ).json()

    assert response["total"] == 1

    by_type = client.get(
        "/api/v1/match-events/",
        headers=auth_headers,
        params={"event_type": "YELLOW_CARD"},
    ).json()

    assert by_type["total"] == 0
