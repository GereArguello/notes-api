from fastapi import status

def test_list_tags_should_return_200(client, user_with_tag):
    token = user_with_tag["access_token"]

    response = client.get(
        "/tags",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_200_OK

    body = response.json()

    # es lista
    assert isinstance(body, list)

    # al menos 1 tag
    assert len(body) == 1

    # estructura básica
    assert "id" in body[0]
    assert "name" in body[0]

def test_list_tags_should_return_only_user_tags(
    client, user_with_tag, create_user, login_user
):
    # user 1 (con tags)
    token_1 = user_with_tag["access_token"]

    response_1 = client.get(
        "/tags",
        headers={"Authorization": f"Bearer {token_1}"}
    )

    assert response_1.status_code == status.HTTP_200_OK

    body1 = response_1.json()
    assert len(body1) == 1

    # user 2 (sin tags)
    user_2 = create_user(email="ejemplo@ejemplo.com")
    token_2 = login_user(user_2["email"], user_2["raw_password"])

    response_2 = client.get(
        "/tags",
        headers={"Authorization": f"Bearer {token_2}"}
    )

    assert response_2.status_code == status.HTTP_200_OK

    body2 = response_2.json()
    assert body2 == []  

def test_list_tags_should_filter_by_search(client, user_with_tag):
    token = user_with_tag["access_token"]

    response = client.get(
        "/tags?search=py",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_200_OK

    body = response.json()

    assert len(body) == 1
    assert "py" in body[0]["name"]
    assert body[0]["name"] == "python"