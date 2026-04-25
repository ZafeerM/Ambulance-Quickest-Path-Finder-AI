from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Seconds between each A* step sent over the WebSocket
    step_delay_seconds: float = 0.1

    # Allowed CORS origins — use JSON array format in .env:
    # CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]
    cors_origins: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
