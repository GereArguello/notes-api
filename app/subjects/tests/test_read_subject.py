from fastapi import status


## TESTS PARA LISTA DE MATERIAS 

def test_subject_list_should_return_200(client, user_login, create_subject):
    token = user_login["access_token"]

    create_subject(token)

    response = client.get(
        "/subjects?page=1&size=10",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_200_OK

    body = response.json()

    assert "items" in body
    assert "total" in body
    assert "page" in body
    assert "size" in body

    assert len(body["items"]) == 1
    assert body["items"][0]["owner_id"] == user_login["user"]["id"]

def test_should_return_subjects_ordered_by_created_at_asc(client, user_login, create_subject):
    token = user_login["access_token"]

    for i in range(2, 12):
        create_subject(token, name= f"materia {i}")

    response = client.get(
        "/subjects?page=1&size=10&order=asc",
        headers={"Authorization": f"Bearer {token}"}
    )

    body = response.json()
    assert len(body["items"]) == 10
    assert body["items"][0]["name"] == "materia 2"
    assert body["items"][9]["name"] == "materia 11"


def test_should_return_subjects_ordered_by_created_at_desc(client, user_login, create_subject):
    token = user_login["access_token"]

    for i in range(2, 12):
        create_subject(token, name= f"materia {i}")

    response = client.get(
        "/subjects?page=1&size=10",
        headers={"Authorization": f"Bearer {token}"}
    )

    body = response.json()
    assert len(body["items"]) == 10
    assert body["items"][0]["name"] == "materia 11"
    assert body["items"][9]["name"] == "materia 2"

def test_should_return_empty_list_when_page_out_of_range(client, user_login, create_subject):
    token = user_login["access_token"]

    create_subject(token)

    response = client.get(
        "/subjects?page=2&size=10",
        headers={"Authorization": f"Bearer {token}"}
    )

    body = response.json()

    assert response.status_code == 200
    assert body["items"] == []

def test_should_respect_page_size(client, user_login, create_subject):
    token = user_login["access_token"]

    for i in range(5):
        create_subject(token, name=f"materia {i}")

    response = client.get(
        "/subjects?page=1&size=3",
        headers={"Authorization": f"Bearer {token}"}
    )

    body = response.json()

    assert len(body["items"]) == 3

def test_should_return_only_current_user_subjects(
    client, user_login, create_subject, create_user
):
    token = user_login["access_token"]

    # subject del user actual
    create_subject(token)

    # crear otro usuario
    user2 = create_user(email="test2@gmail.com")

    # login del segundo usuario
    login_response = client.post(
        "/auth/login",
        data={
            "username": "test2@gmail.com",
            "password": user2["raw_password"]
        }
    )

    other_token = login_response.json()["access_token"]

    # crear subject del otro usuario
    create_subject(other_token, name="materia ajena")

    response = client.get(
        "/subjects",
        headers={"Authorization": f"Bearer {token}"}
    )

    body = response.json()

    assert len(body["items"]) == 1
    assert body["items"][0]["name"] != "materia ajena"

def test_should_fail_without_token(client):
    response = client.get("/subjects")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

## TESTS PARA LEER 1 (UNA) MATERIA

def test_read_subject_should_return_200(client, user_login, create_subject):
    token = user_login["access_token"]
    subject = create_subject(token)

    response = client.get(
        f"/subjects/{subject["id"]}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_200_OK

    body = response.json()

    assert body["id"] == subject["id"]
    assert body["name"] == subject["name"]

def test_should_return_404_if_subject_not_foundh(client, user_login, create_subject):
    token = user_login["access_token"]
    subject = create_subject(token)

    response = client.get(
        "/subjects/9999",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "La materia no existe"

def test_should_return_404_if_user_tries_to_access_other_user_subject(
    client, user_login, create_subject
):
    token_user1 = user_login["access_token"]
    subject = create_subject(token_user1)

    # Crear segundo usuario
    user_data = {
        "first_name": "Juan",
        "last_name": "Perez",
        "email": "otro@example.com",
        "password": "12345678",
        "password2": "12345678"
    }

    client.post("/users/", json=user_data)

    # Login segundo usuario
    login_response = client.post("/auth/login", data={
        "username": user_data["email"],
        "password": user_data["password"]
    })

    token_user2 = login_response.json()["access_token"]

    response = client.get(
        f"/subjects/{subject['id']}",
        headers={"Authorization": f"Bearer {token_user2}"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND