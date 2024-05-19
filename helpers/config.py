from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from telebot.async_telebot import AsyncTeleBot
import logging
import traceback
import asyncpg
from typing import Union
from asyncpg import Connection
from asyncpg.pool import Pool

log = logging.getLogger(__name__)


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


# pool_cache = {}
#
#
# async def create_pool():
#     try:
#         dsn = f"postgresql://{get_settings().POSTGRES_USER}:{get_settings().POSTGRES_PASSWORD}@localhost/{get_settings().POSTGRES_DB}"
#         if dsn in pool_cache:
#             return pool_cache[dsn]
#
#         pool = await asyncpg.create_pool(dsn=dsn, min_size=3, max_size=100, max_inactive_connection_lifetime=60,
#                                          max_queries=1000)
#         pool_cache[dsn] = pool
#         log.info("Успешное подключение к базе данных: %s", dsn)
#         return pool
#     except Exception as e:
#         log.error("Не удалось подключиться к базе данных: %s", str(e))
#         exit(1)
#
#
# def connection():
#     connection = asyncpg.connect(
#         f"postgresql://{get_settings().POSTGRES_USER}:{get_settings().POSTGRES_PASSWORD}@localhost/{get_settings().POSTGRES_DB}")
#     return connection
#
#
# def create_table():
#     try:
#         connection = asyncpg.connect(
#             f"postgresql://{get_settings().POSTGRES_USER}:{get_settings().POSTGRES_PASSWORD}@localhost/{get_settings().POSTGRES_DB}")
#         connection.execute(
#             "CREATE TABLE IF NOT EXISTS user_state (chat_id BIGINT PRIMARY KEY, city TEXT, date_difference TEXT, qty_days TEXT)")
#     except Exception as e:
#         log.error("Не удалось создать таблицу: %s", str(e))
#         exit(1)
#
#
# async def close_pool(pool, connection):
#     try:
#         await pool.release(connection)
#     except Exception as e:
#         log.error(f"Ошибка при закрытии пула соединений: {str(e)}")
#

class DataBaseClass:
    def __init__(self):
        self.pool: Union[Pool, None] = None
        self.connection: Union[Connection, None] = None

    async def create_pool(self):
        try:
            self.pool = await asyncpg.create_pool(f"postgresql://{get_settings().POSTGRES_USER}:"
                                                  f"{get_settings().POSTGRES_PASSWORD}@localhost/{get_settings().POSTGRES_DB}"
                                                  )
            log.info("Успешное подключение к базе данных")
        except Exception as e:
            log.error(f"Не удалось подключиться к базе данных: {str(e)}")
            log.info("Exception traceback:", traceback.format_exc())


    async def execute(self, command: str, *args,
                      fetch: bool = False,
                      fetchval: bool = False,
                      fetchrow: bool = False,
                      execute: bool = False):
        async with self.pool.acquire() as connection:
            connection: Connection
            async with connection.transaction():
                if fetch:
                    result = await connection.fetch(command, *args)
                    log.info("fetch command executed successfully")
                elif fetchval:
                    result = await connection.fetchval(command, *args)
                    log.info("fetchval command executed successfully")
                elif fetchrow:
                    result = await connection.fetchrow(command, *args)
                    log.info("fetchrow command executed successfully")
                elif execute:
                    result = await connection.execute(command, *args)
                    log.info("execute command executed successfully")
                else:
                    result = None
        return result

    async def create_table(self):
        try:
            await self.create_pool()
            create_user_state_table = """
                CREATE TABLE IF NOT EXISTS user_state(
                    chat_id INTEGER PRIMARY KEY,
                    city VARCHAR(50),
                    date_difference VARCHAR(15),
                    qty_days VARCHAR(15),
                    CONSTRAINT unique_chat_id UNIQUE (chat_id)
                );
            """
            create_statistic_table = """
                CREATE TABLE IF NOT EXISTS statistic(
                    id SERIAL PRIMARY KEY,
                    ts INTEGER,
                    user_name VARCHAR(50),
                    chat_id INTEGER,
                    action VARCHAR(50)
                );
            """
            await self.execute(create_user_state_table, execute=True)
            await self.execute(create_statistic_table, execute=True)
            log.info("Таблицы успешно созданы")
        except Exception as e:
            log.error("Не удалось создать таблицу: %s", str(e))
            log.error("Traceback:", traceback.format_exc())
            exit(1)

    async def close_pool(self, pool, connection):
        try:
            await pool.release(connection)
        except Exception as e:
            log.error(f"Ошибка при закрытии пула соединений: {str(e)}")
DataBase = DataBaseClass()
