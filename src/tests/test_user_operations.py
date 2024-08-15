import logging
from httpx import AsyncClient
from conftest import client
from auth.schemas import TokenInfo


def test_delete_account(login_user: TokenInfo):
    headers = {"Authorization": f"Bearer {login_user['access_token']}"}
    response = client.request(
        method="DELETE",
        url="/jwt/users/delete/account/",
        headers=headers
    )
    assert response.status_code == 204
    logging.info("Test 'delete_account' was successful")