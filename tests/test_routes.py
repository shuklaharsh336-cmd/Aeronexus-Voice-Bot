import pytest
from unittest.mock import patch, AsyncMock
from src.services.vonage_service import VonageService
from src.api.routes import get_vonage_service
from main import app

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_answer_webhook(client):
    response = client.get("/webhooks/answer")
    assert response.status_code == 200
    ncco = response.json()
    assert isinstance(ncco, list)
    assert len(ncco) > 0
    assert ncco[0]["action"] == "talk"

def test_events_webhook(client):
    response = client.post("/webhooks/events", json={"status": "completed", "uuid": "test-uuid"})
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@pytest.mark.asyncio
async def test_make_call_success(client, mock_settings):
    # Mock the VonageService
    mock_service = AsyncMock(spec=VonageService)
    mock_service.create_outbound_call.return_value = {"uuid": "mock-call-uuid"}
    
    app.dependency_overrides[get_vonage_service] = lambda: mock_service
    
    response = client.post("/call", json={"to_number": "14155550100"})
    
    assert response.status_code == 200
    assert response.json()["call_id"] == "mock-call-uuid"
    assert response.json()["message"] == "Call initiated successfully"
    mock_service.create_outbound_call.assert_called_once_with("14155550100")
    
    app.dependency_overrides.pop(get_vonage_service, None)

@pytest.mark.asyncio
async def test_make_call_failure(client, mock_settings):
    mock_service = AsyncMock(spec=VonageService)
    mock_service.create_outbound_call.side_effect = Exception("API Error")
    
    app.dependency_overrides[get_vonage_service] = lambda: mock_service
    
    response = client.post("/call", json={"to_number": "14155550100"})
    
    assert response.status_code == 500
    assert "API Error" in response.json()["detail"]
    
    app.dependency_overrides.pop(get_vonage_service, None)
