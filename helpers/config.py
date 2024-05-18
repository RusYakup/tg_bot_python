from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from telebot.async_telebot import AsyncTeleBot
import logging
import traceback

log = logging.getLogger(__name__)
import asyncpg


class Settings(BaseSettings):
    TOKEN: str
    API_KEY: str
    TG_BOT_API_URL: str
    APP_DOMAIN: str
    LOG_LEVEL: str = 'DEBUG'
    SECRET_TOKEN_TG_WEBHOOK: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    model_config = SettingsConfigDict(env_file="../.env")


@lru_cache
def get_settings() -> Settings:
    return Settings()


@lru_cache
def get_bot() -> AsyncTeleBot:
    token = get_settings().TOKEN
    bot = AsyncTeleBot(token)
    return bot


@lru_cache
def create_pool():
    try:
        dsn = f"postgresql://{get_settings().POSTGRES_USER}:{get_settings().POSTGRES_PASSWORD}@localhost/{get_settings().POSTGRES_DB}"
        pool = asyncpg.create_pool(dsn=dsn, min_size=3, max_size=100, max_inactive_connection_lifetime=60,
                                         max_queries=1000)
        log.info("Connected to the database successfully: %s", dsn)
        return pool
    except Exception as e:
        log.error("Failed to connect to the database: %s", str(e))
        exit(1)


# async def create_table(pool):
#     async with pool.acquire() as connection:
#         create_tables = """
#             CREATE TABLE IF NOT EXISTS user_state (
#                 chat_id INTEGER,
#                 city VARCHAR(50),
#                 date_difference VARCHAR(15),
#                 qty_days VARCHAR(15)
#             );
#             CREATE TABLE IF NOT EXISTS statistic (
#                 id SERIAL PRIMARY KEY,
#                 ts INTEGER,
#                 user_name VARCHAR(50),
#                 chat_id INTEGER,
#                 action VARCHAR(50)
#             );
#         """
#         await connection.execute(create_tables)
