import logging


async def test_auth_user_check_self_info(ac, login_user):
    headers = {"Authorization": f"Bearer {login_user['access_token']}"}
    response = await ac.get(
        url="/jwt/users/me/",
        headers=headers
    )
    response_json = response.json()
    assert "logged_in_at" and "password_hash" in response_json
    assert response_json["id"] == 1
    assert response_json["role"] == "admin"
    assert response_json["username"] == "staiddd"
    assert response_json["email"] == "user@example.com"

    logging.info("Test 'auth_user_check_self_info' was successful")


async def test_get_list_users(ac, login_user):
    headers = {"Authorization": f"Bearer {login_user['access_token']}"}
    response = await ac.get(
        url="/jwt/users/all/",
        headers=headers
    )
    response_json = response.json()[0]
    assert response_json["id"] == 1
    assert response_json["role"] == "admin"
    assert response_json["username"] == "staiddd"
    assert response_json["email"] == "user@example.com"
    assert response_json["active"] == True
    assert response_json["albums"] == []

    logging.info("Test 'get_list_users' was successful")


async def test_delete_account(ac, login_user):
    headers = {"Authorization": f"Bearer {login_user['access_token']}"}
    response = await ac.delete(
        url="/jwt/users/delete/account/",
        headers=headers
    )
    assert response.status_code == 204
    logging.info("Test 'delete_account' was successful")