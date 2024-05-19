import asyncpg
import asyncio
import logging
import traceback
# from helpers.config import close_pool
# from helpers.config import create_pool
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

log = logging.getLogger(__name__)


async def execute_query(pool, query: str, *args):
    try:
        pool = await create_pool()

        log.info("СОздали новый пул соединений")

        async with pool.acquire() as connection:
            result = await connection.fetch(query, *args)
            log.info("Запрос выполнен успешно")
            return result
    except Exception as e:
        log.error(f"Ошибка при выполнении запроса: {str(e)}")
        log.info("Exception traceback:", traceback.format_exc())
    finally:
        if pool:
            await close_pool(pool, connection)
            log.info("Пул соединений закрыт")


async def load_data(pool: asyncpg.Pool, query: str, *args, timeout=10):
    try:
        log.debug("Loading data...")
        async with pool.acquire() as connection:
            async with connection.transaction():
                result = await connection.fetch(query, *args, timeout=timeout)
                log.debug("Data loaded successfully")
                print("Data loaded successfully")
        return result
    except asyncio.TimeoutError:
        log.error(
            'Postgres query timed out', traceback.format_exc())
        raise asyncio.TimeoutError('Postgres query timed out')
    except asyncpg.exceptions.UndefinedTableError:
        log.error(
            'Postgres table not found', traceback.format_exc())
        raise
    except asyncpg.exceptions.UndefinedColumnError:
        log.error(
            'Postgres column not found', traceback.format_exc())
        raise
    except:
        log.error(
            'Postgres query failed')
        log.info("Exception traceback:", traceback.format_exc())
        raise
    finally:
        if pool:
            await pool.release(connection)


#
#     return result


async def create_table(pool):
    log.debug("Creating table...")
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
                user_name VARCHAR(50),
                chat_id INTEGER,
                action VARCHAR(50)
            );
        """

        async with pool.acquire() as connection:
            async with connection.transaction():
                await connection.execute(create_user_state_table)
                await connection.execute(create_statistic_table)
        log.info("Tables created successfully")
    except Exception as e:
        log.error(f"An error occurred during table creation: {e}")
        log.error("Exception traceback:", traceback.format_exc())
        exit(1)
    finally:
        if pool:
            await pool.release(connection)
            print("Pool released")



async def check_status(message, pool):
    try:
        query = "SELECT city, date_difference, qty_days FROM user_state WHERE chat_id = $1"
        args = [message.chat.id]
        status = await load_data(pool, query, args)

        if status[0][1] == "waiting value":
            await add_city(message, pool)
        if status[1][1] == "waiting value":
            await add_day(message, pool)
            query_new = "UPDATE user_state SET date_difference = $1 WHERE chat_id = $2"
            new_status = "None"
            await pool.execute(query_new, new_status, message.chat.id)
        if status[2][1] == "waiting value":
            await get_forecast_several(message, pool)
            query_new = "UPDATE user_state SET qty_days = $1 WHERE chat_id = $2"
            new_status = "None"
            await pool.execute(query_new, new_status, message.chat.id)
    except Exception as e:
        log.error("An error occurred: %s", str(e))
        log.debug("Exception traceback", traceback.format_exc())
