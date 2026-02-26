import asyncio
import uuid

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.auth import create_access_token, create_magic_link_token
from app.main import app
from app.config import get_settings

settings = get_settings()


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def test_email():
    return f"test-{uuid.uuid4().hex[:8]}@example.com"


@pytest.fixture
def magic_link_token(test_email):
    return create_magic_link_token(test_email)


@pytest.fixture
def auth_headers():
    user_id = str(uuid.uuid4())
    token = create_access_token(user_id)
    return {"Authorization": f"Bearer {token}"}
