import pytest
from fastapi import status
from httpx import AsyncClient
from httpx import ASGITransport

from app.main import app
from app.models import User, UserTypeEnum
from app.security import (
    get_password_hash,
)
from app.tests.conftest import TestingSessionLocal


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "username",
    [
        ("test.login.email@example.com",),  # * Email
        ("0812345678",),  # * Phone number
        ("0123456789123",),  # * Citizen id
    ],
)
async def test_login_success_multiple_cases(prepare_database, username):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        password = "TestPassword"
        password_hash = get_password_hash(password)
        user_obj = User(
            email="test.login.email@example.com",
            phone_number="0812345678",
            citizen_id="0123456789123",
            first_name_th="ชื่อภาษาไทย",
            last_name_th="นามสกุลภาษาไทย",
            user_type=UserTypeEnum.TOURIST.value,
            agreed_to_terms=True,
            password_hash=password_hash,
        )

        async with TestingSessionLocal() as session:
            session.add(user_obj)
            await session.commit()
            await session.refresh(user_obj)

        response = await client.post(
            "/api/auth/login",
            data={"username": username, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert "refresh_token" in response.json()


@pytest.mark.asyncio
async def test_login_incorrect_password(prepare_database):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        password = "correctpassword"
        password_hash = get_password_hash(password)
        user_obj = User(
            email="wrongpass@example.com",
            phone_number="0812345678",
            citizen_id="0123456789123",
            first_name_th="ชื่อภาษาไทย",
            last_name_th="นามสกุลภาษาไทย",
            user_type=UserTypeEnum.TOURIST.value,
            agreed_to_terms=True,
            password_hash=password_hash,
        )
        async with TestingSessionLocal() as session:
            session.add(user_obj)
            await session.commit()
            await session.refresh(user_obj)

        response = await client.post(
            "/api/auth/login",
            data={"username": "wrongpass", "password": "incorrectpassword"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Incorrect email, phone number, citizen id or password"


@pytest.mark.asyncio
async def test_login_user_not_found(prepare_database):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/api/auth/login",
            data={"username": "nonexistentuser", "password": "anypassword"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Incorrect email, phone number, citizen id or password"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "username",
    [
        ("Mixed.Case.Email@Example.Com",),  # * Email
    ],
)
async def test_login_case_insensitivity(prepare_database, username):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        password = "TestPassword"
        password_hash = get_password_hash(password)
        user_obj = User(
            email="mixed.case.email@example.com",
            phone_number="0812345678",
            citizen_id="0123456789123",
            first_name_th="ชื่อภาษาไทย",
            last_name_th="นามสกุลภาษาไทย",
            user_type=UserTypeEnum.TOURIST.value,
            agreed_to_terms=True,
            password_hash=password_hash,
        )

        async with TestingSessionLocal() as session:
            session.add(user_obj)
            await session.commit()
            await session.refresh(user_obj)

        response = await client.post(
            "/api/auth/login",
            data={
                "username": username,
                "password": password,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert "refresh_token" in response.json()
