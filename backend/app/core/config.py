from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Interview Coach API"
    api_v1_str: str = "/api"
    secret_key: str
    access_token_expire_minutes: int = 1440
    database_url: str
    frontend_url: str = "http://localhost:3000"
    nlp_service_url: str = Field(
        default="http://localhost:8101",
        validation_alias=AliasChoices("NLP_SERVICE_URL", "ML_NLP_SERVICE_URL"),
    )
    vision_service_url: str = Field(
        default="http://localhost:8102",
        validation_alias=AliasChoices("VISION_SERVICE_URL", "ML_VISION_SERVICE_URL"),
    )
    emotion_service_url: str = Field(
        default="http://localhost:8103",
        validation_alias=AliasChoices("EMOTION_SERVICE_URL", "ML_EMOTION_SERVICE_URL"),
    )
    speech_service_url: str = Field(
        default="http://localhost:8104",
        validation_alias=AliasChoices("SPEECH_SERVICE_URL", "ML_SPEECH_SERVICE_URL"),
    )
    backend_base_url: str = "http://localhost:8000"
    google_client_id: str | None = None
    google_client_secret: str | None = None
    github_client_id: str | None = None
    github_client_secret: str | None = None
    aws_region: str | None = None
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    s3_bucket: str | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
