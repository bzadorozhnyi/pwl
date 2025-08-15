from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_NAME: str = "pwl_db"
    DB_USER: str = "postgres"
    DB_PASS: str = "password"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432

    @property
    def db_url(self) -> str:
        return f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


settings = Settings()
