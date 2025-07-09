import pytest
from httpx import AsyncClient
from httpx import ASGITransport

from app.main import app


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "username_suffix, email, phone_number, expected_status",
    [
        ("1", "test1@example.com", "0812345678", 200),
        ("2", "test2@example.com", None, 200),
        ("3", None, "0812345679", 200),
    ],
)
async def test_register_success_multiple_cases(
    prepare_database, username_suffix, email, phone_number, expected_status
):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        username = f"testuser{username_suffix}"
        password = "securepass123"

        payload = {
            "username": username,
            "full_name": "Full Name",
            "password": password,
        }
        if email is not None:
            payload["email"] = email
        if phone_number is not None:
            payload["phone_number"] = phone_number

        response = await client.post("/api/auth/register", json=payload)

        assert response.status_code == expected_status

        if response.status_code == 200:
            data = response.json()
            assert data["username"] == username
            assert data["full_name"] == "Full Name"
            assert data["is_active"] is True
            assert "id" in data
            assert "created_at" in data
            assert "updated_at" in data

            if email is not None:
                assert data["email"] == email
            else:
                assert data.get("email") is None

            if phone_number is not None:
                assert data["phone_number"] == phone_number
            else:
                assert data.get("phone_number") is None


@pytest.mark.asyncio
async def test_register_username_taken(prepare_database):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        await client.post(
            "/api/auth/register",
            json={
                "username": "takenusername",
                "email": "first@example.com",
                "phone_number": "0000000001",
                "full_name": "Full Name",
                "password": "pass",
            },
        )
        response = await client.post(
            "/api/auth/register",
            json={
                "username": "takenusername",
                "email": "second@example.com",
                "phone_number": "0000000002",
                "full_name": "Full Name",
                "password": "pass",
            },
        )
        assert response.status_code == 409
        assert response.json()["detail"] == "Username already taken"


@pytest.mark.asyncio
async def test_register_email_taken(prepare_database):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        await client.post(
            "/api/auth/register",
            json={
                "username": "userforemail",
                "email": "taken@example.com",
                "phone_number": "0000000003",
                "full_name": "Full Name",
                "password": "pass",
            },
        )
        response = await client.post(
            "/api/auth/register",
            json={
                "username": "anotheruser",
                "email": "taken@example.com",
                "phone_number": "0000000004",
                "full_name": "Full Name",
                "password": "pass",
            },
        )
        assert response.status_code == 409
        assert response.json()["detail"] == "Email already registered"


@pytest.mark.asyncio
async def test_register_phone_number_taken(prepare_database):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        await client.post(
            "/api/auth/register",
            json={
                "username": "userforphone",
                "email": "phone@example.com",
                "phone_number": "0811111111",
                "full_name": "Full Name",
                "password": "pass",
            },
        )
        response = await client.post(
            "/api/auth/register",
            json={
                "username": "yetanotheruser",
                "email": "yetanother@example.com",
                "phone_number": "0811111111",
                "full_name": "Full Name",
                "password": "pass",
            },
        )
        assert response.status_code == 409
        assert response.json()["detail"] == "Phone number already registered"


@pytest.mark.asyncio
async def test_register_missing_email_and_phone(prepare_database):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/api/auth/register",
            json={
                "username": "nouserinfo",
                "full_name": "No Contact Info",
                "password": "pass",
            },
        )
        assert response.status_code == 422
        assert "Either email or phone_number must be provided." in response.text


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "username",
    [
        "UPPERCASE",
        "user name",
        "user-name",
        "user.name",
        "emoji😀",
        "name!",
    ],
)
async def test_register_invalid_username_format(username, prepare_database):

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:

        response = await client.post(
            "/api/auth/register",
            json={
                "username": username,
                "email": "valid@example.com",
                "full_name": "Full Name",
                "password": "pass",
            },
        )
        assert response.status_code == 422
        assert "Username must contain only lowercase letters and numbers" in response.text


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "email",
    [
        "email",
        # ! Pydantic อนุญาติ 2 รูปแบบนี้
        # ! "emoji😀@example.com",
        # ! "name!@domain.com",
        "invalid-email",
        "user@.com",
        "@domain.com",
        "user@domain",
        "user@",
    ],
)
async def test_register_invalid_email_format(email, prepare_database):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/api/auth/register",
            json={
                "username": "validusername",
                "email": email,
                "full_name": "Full Name",
                "password": "securepass",
            },
        )
        assert response.status_code == 422


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "phone",
    [
        "123 456 789",
        "+66812345678",
        "abcdefghijk",
        "123",
        "1234567890123456789012",
    ],
)
async def test_register_invalid_phone_number_format(phone, prepare_database):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/api/auth/register",
            json={
                "username": "validuser",
                "email": "valid@example.com",
                "phone_number": phone,
                "full_name": "Full Name",
                "password": "securepass",
            },
        )
        assert response.status_code == 422
        assert "Phone number must contain digits only" in response.text
