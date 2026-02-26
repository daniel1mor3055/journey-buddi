import pytest

from app.auth import create_magic_link_token, verify_magic_link_token, create_access_token, decode_access_token


@pytest.mark.asyncio
async def test_magic_link_request(client, test_email):
    response = await client.post("/api/v1/auth/magic-link", json={"email": test_email})
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Magic link sent"
    assert data["expires_in"] == 900


@pytest.mark.asyncio
async def test_magic_link_invalid_email(client):
    response = await client.post("/api/v1/auth/magic-link", json={"email": "not-an-email"})
    assert response.status_code == 422


def test_create_and_verify_magic_link_token():
    email = "test@example.com"
    token = create_magic_link_token(email)
    result = verify_magic_link_token(token)
    assert result == email


def test_verify_invalid_magic_link_token():
    result = verify_magic_link_token("invalid-token")
    assert result is None


def test_create_and_decode_access_token():
    user_id = "test-user-id"
    token = create_access_token(user_id)
    result = decode_access_token(token)
    assert result == user_id


def test_decode_invalid_access_token():
    result = decode_access_token("invalid-token")
    assert result is None
