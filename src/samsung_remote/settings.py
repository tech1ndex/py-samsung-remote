from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE, env_prefix="TV_")

    host: str = "10.0.0.2"
    port: int = 8001
    server_host: str = "0.0.0.0"
    server_port: int = 5001


settings = Settings()
