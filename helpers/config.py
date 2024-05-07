from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from telebot.async_telebot import AsyncTeleBot


class Settings(BaseSettings):
    TOKEN: str
    API_KEY: str
    TG_BOT_API_URL: str
    APP_DOMAIN: str
    LOG_LEVEL: str = 'DEBUG'
    SECRET_TOKEN_TG_WEBHOOK: str

    model_config = SettingsConfigDict(env_file="../.env")


@lru_cache
def get_settings() -> Settings:
    return Settings()


@lru_cache
def get_bot() -> AsyncTeleBot:
    token = get_settings().TOKEN
    bot = AsyncTeleBot(token)
    return bot
