import asyncpg
import logging
import traceback
from asyncpg import Connection
from helpers.config import get_settings

log = logging.getLogger(__name__)
pool_cache = {}


async def create_pool(clear_cache: bool = False):
    try:
        if clear_cache:
            pool_cache.clear()
        else:
            dsn = f"postgresql://{get_settings().POSTGRES_USER}:{get_settings().POSTGRES_PASSWORD}@localhost/{get_settings().POSTGRES_DB}"
            if dsn in pool_cache:
                return pool_cache[dsn]

            pool = await asyncpg.create_pool(dsn=dsn, min_size=3, max_size=100, max_inactive_connection_lifetime=60,
                                             max_queries=1000)
            pool_cache[dsn] = pool
            log.info("Successfully connected to the database: %s", dsn)

            return pool
    except Exception as e:
        log.error("Не удалось подключиться к базе данных: %s", str(e))
        log.error("Exception traceback:", traceback.format_exc())
        exit(1)


async def create_table():
    log.debug("Creating table...")
    pool = await create_pool()
    try:
        create_user_state_table = """
            CREATE TABLE IF NOT EXISTS user_state (
                chat_id INTEGER PRIMARY KEY,
                city VARCHAR(50),
                date_difference VARCHAR(15),
                qty_days VARCHAR(15),
                CONSTRAINT unique_chat_id UNIQUE (chat_id)
            );
        """
        create_statistic_table = """
            CREATE TABLE IF NOT EXISTS statistic (
                id SERIAL PRIMARY KEY,
                ts INTEGER,
                user_id INTEGER,
                user_name VARCHAR(50),
                chat_id INTEGER,
                action VARCHAR(50)
            );
        """
        async with pool.acquire() as connection:
            async with connection.transaction():
                await connection.execute(create_user_state_table)
                await connection.execute(create_statistic_table)
        await pool.close()
        await create_pool(clear_cache=True)
        log.info("Tables created successfully")
    except Exception as e:
        log.error(f"An error occurred during table creation: {e}")
        log.error("Exception traceback:", traceback.format_exc())
        exit(1)


async def add_statistic_bd(pool: asyncpg.Pool, message):
    try:
        command = ["/start", "/help", "/change_city", "/current_weather", "/weather_forecast",
                   "/forecast_for_several_days", "/weather_statistic", "/prediction"]
        if message.text in command:
            query = "INSERT INTO statistic (ts, user_name, chat_id, action) VALUES ($1, $2, $3, $4)"
            args = [message.date, message.from_user.first_name, message.chat.id, message.text]
            await execute(pool, query, *args, fetch=True)
            log.debug("Statistic added successfully")
            return
        else:
            return None
    except Exception as e:
        log.error(f"An error occurred during statistic adding: {e}")
        log.error("Exception traceback:", traceback.format_exc())


async def execute(pool: asyncpg.Pool, query: str, *args,
                  fetch: bool = False,
                  fetchval: bool = False,
                  fetchrow: bool = False,
                  execute: bool = False):
    async with pool.acquire() as connection:
        connection: Connection
        async with connection.transaction():
            if fetch:
                result = await connection.fetch(query, *args)
                log.info("fetch command executed successfully")
            elif fetchval:
                result = await connection.fetchval(query, *args)
                log.info("fetchval command executed successfully")
            elif fetchrow:
                result = await connection.fetchrow(query, *args)
                log.info("fetchrow command executed successfully")
            elif execute:
                result = await connection.execute(query, *args)
                log.info("execute command executed successfully")
            else:
                result = None
    return result
