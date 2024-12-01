import sys
import os
import pytest
from httpx import AsyncClient
from contacts_api.app.main import app
from app.crud import create_access_token
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "C:/Users/Alex/Desktop/contacts_api")))

@pytest.fixture
async def test_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
def test_token():
    return create_access_token(data={"sub": "test@example.com"})