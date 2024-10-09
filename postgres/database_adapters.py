import asyncpg
import logging
import traceback
from fastapi.security import HTTPBasicCredentials, HTTPBasic
from fastapi import HTTPException, Depends
from config.config import get_settings, Settings
#from postgres.pool import DbPool
from postgres.sqlfactory import update, where
from asyncpg import Pool
from postgres.pool import get_db_pool


log = logging.getLogger(__name__)
pool_cache = {}
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


#


async def create_table(pool: Pool = Depends(get_db_pool)):
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

    try:
        async with pool.acquire() as connection:
            async with connection.transaction():
                await connection.execute(create_user_state_table)  # Execute user_state table creation
                await connection.execute(create_statistic_table)  # Execute statistic table creation

        log.info("Tables created successfully")
    except Exception as e:
        log.error(f"An error occurred during table creation: {e}")
        log.error("Exception traceback:", traceback.format_exc())
        exit(1)  # Exit the program with error code 1


async def sql_update_user_state_bd(bot, pool: asyncpg.Pool, message, field, new_state: str = "waiting_value"):
    try:
        update_sql = update("user_state", {f"{field}": "$1"})
        conditions = {
            "chat_id": ("=", message.chat.id),
        }
        query, args = where(update_sql, conditions, 2)
        args.insert(0, new_state)

        await execute(pool, query, *args, fetch=True)
        return f"{query}", *args
    except Exception as e:
        log.error(f"An error occurred during user state adding: {e}")
        log.debug("Exception traceback:", traceback.format_exc())


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

    Returns:
        The result of the query based on the specified fetch method.
    """
    try:
        async with pool.acquire() as connection:
            connection: asyncpg.Connection
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
    except asyncpg.PostgresError as e:
        log.error(f"Database error: {e} {traceback.format_exc()}")
    except Exception as e:
        log.error(f"Unexpected error: {e} {traceback.format_exc()}")
    return None
