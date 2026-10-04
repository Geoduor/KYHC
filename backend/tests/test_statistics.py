from fastapi.testclient import TestClient


def build_stats_context(
    client: TestClient,
    auth_headers: dict[str, str],
    slug: str = "",
):
    home = client.post(
        "/api/v1/teams/",
        headers=auth_headers,
        json={
            "name": f"Stats Home {slug}".strip(),
            "category": "Senior",
        },
    ).json()

    away = client.post(
        "/api/v1/teams/",
        headers=auth_headers,
        json={
            "name": f"Stats Away {slug}".strip(),
            "category": "Senior",
        },
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

    return scorer, assistant, match, home, away


def test_player_statistics_from_events(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    scorer, assistant, match, _, _ = build_stats_context(
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


def test_team_statistics(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    _, _, match, home, _ = build_stats_context(
        client,
        auth_headers,
    )

    client.put(
        f"/api/v1/matches/{match['id']}",
        headers=auth_headers,
        json={
            "status": "Completed",
            "home_score": 3,
            "away_score": 1,
        },
    )

    response = client.get(
        f"/api/v1/statistics/team/{home['id']}",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["played"] == 1
    assert body["wins"] == 1
    assert body["goals_for"] == 3
    assert body["goals_against"] == 1
    assert body["goal_difference"] == 2


def test_team_statistics_unknown_team(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    response = client.get(
        "/api/v1/statistics/team/9999",
        headers=auth_headers,
    )

    assert response.status_code == 404


def test_player_statistics_crud(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    scorer, _, match, _, _ = build_stats_context(
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
        params={"mvp_only": True},
    )

    assert fetched.status_code == 200
    assert fetched.json()["total"] == 1


def test_duplicate_player_match_statistics_rejected(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    scorer, _, match, _, _ = build_stats_context(
        client,
        auth_headers,
    )

    payload = {
        "player_id": scorer["id"],
        "match_id": match["id"],
        "goals": 1,
    }

    first = client.post(
        "/api/v1/player-statistics/",
        headers=auth_headers,
        json=payload,
    )

    assert first.status_code == 201

    second = client.post(
        "/api/v1/player-statistics/",
        headers=auth_headers,
        json=payload,
    )

    assert second.status_code == 400


def test_player_statistics_unknown_references(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    scorer, _, match, _, _ = build_stats_context(
        client,
        auth_headers,
    )

    unknown_player = client.post(
        "/api/v1/player-statistics/",
        headers=auth_headers,
        json={
            "player_id": 9999,
            "match_id": match["id"],
        },
    )

    assert unknown_player.status_code == 404

    unknown_match = client.post(
        "/api/v1/player-statistics/",
        headers=auth_headers,
        json={
            "player_id": scorer["id"],
            "match_id": 9999,
        },
    )

    assert unknown_match.status_code == 404
