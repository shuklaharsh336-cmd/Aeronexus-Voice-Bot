import pytest
from unittest.mock import patch, mock_open, AsyncMock
from src.services.vonage_service import VonageService
from src.config import Settings
import httpx

@pytest.fixture
def mock_service():
    with patch("src.services.vonage_service.get_settings") as mock_get_settings:
        mock_get_settings.return_value = Settings(
            vonage_application_id="test_app_id",
            vonage_private_key_path="test_private.key",
            vonage_number="1234567890",
            ngrok_url="http://test.ngrok.io"
        )
        yield VonageService()

def test_generate_jwt(mock_service):
    mock_key = b"-----BEGIN PRIVATE KEY-----\nMOCKKEY\n-----END PRIVATE KEY-----"
    
    with patch("builtins.open", mock_open(read_data=mock_key)):
        with patch("jwt.encode") as mock_jwt_encode:
            mock_jwt_encode.return_value = "mock_token"
            token = mock_service._generate_jwt()
            
            assert token == "mock_token"
            mock_jwt_encode.assert_called_once()
            args, kwargs = mock_jwt_encode.call_args
            
            assert args[1] == mock_key
            assert kwargs["algorithm"] == "RS256"
            payload = args[0]
            assert payload["application_id"] == "test_app_id"
            assert "iat" in payload
            assert "jti" in payload
            assert "exp" in payload

@pytest.mark.asyncio
async def test_create_outbound_call_success(mock_service):
    from unittest.mock import MagicMock
    with patch.object(mock_service, "_generate_jwt", return_value="mock_token"):
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"uuid": "mock-uuid"}
        
        with patch("httpx.AsyncClient.post", return_value=mock_response) as mock_post:
            data = await mock_service.create_outbound_call("14155550100")
            
            assert data["uuid"] == "mock-uuid"
            mock_post.assert_called_once()
            
            args, kwargs = mock_post.call_args
            assert args[0] == mock_service.base_url
            assert kwargs["headers"]["Authorization"] == "Bearer mock_token"
            assert kwargs["json"]["to"][0]["number"] == "14155550100"
            assert kwargs["json"]["from"]["number"] == "1234567890"

@pytest.mark.asyncio
async def test_create_outbound_call_failure(mock_service):
    from unittest.mock import MagicMock
    with patch.object(mock_service, "_generate_jwt", return_value="mock_token"):
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        
        error = httpx.HTTPStatusError("Unauthorized", request=AsyncMock(), response=mock_response)
        
        with patch("httpx.AsyncClient.post", side_effect=error):
            with pytest.raises(Exception, match="Failed to create call: Unauthorized"):
                await mock_service.create_outbound_call("14155550100")
