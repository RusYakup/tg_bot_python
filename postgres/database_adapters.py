import asyncpg
import logging
import traceback
from fastapi.security import HTTPBasicCredentials, HTTPBasic
from fastapi import HTTPException, Depends
from decorators.decorators import log_database_query
from prometheus.couters import instance_id, database_errors_counters, count_instance_errors
from config.config import get_settings, Settings
from postgres.sqlfactory import update, where, insert, delete
from asyncpg import Pool
from postgres.pool import DbPool
from typing import Union, Optional

log = logging.getLogger(__name__)
security = HTTPBasic()


def verify_credentials(credentials: HTTPBasicCredentials = Depends(security),
                       settings: Settings = Depends(get_settings)):
    """
    Function to verify the provided credentials.
    Args:
        credentials (HTTPBasicCredentials): The credentials to be verified.
        settings (Settings): The application settings.
    Returns:
        HTTPBasicCredentials: The verified credentials if successful.
    Raises:
        HTTPException: If the credentials are incorrect.
    """
    try:
        correct_username = settings.GET_USER
        correct_password = settings.GET_PASSWORD
        # Check if the provided credentials match the correct username and password
        if credentials.username == correct_username and credentials.password == correct_password:
            log.info("Credentials verified successfully")
            return credentials
    except HTTPException as e:
        log.debug("An error occurred: %s", str(e))
        log.debug("Exception traceback", traceback.format_exc())
        raise HTTPException(status_code=401, detail="Incorrect username or password")


async def create_table(pool: Pool = Depends(DbPool.get_pool)):
    """
    This function creates two tables: user_state and statistic.
    """
    log.debug("Creating table...")
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
    create_users_online_table = """
    CREATE TABLE IF NOT EXISTS users_online (
            chat_id INTEGER NOT NULL UNIQUE,
            timestamp INTEGER NOT NULL
    );
    """

    try:
        async with pool.acquire() as connection:
            async with connection.transaction():
                await connection.execute(create_user_state_table)  # Execute user_state table creation
                await connection.execute(create_statistic_table)  # Execute statistic table creation
                await connection.execute(create_users_online_table)

        log.info("Tables created successfully")
    except Exception as e:
        log.error(f"An error occurred during table creation: {e}")
        log.debug("Exception traceback:", traceback.format_exc())
        exit(1)  # Exit the program with error code 1


@log_database_query
async def sql_update_user_state_bd(bot, pool: asyncpg.Pool, message, fields: str, new_state: str = "waiting_value"):
    try:
        update_query, args = update("user_state", {fields: new_state})

        conditions = {
            "chat_id": ("=", message.chat.id),
        }
        query_where, args_where = where(update_query, conditions)
        args += args_where
        await execute_query(pool, query_where, *args, fetch=True)
        if new_state == "waiting_value":
            log.info(f"User {message.chat.id} state waiting_value for data")
        else:
            log.info(f"User {message.chat.id} {fields} updated successfully")
    except Exception as e:
        count_instance_errors.labels(instance=instance_id).inc()
        await bot.send_message(message.chat.id, "An error occurred. Please try again later.")
        log.error(f"An error occurred during user state adding: {e}")
        log.debug("Exception traceback:", traceback.format_exc())


@log_database_query
async def add_statistic_bd(pool: asyncpg.Pool, message):
    """
    Add a statistic record to the database based on the message received.

    Args:
        pool (asyncpg.Pool): The connection pool to the database.
        message: The message object containing the necessary information.

    Returns:
        None: If the message text is not in the predefined command list.

    Raises:
        Exception: If an error occurs during the process.
    """
    try:
        # List of valid commands
        command = ["/start", "/help", "/change_city", "/current_weather", "/weather_forecast",
                   "/forecast_for_several_days", "/weather_statistic", "/prediction"]

        if message.text in command:
            fields = {"ts": message.date, "user_name": message.from_user.first_name, "chat_id": message.chat.id,
                      "action": message.text}
            sql, args = insert("statistic", fields)
            await execute_query(pool, sql, *args, fetch=True)
            log.debug("Statistic added successfully")
            return
        else:
            return None
    except Exception as e:
        count_instance_errors.labels(instance=instance_id).inc()
        log.error(f"An error occurred during statistic adding: {e}")
        log.error("Exception traceback:", traceback.format_exc())


async def execute_query(pool: asyncpg.Pool, query: str, *args,
                        fetch: bool = False,
                        fetchval: bool = False,
                        fetchrow: bool = False,
                        execute: bool = False,
                        max_retries: int = 10) -> Optional[Union[asyncpg.Record, int]]:
    """
    Execute the specified query using the provided connection pool.
    Args:
        pool (asyncpg.Pool): The connection pool to execute the query.
        query (str): The SQL query to execute.
        *args: Optional arguments to be passed with the query.
        fetch (bool): If True, fetch all results.
        fetchval (bool): If True, fetch a single value.
        fetchrow (bool): If True, fetch a single row.
        execute (bool): If True, execute the query without fetching.
        max_retries (int): The maximum number of retries.
    Returns:
        The result of the query based on the specified fetch method.
    """
    retries = 0
    while retries < max_retries:
        try:
            async with pool.acquire() as connection:
                async with connection.transaction():
                    if fetch:
                        result = await connection.fetch(query, *args)
                        log.debug("fetch command executed successfully")
                    elif fetchval:
                        result = await connection.fetchval(query, *args)
                        log.debug("fetchval command executed successfully")
                    elif fetchrow:
                        result = await connection.fetchrow(query, *args)
                        log.debug("fetchrow command executed successfully")
                    elif execute:
                        result = await connection.execute(query, *args)
                        log.debug("execute command executed successfully")
                    else:
                        result = None
            return result
        except asyncpg.PostgresError as e:
            log.error(f"Database error: {e} {traceback.format_exc()}")
            database_errors_counters[0].labels(instance=instance_id).inc()  # database_connection_errors
        except asyncpg.QueryCanceledError as e:
            log.error(f"Query canceled error: {e} {traceback.format_exc()}")
            database_errors_counters[1].labels(instance=instance_id).inc()  # database_query_errors
        except Exception as e:
            log.error(f"Unexpected error: {e} {traceback.format_exc()} {query} {args}")
            database_errors_counters[2].labels(instance=instance_id).inc()  # database_other_errors
    raise Exception("Max retries exceeded")

# @log_database_query
# async def add_user_id(chat_id, pool: Pool = Depends(DbPool.get_pool)):
#     timestamp = int(datetime.datetime.now().timestamp())
#
#     try:
#         sql_update, args_update = update("users_online", {"timestamp": timestamp})
#         conditions = {
#             "chat_id": ("=", chat_id)
#         }
#         query_where, args = where(sql_update, conditions)
#         args_where = args_update + args
#         res = await execute_query(pool, query_where, *args_where, execute=True)
#         if res == "UPDATE 0":
#             sql_insert, args = insert("users_online", {"chat_id": chat_id, "timestamp": timestamp})
#             # current_users_gauge.labels(instance=instance_id).inc()
#             await execute_query(pool, sql_insert, *args, execute=True)
#     except Exception as e:
#         log.error(f"An error occurred during user state adding: {e}")
#         log.debug("Exception traceback:", traceback.format_exc())
#

# @log_database_query
# async def del_users_online(pool: asyncpg.Pool):
#
#     try:
#         log.debug("Starting the task: del_users_online")
#         res = delete("users_online")
#         sql, args = where(res, {"timestamp": ("<", int(time.time()) - 60)})  # 60 seconds test
#         res = await execute_query(pool, sql, *args, execute=True)
#         result_parts = res.split()
#         deleted_count = int(result_parts[1]) if len(result_parts) == 2 else 0
#         if deleted_count >= 1:
#             log.info(f"Deleted {deleted_count} users online")
#             # current_value = current_users_gauge.labels(instance=instance_id)._value.get()
#             # if current_value > 0:
#             #     current_users_gauge.labels(instance=instance_id).dec()
#             # else:
#             #     log.info(f"Current users count for instance {instance_id} is already zero and cannot be decremented.")
#         else:
#             log.info("No users online were deleted")
#     except Exception as e:
#         log.error(f"Error в del_users_online: {e}")
