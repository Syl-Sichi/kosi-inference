from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ollama_base_url: str = "http://127.0.0.1:11434"
    kosi_model: str = "kosi"
    kosi_api_key: str | None = None
    request_timeout_s: float = 120.0


settings = Settings()
