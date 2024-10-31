from bot.actions import (add_city, start_message, change_city, weather, weather_forecast,
                         help_message, add_day, forecast_for_several_days, get_forecast_several, statistic, prediction)
from config.config import Settings
from telebot.async_telebot import AsyncTeleBot
import logging
import traceback
from decorators.decorators import log_database_query
from postgres.database_adapters import execute_query, add_statistic_bd, sql_update_user_state_bd
from asyncpg.pool import Pool
from postgres.sqlfactory import select, where, insert, update
from prometheus.couters import (unknown_command_counter, error_counter, total_users_counter, instance_id, )

log = logging.getLogger(__name__)


@log_database_query
async def check_chat_id(pool: Pool, message):
    """
     Checks the chat_id in the user_state table, inserts if not present, and retrieves the data.
     Args:
         pool (Pool): The asyncpg Pool.
         message: The message object containing chat information.
     Returns:
         dict: The user_state data for the given chat_id.
     """
    try:
        fields = {
            "chat_id": message.chat.id,
            "city": "Moskva",
            "date_difference": "None",
            "qty_days": "None",
        }

        on_conflict = "chat_id"
        sql_insert, args_insert = insert("user_state", fields, on_conflict=on_conflict)
        await execute_query(pool, sql_insert, *args_insert, fetch=True)

        sql_select = select("user_state", ["city", "date_difference", "qty_days"])
        query, args = where(sql_select, {"chat_id": ("=", message.chat.id)})

        res = await execute_query(pool, query, *args, fetch=True)

        decoded_result = [dict(r) for r in res][0]
        log.debug("user_state table updated successfully")
        return decoded_result
    except Exception as e:
        log.error("An error occurred: %s", str(e))
        log.debug(f"Exception traceback: \n {traceback.format_exc()}")


async def check_waiting(status_user: dict, pool, message, bot: AsyncTeleBot, config: Settings):
    """
    Check the status of the user and perform actions based on the status.
    Args:
        status_user (dict): Dictionary containing user status information.
        pool: The asyncpg Pool.
        message: The message object containing chat information.
        bot (AsyncTeleBot): The asynchronous Telegram bot instance.
        config (Settings): The settings configuration.
    Raises:
        Exception: If an error occurs during the process.
    """
    try:
        if status_user["city"] == "waiting_value":
            await add_city(pool, message, bot, config)
        if status_user["date_difference"] == "waiting_value":
            await add_day(pool, message, bot, config, status_user)
            await sql_update_user_state_bd(bot, pool, message, "date_difference", "None")
        if status_user["qty_days"] == "waiting_value":
            await get_forecast_several(message, bot, config, status_user)
            await sql_update_user_state_bd(bot, pool, message, "qty_days", "None")
    except Exception as e:
        await bot.send_message(message.chat.id, 'An error occurred. Please try again later.')
        log.error("An error occurred: %s", str(e))
        log.debug("Exception traceback", traceback.format_exc())


async def handlers(pool, message, bot, config, status_user):
    """
    This function handles different message commands and calls corresponding functions.

    Args:
        pool: The asyncpg Pool.
        message: The message object containing chat information.
        bot (AsyncTeleBot): The asynchronous Telegram bot instance.
        config (Settings): The settings configuration.
        status_user (dict): Dictionary containing user status information.
    """
    try:
        if message.text == '/start':
            await start_message(pool, message, bot)
            await add_statistic_bd(pool, message)
        elif message.text == '/help':
            await help_message(message, bot)
            await add_statistic_bd(pool, message)
        elif message.text == '/change_city':
            await change_city(pool, message, bot)
            await add_statistic_bd(pool, message)
        elif message.text == '/current_weather':
            await weather(message, bot, config, status_user)
            await add_statistic_bd(pool, message)
        elif message.text == '/weather_forecast':
            await weather_forecast(pool, message, bot)
            await add_statistic_bd(pool, message)
        elif message.text == '/forecast_for_several_days':
            await forecast_for_several_days(pool, message, bot)
            await add_statistic_bd(pool, message)
        elif message.text == '/weather_statistic':
            await statistic(message, bot, config, status_user)
            await add_statistic_bd(pool, message)
        elif message.text == '/prediction':
            await prediction(message, bot, config, status_user)
            await add_statistic_bd(pool, message)
        else:
            unknown_command_counter.labels(instance=instance_id).inc()  # Count the number of unknown commands
            await bot.send_message(message.chat.id, 'Unknown command. Please try again\n/help')
    except Exception as e:
        error_counter.labels(instance=instance_id).inc()  # Count the number of errors
        await bot.send_message(message.chat.id,
                               'An error occurred. Please send administrators a message or contact support.')
        log.error("An error occurred: %s", str(e))
        log.debug("Exception traceback", traceback.format_exc())
