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
            "email": "coach@test.com",
            "experience_years": 5,
            "team_id": team["id"],
        },
    )

    assert response.status_code == 201
    assert response.json()["team_id"] == team["id"]
