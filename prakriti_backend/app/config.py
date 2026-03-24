from pydantic_settings import BaseSettings


class Settings(BaseSettings):
	DATABASE_URL: str = 'sqlite+aiosqlite:///./test.db'
	REDIS_URL: str = 'redis://localhost:6379/0'
	JWT_SECRET: str = 'REPLACE_WITH_32_CHAR_RANDOM_STRING'
	GOOGLE_API_KEY: str = ''
	OPENWEATHER_API_KEY: str = ''

	class Config:
		env_file = '.env'


settings = Settings()
