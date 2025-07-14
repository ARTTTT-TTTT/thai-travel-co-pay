import pytest
from fastapi import status
from httpx import AsyncClient
from httpx import ASGITransport

from app.main import app
from app.models import UserTypeEnum


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "email, phone_number, citizen_id, user_type",
    [
        ("test1@example.com", "0812345678", "0123456789123", UserTypeEnum.TOURIST.value),
        ("test2@example.com", "0823456789", "1234567890123", UserTypeEnum.OPERATOR.value),
        ("test3@example.com", "1234567", "0123456789124", UserTypeEnum.TOURIST.value),
        ("test4@example.com", "123456789012345", "1234567890125", UserTypeEnum.OPERATOR.value),
    ],
)
async def test_register_success_multiple_cases(
    prepare_database, email, phone_number, citizen_id, user_type
):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:

        response = await client.post(
            "/api/auth/register",
            json={
                "email": email,
                "phone_number": phone_number,
                "citizen_id": citizen_id,
                "first_name_th": "ชื่อภาษาไทย",
                "last_name_th": "นามสกุลภาษาไทย",
                "user_type": user_type,
                "agreed_to_terms": True,
                "password": "password",
            },
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == email
        assert data["phone_number"] == phone_number
        assert data["citizen_id"] == citizen_id
        assert data["first_name_th"] == "ชื่อภาษาไทย"
        assert data["last_name_th"] == "นามสกุลภาษาไทย"
        assert data["agreed_to_terms"] is True
        assert data["is_active"] is True
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

        if user_type is UserTypeEnum.TOURIST.value:
            assert data["user_type"] == UserTypeEnum.TOURIST.value
        else:
            assert data["user_type"] == UserTypeEnum.OPERATOR.value


@pytest.mark.asyncio
async def test_register_email_taken(prepare_database):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        await client.post(
            "/api/auth/register",
            json={
                "email": "taken@example.com",
                "phone_number": "0123456789",
                "citizen_id": "0123456789123",
                "first_name_th": "ชื่อภาษาไทย",
                "last_name_th": "นามสกุลภาษาไทย",
                "user_type": UserTypeEnum.OPERATOR.value,
                "agreed_to_terms": True,
                "password": "password",
            },
        )
        response = await client.post(
            "/api/auth/register",
            json={
                "email": "taken@example.com",
                "phone_number": "1234567890",
                "citizen_id": "1234567891230",
                "first_name_th": "ชื่อภาษาไทย",
                "last_name_th": "นามสกุลภาษาไทย",
                "user_type": UserTypeEnum.OPERATOR.value,
                "agreed_to_terms": True,
                "password": "password",
            },
        )
        assert response.status_code == status.HTTP_409_CONFLICT
        assert response.json()["detail"] == "Email already registered"


@pytest.mark.asyncio
async def test_register_phone_number_taken(prepare_database):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        await client.post(
            "/api/auth/register",
            json={
                "email": "first@example.com",
                "phone_number": "0123456789",
                "citizen_id": "0123456789123",
                "first_name_th": "ชื่อภาษาไทย",
                "last_name_th": "นามสกุลภาษาไทย",
                "user_type": UserTypeEnum.OPERATOR.value,
                "agreed_to_terms": True,
                "password": "password",
            },
        )
        response = await client.post(
            "/api/auth/register",
            json={
                "email": "second@example.com",
                "phone_number": "0123456789",
                "citizen_id": "1234567891230",
                "first_name_th": "ชื่อภาษาไทย",
                "last_name_th": "นามสกุลภาษาไทย",
                "user_type": UserTypeEnum.OPERATOR.value,
                "agreed_to_terms": True,
                "password": "password",
            },
        )
        assert response.status_code == status.HTTP_409_CONFLICT
        assert response.json()["detail"] == "Phone number already registered"


@pytest.mark.asyncio
async def test_register_citizen_id_taken(prepare_database):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        await client.post(
            "/api/auth/register",
            json={
                "email": "first@example.com",
                "phone_number": "0123456789",
                "citizen_id": "0123456789123",
                "first_name_th": "ชื่อภาษาไทย",
                "last_name_th": "นามสกุลภาษาไทย",
                "user_type": UserTypeEnum.OPERATOR.value,
                "agreed_to_terms": True,
                "password": "password",
            },
        )
        response = await client.post(
            "/api/auth/register",
            json={
                "email": "second@example.com",
                "phone_number": "1234567890",
                "citizen_id": "0123456789123",
                "first_name_th": "ชื่อภาษาไทย",
                "last_name_th": "นามสกุลภาษาไทย",
                "user_type": UserTypeEnum.OPERATOR.value,
                "agreed_to_terms": True,
                "password": "password",
            },
        )
        assert response.status_code == status.HTTP_409_CONFLICT
        assert response.json()["detail"] == "Citizen id already registered"


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
        1,
        "",
    ],
)
async def test_register_invalid_email_format(prepare_database, email):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/api/auth/register",
            json={
                "email": email,
                "phone_number": "0123456789",
                "citizen_id": "0123456789123",
                "first_name_th": "ชื่อภาษาไทย",
                "last_name_th": "นามสกุลภาษาไทย",
                "user_type": UserTypeEnum.OPERATOR.value,
                "agreed_to_terms": True,
                "password": "password",
            },
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "phone",
    ["123 456 789", "+66812345678", "abcdefghijk", "123456", "1234567890123456", 1, ""],
)
async def test_register_invalid_phone_number_format(phone, prepare_database):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/api/auth/register",
            json={
                "email": "validphone@example.com",
                "phone_number": phone,
                "citizen_id": "0123456789123",
                "first_name_th": "ชื่อภาษาไทย",
                "last_name_th": "นามสกุลภาษาไทย",
                "user_type": UserTypeEnum.OPERATOR.value,
                "agreed_to_terms": True,
                "password": "password",
            },
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        # assert "Phone number must contain digits only" in response.text


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "citizen_id",
    ["123 456 789", "+66812345678", "abcdefghijk", "123456", "1234567890123456", 1, ""],
)
async def test_register_invalid_citizen_id_format(citizen_id, prepare_database):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/api/auth/register",
            json={
                "email": "validphone@example.com",
                "phone_number": "0123456789",
                "citizen_id": citizen_id,
                "first_name_th": "ชื่อภาษาไทย",
                "last_name_th": "นามสกุลภาษาไทย",
                "user_type": UserTypeEnum.OPERATOR.value,
                "agreed_to_terms": True,
                "password": "password",
            },
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        # assert "Citizen id must contain digits only" in response.text


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "first_name_th",
    ["John", "ชื่อ123", "ชื่อ*", "ชื่อ ภาษาไทย", 1, "", " "],
)
async def test_register_invalid_first_name_th(first_name_th, prepare_database):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/api/auth/register",
            json={
                "email": "valid@example.com",
                "phone_number": "0123456789",
                "citizen_id": "1234567890123",
                "first_name_th": first_name_th,
                "last_name_th": "นามสกุล",
                "user_type": UserTypeEnum.OPERATOR.value,
                "agreed_to_terms": True,
                "password": "password",
            },
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        # assert "First name (TH) must contain only Thai characters (no spaces, numbers, or symbols) and be 1-50 characters long." in response.text


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "last_name_th",
    ["Smith", "นาม123", "นาม*", "นาม สกุล", 1, "", " "],
)
async def test_register_invalid_last_name_th(last_name_th, prepare_database):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/api/auth/register",
            json={
                "email": "valid@example.com",
                "phone_number": "0123456789",
                "citizen_id": "1234567890123",
                "first_name_th": "ชื่อ",
                "last_name_th": last_name_th,
                "user_type": UserTypeEnum.OPERATOR.value,
                "agreed_to_terms": True,
                "password": "password",
            },
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        # assert "Last name (TH) must contain only Thai characters (no spaces, numbers, or symbols) and be 1-50 characters long." in response.text
