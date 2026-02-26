import pytest


@pytest.mark.asyncio
async def test_list_trips_requires_auth(client):
    response = await client.get("/api/v1/trips")
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_create_trip_requires_auth(client):
    response = await client.post(
        "/api/v1/trips",
        json={"destination": "new-zealand"},
    )
    assert response.status_code in (401, 403)
