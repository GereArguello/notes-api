from fastapi import status

def test_should_fail_if_passwords_dont_match(client):
    data = {
        "first_name": "Pedro",
        "last_name": "Sanchez",
        "email": "test@example.com",
        "password": "12345678",
        "password2": "87654321"
    }

    response = client.post("/users/", json=data)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert response.json()["detail"] == "Las contraseñas no coinciden"

def test_should_fail_if_email_already_exists(client, create_user):
    user = create_user("test@example.com")
    data = {
        "first_name": "Pepe",
        "last_name": "Sanchez",
        "email": user["email"],
        "password": "12345678",
        "password2": "12345678"
    }


    response = client.post("/users/", json=data)

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == "El email ya está registrado"

def test_should_create_user_successfully(client):
    data = {
        "first_name": "Pepe",
        "last_name": "Sanchez",
        "email": "newuser@example.com",
        "password": "12345678",
        "password2": "12345678"
    }

    response = client.post("/users/", json=data)

    assert response.status_code == status.HTTP_201_CREATED

    body = response.json()

    assert body["email"] == data["email"]
    assert body["first_name"] == data["first_name"]

    # Muy importante: asegurarse que NO devuelve el password
    assert "password" not in body
    assert "password_hash" not in body
    assert "id" in body