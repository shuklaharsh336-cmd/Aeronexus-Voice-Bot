from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    host: str = "0.0.0.0"
    port: int = 8000

    vonage_api_key: str | None = None
    vonage_api_secret: str | None = None
    gemini_api_key: str | None = None
    
    vonage_application_id: str = ""
    vonage_private_key_path: str = ""
    vonage_number: str = ""
    
    log_level: str = "INFO"
    
    ngrok_url: str = "" # Used to construct webhook URLs if behind NAT
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
