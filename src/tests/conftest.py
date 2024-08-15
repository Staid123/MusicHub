import asyncio
from http.client import HTTPException
import logging
from typing import AsyncGenerator

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from auth.schemas import TokenInfo
from database import db_helper
from config import settings
from database.models import Base
from main import app

# DATABASE
DATABASE_URL_TEST = settings.db_test.url

engine_test = create_async_engine(DATABASE_URL_TEST, poolclass=NullPool)
async_session_maker = async_sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)
Base.metadata.bind = engine_test

async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

app.dependency_overrides[db_helper.session_getter] = override_get_async_session

@pytest.fixture(autouse=True, scope='session')
async def prepare_database():
    async with engine_test.begin() as conn:
        logging.info("DELETING DATABASE")
        await conn.run_sync(Base.metadata.drop_all)
    async with engine_test.begin() as conn:
        logging.info("CREATING DATABASE")
        await conn.run_sync(Base.metadata.create_all)
    yield
    # async with engine_test.begin() as conn:
    #     logging.info("DELETING DATABASE")
    #     await conn.run_sync(Base.metadata.drop_all)

client = TestClient(app)

@pytest.fixture(scope="session")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac

@pytest.fixture(scope="session")
def register_user():
    response = client.post(
        url="/jwt/auth/signup/",
        json={
            "username": "staiddd",
            "email": "user@example.com",
            "password_hash": "1234"
        }
    )
    assert response.status_code == 201
    logging.info("REGISTERED USER ID: %s", response.json()['user']['user_id'])
    return response.json()


@pytest.fixture(scope="function")
def login_user(register_user):
    response = client.post(
        url="/jwt/auth/login/",
        data={
            "username": register_user["user"]["email"],
            "password": "1234"
        }
    )
    assert response.status_code == 200
    return response.json()