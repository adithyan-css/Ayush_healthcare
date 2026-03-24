from pydantic_settings import BaseSettings
class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"
    REDIS_URL: str = "redis://localhost:6379/0"
    JWT_SECRET: str = "secret"
    CLAUDE_API_KEY: str = ""
    class Config:
        env_file = ".env"
settings = Settings()
