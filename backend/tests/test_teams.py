from fastapi.testclient import TestClient


def create_team(
    client: TestClient,
    auth_headers: dict[str, str],
    name: str = "U16 Team",
):
    return client.post(
        "/api/v1/teams/",
        headers=auth_headers,
        json={
            "name": name,
            "category": "Youth",
            "description": "A youth team",
        },
    )


def test_create_and_get_team(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    response = create_team(client, auth_headers)

    assert response.status_code == 201

    team = response.json()

    assert team["name"] == "U16 Team"
    assert team["is_active"] is True

    fetched = client.get(
        f"/api/v1/teams/{team['id']}",
        headers=auth_headers,
    )

    assert fetched.status_code == 200
    assert fetched.json()["id"] == team["id"]


def test_duplicate_team_name(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    create_team(client, auth_headers, name="Duplicate FC")

    response = create_team(
        client,
        auth_headers,
        name="Duplicate FC",
    )

    assert response.status_code == 400


def test_update_team(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    team = create_team(
        client,
        auth_headers,
        name="Updatable",
    ).json()

    response = client.put(
        f"/api/v1/teams/{team['id']}",
        headers=auth_headers,
        json={"category": "Senior"},
    )

    assert response.status_code == 200
    assert response.json()["category"] == "Senior"
    assert response.json()["name"] == "Updatable"


def test_delete_team(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    team = create_team(
        client,
        auth_headers,
        name="Deletable",
    ).json()

    response = client.delete(
        f"/api/v1/teams/{team['id']}",
        headers=auth_headers,
    )

    assert response.status_code == 204

    fetched = client.get(
        f"/api/v1/teams/{team['id']}",
        headers=auth_headers,
    )

    assert fetched.status_code == 404


def test_team_not_found(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    response = client.get(
        "/api/v1/teams/9999",
        headers=auth_headers,
    )

    assert response.status_code == 404


def test_list_teams_returns_page(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    create_team(client, auth_headers, name="Page Team A")
    create_team(client, auth_headers, name="Page Team B")

    response = client.get(
        "/api/v1/teams/",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert set(body.keys()) == {"items", "total", "skip", "limit"}
    assert body["total"] == 2
    assert len(body["items"]) == 2


def test_pagination_skip_limit(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    for index in range(5):
        create_team(
            client,
            auth_headers,
            name=f"Paginated {index}",
        )

    response = client.get(
        "/api/v1/teams/",
        headers=auth_headers,
        params={"skip": 1, "limit": 2},
    )

    body = response.json()

    assert body["total"] == 5
    assert body["skip"] == 1
    assert body["limit"] == 2
    assert len(body["items"]) == 2


def test_list_filter_search_and_category(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    create_team(client, auth_headers, name="Lions")
    client.post(
        "/api/v1/teams/",
        headers=auth_headers,
        json={"name": "Eagles", "category": "Senior"},
    )

    search = client.get(
        "/api/v1/teams/",
        headers=auth_headers,
        params={"search": "lion"},
    ).json()

    assert search["total"] == 1
    assert search["items"][0]["name"] == "Lions"

    category = client.get(
        "/api/v1/teams/",
        headers=auth_headers,
        params={"category": "Senior"},
    ).json()

    assert category["total"] == 1
    assert category["items"][0]["name"] == "Eagles"


def test_create_player_in_team(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    team = create_team(
        client,
        auth_headers,
        name="Player Team",
    ).json()

    response = client.post(
        "/api/v1/players/",
        headers=auth_headers,
        json={
            "first_name": "Jane",
            "last_name": "Doe",
            "date_of_birth": "2010-04-12",
            "gender": "Female",
            "position": "Forward",
            "jersey_number": 9,
            "team_id": team["id"],
        },
    )

    assert response.status_code == 201

    player = response.json()

    assert player["team_id"] == team["id"]
    assert player["is_active"] is True


def test_create_player_with_unknown_team(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    response = client.post(
        "/api/v1/players/",
        headers=auth_headers,
        json={
            "first_name": "No",
            "last_name": "Team",
            "date_of_birth": "2010-04-12",
            "gender": "Male",
            "position": "Defender",
            "jersey_number": 4,
            "team_id": 9999,
        },
    )

    assert response.status_code == 404


def test_filter_players_by_team(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    team_a = create_team(
        client,
        auth_headers,
        name="Team A",
    ).json()

    team_b = create_team(
        client,
        auth_headers,
        name="Team B",
    ).json()

    for team in (team_a, team_b):
        client.post(
            "/api/v1/players/",
            headers=auth_headers,
            json={
                "first_name": "Player",
                "last_name": f"Of {team['name']}",
                "date_of_birth": "2010-04-12",
                "gender": "Male",
                "position": "Forward",
                "jersey_number": 9,
                "team_id": team["id"],
            },
        )

    response = client.get(
        "/api/v1/players/",
        headers=auth_headers,
        params={"team_id": team_a["id"]},
    )

    body = response.json()

    assert body["total"] == 1
    assert body["items"][0]["team_id"] == team_a["id"]


def test_create_coach(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    team = create_team(
        client,
        auth_headers,
        name="Coach Team",
    ).json()

    response = client.post(
        "/api/v1/coaches/",
        headers=auth_headers,
        json={
            "first_name": "John",
            "last_name": "Coach",
            "email": "headcoach@test.com",
            "experience_years": 5,
            "team_id": team["id"],
        },
    )

    assert response.status_code == 201
    assert response.json()["team_id"] == team["id"]


def test_create_coach_unknown_team(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    response = client.post(
        "/api/v1/coaches/",
        headers=auth_headers,
        json={
            "first_name": "No",
            "last_name": "Team",
            "email": "noteam@test.com",
            "team_id": 9999,
        },
    )

    assert response.status_code == 404
