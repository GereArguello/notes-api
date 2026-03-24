from fastapi import status
from app.core.enums import DifficultyLevel

def test_create_subject_should_return_201(client, user_login):
    token = user_login["access_token"]
    user = user_login["user"]

    data = {
        "name": "Materia 1",
        "description": "Materia de ejemplo",
        "difficulty": DifficultyLevel.MEDIUM
    }

    response = client.post(
        "/subjects",
        headers={"Authorization": f"Bearer {token}"},
        json=data
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["owner_id"] == user["id"]
    assert response.json()["difficulty"] == DifficultyLevel.MEDIUM.value
    assert response.json()["difficulty_label"] == DifficultyLevel.MEDIUM.label


def test_should_return_401_if_not_authenticated(client):
    response = client.post("/subjects", json={
            "name": "Test",
            "difficulty": DifficultyLevel.MEDIUM
    })

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_should_return_409_if_subject_name_already_exists(client, user_login, create_subject):
    token = user_login["access_token"]

    response_1 = create_subject(token, None)

    data = {
        "name": "Materia 1",
        "description": "Materia de ejemplo",
        "difficulty": DifficultyLevel.MEDIUM
    }

    response_2 = client.post(
        "/subjects",
        headers={"Authorization": f"Bearer {token}"},
        json=data
    )

    assert response_2.status_code == status.HTTP_409_CONFLICT

def test_should_return_422_if_missing_name(client, user_login):
    token = user_login["access_token"]

    data = {
        "description": "Materia sin nombre",
        "difficulty": DifficultyLevel.MEDIUM
    }

    response = client.post(
        "/subjects",
        headers={"Authorization": f"Bearer {token}"},
        json=data
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

def test_should_allow_same_subject_name_for_different_users(
    create_user, login_user, create_subject
):
    user1 = create_user("user1@gmail.com")
    user2 = create_user("user2@gmail.com")

    token1 = login_user(user1["email"], user1["raw_password"])
    token2 = login_user(user2["email"], user2["raw_password"])

    data = {
        "name": "Math",
        "description": "Test",
        "difficulty": DifficultyLevel.MEDIUM
    }

    res1 = create_subject(token1, data)
    res2 = create_subject(token2, data)

    assert res1["name"] == res2["name"]
    assert res1["owner_id"] != res2["owner_id"]