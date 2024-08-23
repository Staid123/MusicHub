import logging

class TestAuth:
    async def test_register(self, register_user):
        assert register_user == {
            "user": {
                "user_id": 1,
                "username": "staiddd",
                "email": "user@example.com",
                "password_hash": "1234"
            }
        }

    async def test_login(self, login_user):
        assert all(token in login_user for token in ["access_token", "token_type", "refresh_token"]) 

    async def test_create_new_access_token(self, login_user, ac):
        response = await ac.post(
            url="/jwt/auth/refresh/",
            headers={"Authorization": f"Bearer {login_user['refresh_token']}"}
        )
        assert response.status_code == 201
        assert all(field in response.json() for field in ["access_token", "token_type"])
        logging.info("Test 'create_new_access_token' was successful")