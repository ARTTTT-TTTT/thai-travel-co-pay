import pytest
from httpx import AsyncClient
from httpx import ASGITransport

from app.main import app
from app.models import User
from app.security import (
    get_password_hash,
)
from app.tests.conftest import TestingSessionLocal


@pytest.mark.asyncio
async def test_login_success_multiple_cases(
    prepare_database,
):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        password = "TestPassword"
        hashed_password = get_password_hash(password)
        user_obj = User(
            username="testloginuser",
            email="test.login.email@example.com",
            phone_number="0812345678",
            hashed_password=hashed_password,
            full_name="Single User Test",
        )

        async with TestingSessionLocal() as session:
            session.add(user_obj)
            await session.commit()
            await session.refresh(user_obj)

        # * Username
        response_username = await client.post(
            "/api/auth/login",
            data={"username": user_obj.username, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response_username.status_code == 200
        assert "access_token" in response_username.json()

        # * Email
        response_email = await client.post(
            "/api/auth/login",
            data={"username": user_obj.email.lower(), "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response_email.status_code == 200
        assert "access_token" in response_email.json()

        # * Phone
        response_phone = await client.post(
            "/api/auth/login",
            data={"username": user_obj.phone_number, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response_phone.status_code == 200
        assert "access_token" in response_phone.json()


@pytest.mark.asyncio
async def test_login_incorrect_password(prepare_database):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        password = "correctpassword"
        hashed_pass = get_password_hash(password)
        user_obj = User(
            username="wrongpass",
            email="wrongpass@example.com",
            phone_number="08123456",
            hashed_password=hashed_pass,
            full_name="Wrong Pass User",
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
        assert response.status_code == 401
        assert response.json()["detail"] == "Incorrect username, email, phone number, or password"


@pytest.mark.asyncio
async def test_login_user_not_found(prepare_database):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/api/auth/login",
            data={"username": "nonexistentuser", "password": "anypassword"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Incorrect username, email, phone number, or password"


@pytest.mark.asyncio
async def test_login_case_insensitivity(prepare_database):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        password = "TestPassword"
        hashed_password = get_password_hash(password)
        user_obj = User(
            username="mixedcaseuser",
            email="mixed.case.email@example.com",
            phone_number="0901234567",
            hashed_password=hashed_password,
            full_name="Mixed Case Login",
        )

        async with TestingSessionLocal() as session:
            session.add(user_obj)
            await session.commit()
            await session.refresh(user_obj)

        # * Username
        response_username = await client.post(
            "/api/auth/login",
            data={"username": "MixedCaseUser", "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response_username.status_code == 200
        assert "access_token" in response_username.json()

        # * Email
        response_email = await client.post(
            "/api/auth/login",
            data={
                "username": "Mixed.Case.Email@Example.Com",
                "password": password,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response_email.status_code == 200
        assert "access_token" in response_email.json()

        # * Phone
        response_phone = await client.post(
            "/api/auth/login",
            data={"username": "0901234567", "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response_phone.status_code == 200
        assert "access_token" in response_phone.json()
