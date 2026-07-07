import time
import jwt
import httpx
import uuid
import os
from typing import Dict, Any
from ..config import get_settings
from ..logger import setup_logger

logger = setup_logger(__name__)

class VonageService:
    def __init__(self):
        self.settings = get_settings()
        self.base_url = "https://api.nexmo.com/v1/calls"
        # Path resolution fix
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.key_path = os.path.join(base_dir, "private.key")

    def _generate_jwt(self) -> str:
        """Generates a JWT for authenticating with the Vonage Voice API."""
        try:
            with open(self.key_path, 'r') as key_file:
                private_key = key_file.read()
                
            payload = {
                "application_id": self.settings.vonage_application_id,
                "iat": int(time.time()),
                "jti": str(uuid.uuid4()),
                "exp": int(time.time()) + 3600,
            }
            
            token = jwt.encode(payload, private_key, algorithm="RS256")
            return token
        except FileNotFoundError:
            logger.error(f"Private key file not found at {self.key_path}")
            raise Exception("Vonage private key not found")
        except Exception as e:
            logger.error(f"Error generating JWT: {str(e)}")
            raise

    async def create_outbound_call(self, to_number: str) -> Dict[str, Any]:
        """Initiates an outbound call to the given number."""
        token = self._generate_jwt()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        answer_url = f"{self.settings.ngrok_url}/webhooks/answer" if self.settings.ngrok_url else f"http://{self.settings.host}:{self.settings.port}/webhooks/answer"
        event_url = f"{self.settings.ngrok_url}/webhooks/events" if self.settings.ngrok_url else f"http://{self.settings.host}:{self.settings.port}/webhooks/events"
        
        payload = {
            "to": [{"type": "phone", "number": to_number}],
            "from": {"type": "phone", "number": self.settings.vonage_number},
            "answer_url": [answer_url],
            "event_url": [event_url]
        }
        
        logger.info(f"Initiating call to {to_number} from {self.settings.vonage_number}")
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.base_url, headers=headers, json=payload, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                logger.info(f"Call initiated successfully. Call UUID: {data.get('uuid')}")
                return data
            except httpx.HTTPStatusError as e:
                logger.error(f"Vonage API error: {e.response.status_code} - {e.response.text}")
                raise Exception(f"Failed to create call: {e.response.text}")
            except Exception as e:
                logger.error(f"Unexpected error creating call: {str(e)}")
                raise