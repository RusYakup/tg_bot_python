from bot.actions import (add_city, start_message, change_city, weather, weather_forecast,
                         help_message, add_day, forecast_for_several_days, get_forecast_several, statistic, prediction)
from helpers.config import Settings
from telebot.async_telebot import AsyncTeleBot
import logging
import traceback
from postgres.database_adapters import execute, add_statistic_bd, sql_update_user_state_bd
from asyncpg.pool import Pool
from postgres.sqlfactory import select, where

log = logging.getLogger(__name__)


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
        query = "INSERT INTO user_state (chat_id, city, date_difference, qty_days) VALUES ($1, $2, $3, $4) ON CONFLICT (chat_id) DO NOTHING"
        args = [message.chat.id, "Moskva", "None", "None"]
        await execute(pool, query, *args, fetch=True)
        sql_select = select("user_state", fields=("city", "date_difference", "qty_days"))
        query, args = where(sql_select, {"chat_id": ("=", message.chat.id)}, 1)
        res = await execute(pool, query, *args, fetch=True)
        decoded_result = [dict(r) for r in res][0]
        log.info("user_state table updated successfully")
        return decoded_result
    except Exception as e:
        log.debug("An error occurred: %s", str(e))
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
            await add_day(pool, message, bot, config)
            query = await sql_update_user_state_bd(bot, pool, message, "date_difference", "None")
            await execute(pool, *query, fetch=True)
        if status_user["qty_days"] == "waiting_value":
            await get_forecast_several(pool, message, bot, config)
            query = await sql_update_user_state_bd(bot, pool, message, "qty_days", "None")
            await execute(pool, *query, fetch=True)


    except Exception as e:
        log.error("An error occurred: %s", str(e))
        log.error("Exception traceback", traceback.format_exc())


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
        elif message.text == '/help':
            await help_message(message, bot)
        elif message.text == '/change_city':
            await change_city(pool, message, bot)
        elif message.text == '/current_weather':
            await weather(message, bot, config, status_user)
        elif message.text == '/weather_forecast':
            await weather_forecast(pool, message, bot)
        elif message.text == '/forecast_for_several_days':
            await forecast_for_several_days(pool, message, bot)
        elif message.text == '/weather_statistic':
            await statistic(pool, message, bot, config, status_user)
        elif message.text == '/prediction':
            await prediction(pool, message, bot, config, status_user)
        else:
            await bot.send_message(message.chat.id, 'Unknown command. Please try again\n/help')
    except Exception as e:
        log.error("An error occurred: %s", str(e))
        log.error("Exception traceback", traceback.format_exc())
    finally:
        await add_statistic_bd(pool, message)
