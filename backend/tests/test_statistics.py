from fastapi.testclient import TestClient


def build_stats_context(
    client: TestClient,
    auth_headers: dict[str, str],
):
    home = client.post(
        "/api/v1/teams/",
        headers=auth_headers,
        json={"name": "Stats Home", "category": "Senior"},
    ).json()

    away = client.post(
        "/api/v1/teams/",
        headers=auth_headers,
        json={"name": "Stats Away", "category": "Senior"},
    ).json()

    scorer = client.post(
        "/api/v1/players/",
        headers=auth_headers,
        json={
            "first_name": "Star",
            "last_name": "Player",
            "date_of_birth": "2000-01-01",
            "gender": "Male",
            "position": "Forward",
            "jersey_number": 7,
            "team_id": home["id"],
        },
    ).json()

    assistant = client.post(
        "/api/v1/players/",
        headers=auth_headers,
        json={
            "first_name": "Assist",
            "last_name": "King",
            "date_of_birth": "2000-01-01",
            "gender": "Male",
            "position": "Midfield",
            "jersey_number": 8,
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

    return scorer, assistant, match


def test_player_statistics_from_events(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    scorer, assistant, match = build_stats_context(
        client,
        auth_headers,
    )

    # A goal with an assisting player.
    client.post(
        "/api/v1/match-events/",
        headers=auth_headers,
        json={
            "minute": 10,
            "event_type": "GOAL",
            "match_id": match["id"],
            "player_id": scorer["id"],
            "assisting_player_id": assistant["id"],
        },
    )

    # A second goal, no assist.
    client.post(
        "/api/v1/match-events/",
        headers=auth_headers,
        json={
            "minute": 20,
            "event_type": "GOAL",
            "match_id": match["id"],
            "player_id": scorer["id"],
        },
    )

    # A yellow card.
    client.post(
        "/api/v1/match-events/",
        headers=auth_headers,
        json={
            "minute": 30,
            "event_type": "YELLOW_CARD",
            "match_id": match["id"],
            "player_id": scorer["id"],
        },
    )

    scorer_stats = client.get(
        f"/api/v1/statistics/player/{scorer['id']}",
        headers=auth_headers,
    ).json()

    assert scorer_stats["goals"] == 2
    assert scorer_stats["assists"] == 0
    assert scorer_stats["cards"]["yellow"] == 1

    assistant_stats = client.get(
        f"/api/v1/statistics/player/{assistant['id']}",
        headers=auth_headers,
    ).json()

    assert assistant_stats["goals"] == 0
    assert assistant_stats["assists"] == 1


def test_statistics_unknown_player(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    response = client.get(
        "/api/v1/statistics/player/9999",
        headers=auth_headers,
    )

    assert response.status_code == 404


def test_player_statistics_crud(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    scorer, _, match = build_stats_context(
        client,
        auth_headers,
    )

    created = client.post(
        "/api/v1/player-statistics/",
        headers=auth_headers,
        json={
            "player_id": scorer["id"],
            "match_id": match["id"],
            "goals": 1,
            "shots": 4,
            "shots_on_target": 2,
            "rating": 7.5,
        },
    )

    assert created.status_code == 201

    statistic = created.json()

    assert statistic["goals"] == 1
    assert statistic["rating"] == 7.5

    updated = client.put(
        f"/api/v1/player-statistics/{statistic['id']}",
        headers=auth_headers,
        json={"mvp": True},
    )

    assert updated.status_code == 200
    assert updated.json()["mvp"] is True

    fetched = client.get(
        "/api/v1/player-statistics/",
        headers=auth_headers,
    )

    assert fetched.status_code == 200
    assert len(fetched.json()) >= 1
