from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # --- App ---
    APP_NAME: str = "AI Resume Analyzer"
    DEBUG: bool = True

    # --- Database (MySQL) ---
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = "admin"
    DB_NAME: str = "resume_analyzer"

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    # --- LLM (filled in later step) ---
    LLM_API_KEY: str = "ollama"

    class Config:
        env_file = ".env"


settings = Settings()
