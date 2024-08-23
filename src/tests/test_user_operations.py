import logging


class TestUserOperations:
    async def test_auth_user_check_self_info(self, ac, login_user):
        logging.info("Running test 'auth_user_check_self_info'")
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

    async def test_get_list_users(self, ac, login_user):
        logging.info("Running test 'get_list_users'")
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

    async def test_delete_account(self, ac, login_user):
        logging.info("Running test 'delete_account'")
        headers = {"Authorization": f"Bearer {login_user['access_token']}"}
        response = await ac.delete(
            url="/jwt/users/delete/account/",
            headers=headers
        )
        assert response.status_code == 204
        logging.info("Test 'delete_account' was successful")