import pytest
from fastapi.testclient import TestClient
from main import app
from src.config import get_settings, Settings
import os

@pytest.fixture
def test_app():
    return app

@pytest.fixture
def client(test_app):
    return TestClient(test_app)

@pytest.fixture
def mock_settings():
    def get_mock_settings():
        return Settings(
            vonage_application_id="test_app_id",
            vonage_private_key_path="test_private.key",
            vonage_number="1234567890",
            ngrok_url="http://test.ngrok.io"
        )
    app.dependency_overrides[get_settings] = get_mock_settings
    yield
    app.dependency_overrides.clear()
