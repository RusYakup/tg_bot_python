from bot.actions import (add_city, start_message, change_city, weather, weather_forecast,
                         help_message, add_day, forecast_for_several_days, get_forecast_several, statistic, prediction)
from helpers.config import Settings
from telebot.async_telebot import AsyncTeleBot
import logging
import traceback
from postgres.database_adapters import execute, add_statistic_bd
from asyncpg.pool import Pool

log = logging.getLogger(__name__)


async def check_chat_id(pool: Pool, message):
    try:
        query = "INSERT INTO user_state (chat_id, city, date_difference, qty_days) VALUES ($1, $2, $3, $4) ON CONFLICT (chat_id) DO NOTHING"
        args = [message.chat.id, "Moskva", "None", "None"]
        await execute(pool, query, *args, fetch=True)

        query = "SELECT city, date_difference, qty_days FROM user_state WHERE chat_id = $1"
        result = await execute(pool, query, message.chat.id, fetch=True)
        decoded_result = [dict(r) for r in result][0]
        log.debug("user_state table updated successfully")
        return decoded_result
    except Exception as e:
        log.debug("An error occurred: %s", str(e))
        log.debug(traceback.format_exc())


async def check_waiting(status_user: dict, pool, message, bot: AsyncTeleBot, config: Settings):
    try:
        if status_user["city"] == "waiting_value":
            await add_city(pool, message, bot, config)
        if status_user["date_difference"] == "waiting_value":
            await add_day(pool, message, bot, config)
        if status_user["qty_days"] == "waiting_value":
            await get_forecast_several(pool, message, bot, config)
            query_new = "UPDATE user_state SET qty_days = $1 WHERE chat_id = $2"
            new_status = "None"
            await execute(pool, query_new, new_status, message.chat.id, fetch=True)
    except Exception as e:
        log.error("An error occurred: %s", str(e))
        log.error("Exception traceback", traceback.format_exc())


async def handlers(pool, message, bot, config, status_user):
    try:
        if message.text == '/start':
            await start_message(pool, message, bot, config)
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
