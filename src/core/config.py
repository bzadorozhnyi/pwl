from pydantic_ai.models import KnownModelName as AgentKnownModelName
from pydantic_settings import BaseSettings, SettingsConfigDict

from enums.mail_backend import MailBackend


class Settings(BaseSettings):
    DB_NAME: str = "pwl_db"
    DB_USER: str = "postgres"
    DB_PASS: str = "password"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    VERIFY_TOKEN_EXPIRE_HOURS: int = 1
    UI_URL_PROTOCOL: str = "http://"
    BASE_UI_DOMAIN: str = "localhost:3000"
    ADMIN_PANEL_SECRET_KEY: str = "admin_panel_secret"
    AGENT_MODEL: AgentKnownModelName = "openai:gpt-4.1-mini"
    AGENT_API_KEY: str

    # Email settings
    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_FROM: str = "no-reply@example.com"
    MAIL_PORT: int = 1025
    MAIL_SERVER: str = "localhost"
    MAIL_STARTTLS: bool = False
    MAIL_SSL_TLS: bool = False
    MAIL_USE_CREDENTIALS: bool = False
    MAIL_BACKEND: MailBackend = MailBackend.CONSOLE

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def db_url(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def test_db_url(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/testing_{self.DB_NAME}"


settings = Settings()
