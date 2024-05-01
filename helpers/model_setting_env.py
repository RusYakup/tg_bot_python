
from pydantic_settings import BaseSettings
class Settings(BaseSettings):
    TOKEN: str
    API_KEY: str
    TG_BOT_API_URL: str
    APP_DOMAIN: str
    LOG_LEVEL: str
    SECRET_TOKEN_TG_WEBHOOK: str

    class Config:
        env_file = ".env"