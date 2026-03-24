from pydantic_settings import BaseSettings


class Settings(BaseSettings):
	DATABASE_URL: str = 'sqlite+aiosqlite:///./test.db'
	REDIS_URL: str = 'redis://localhost:6379/0'
	JWT_SECRET: str = 'changeme-32chars'
	JWT_ALGORITHM: str = 'HS256'
	ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
	REFRESH_TOKEN_EXPIRE_DAYS: int = 30
	ANTHROPIC_API_KEY: str = ''
	CLAUDE_MODEL: str = 'claude-3-5-sonnet-latest'
	GOOGLE_API_KEY: str = ''
	OPENWEATHER_API_KEY: str = ''
	TWITTER_BEARER_TOKEN: str = ''
	ENVIRONMENT: str = 'development'
	CORS_ORIGINS: str = 'http://localhost:3000'

	@property
	def is_production(self) -> bool:
		return self.ENVIRONMENT.lower() == 'production'

	@property
	def cors_origins_list(self) -> list[str]:
		return [origin.strip() for origin in self.CORS_ORIGINS.split(',') if origin.strip()]

	class Config:
		env_file = '.env'


settings = Settings()
