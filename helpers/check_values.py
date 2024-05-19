from helpers.status_of_values import (user_input)
from bot.actions import (add_city, start_message, change_city, weather, weather_forecast,
                         help_message, add_day, forecast_for_several_days, get_forecast_several, statistic, prediction)
from helpers.config import Settings
from telebot.async_telebot import AsyncTeleBot
import logging
import traceback
from helpers.config import DataBaseClass


log = logging.getLogger(__name__)


async def check_chat_id(message, DataBase: DataBaseClass):
    try:

        chat_id = message.chat.id

        query = "INSERT INTO user_state (chat_id, city, date_difference, qty_days) VALUES ($1, $2, $3, $4) ON CONFLICT (chat_id) DO NOTHING"
        args = [chat_id, "Moskva", "None", "None"]
        await DataBase.execute(query, *args, fetch=True)

        # await check_chat_id(message, pool)
        # user_input_values = user_input.get(message.chat.id, {}).values()
        # if any(value == 'waiting value' for value in user_input_values):
        #     await check_waiting(message, bot, config)
        # else:
        #     await handlers(message, bot, config)

    except Exception as e:
        log.debug("An error occurred: %s", str(e))
        log.debug(traceback.format_exc())


# try:
#         async with pool.transaction():
#             existing_chat_id = await pool.fetchrow("SELECT chat_id FROM user_state WHERE chat_id = $1",
#                                                    message.chat.id)
#             if existing_chat_id is None:
#                 await pool.execute(
#                     "INSERT INTO user_state (chat_id, city, date_difference, qty_days) VALUES ($1, $2, $3, $4)",
#                     message.chat.id, "Moskva", None, None)
#     except Exception as e:
#         log.debug("An error occurred: %s", str(e))
#         log.debug(traceback.format_exc())
#         await pool.close()

# if message.chat.id not in user_input:
#     user_input[message.chat.id] = {'city': 'Moskva',
#                                    'date_difference': "None",
#                                    'qty_days': "None"}
#

async def check_status(message, pool):
    # try:
        pass
    #     query = "SELECT city, date_difference, qty_days FROM user_state WHERE chat_id = $1"
    #     args = [message.chat.id]
    #     status = await load_data(pool, query, args)
    #
    #     if status[0][1] == "waiting value":
    #         await add_city(message, pool)
    #     if status[1][1] == "waiting value":
    #         await add_day(message, pool)
    #         query_new = "UPDATE user_state SET date_difference = $1 WHERE chat_id = $2"
    #         new_status = "None"
    #         await pool.execute(query_new, new_status, message.chat.id)
    #     if status[2][1] == "waiting value":
    #         await get_forecast_several(message, pool)
    #         query_new = "UPDATE user_state SET qty_days = $1 WHERE chat_id = $2"
    #         new_status = "None"
    #         await pool.execute(query_new, new_status, message.chat.id)
    # except Exception as e:
    #     log.error("An error occurred: %s", str(e))
    #     log.debug("Exception traceback", traceback.format_exc())
    #

async def check_waiting(message, bot: AsyncTeleBot, config: Settings, DataBase: DataBaseClass):
    try:




        if user_input[message.chat.id]['city'] == "waiting value":
            await add_city(message, bot, config)
        # if user_input[message.chat.id]['location'] == "waiting value":
        #     print("waiting value: location")
        #     await get_coordinates(message)
        if user_input[message.chat.id]['date_difference'] == "waiting value":
            await add_day(message, bot, config)
            user_input[message.chat.id]['date_difference'] = None
        if user_input[message.chat.id]['qty_days'] == "waiting value":
            await get_forecast_several(message, bot, config)
            user_input[message.chat.id]['qty_days'] = None
    except Exception as e:
        log.error("An error occurred: %s", str(e))
        log.debug("Exception traceback", traceback.format_exc())



async def handlers(message, bot, config):
    if message.text == '/start':
        await start_message(message, bot, config)
    elif message.text == '/help':
        await help_message(message, bot)
    elif message.text == '/change_city':
        await change_city(message, bot)
    elif message.text == '/current_weather':
        await weather(message, bot, config)
    elif message.text == '/weather_forecast':
        await weather_forecast(message, bot)
    elif message.text == '/forecast_for_several_days':
        await forecast_for_several_days(message, bot)
    elif message.text == '/weather_statistic':
        await statistic(message, bot, config)
    elif message.text == '/prediction':
        await prediction(message, bot, config)

    else:
        await bot.send_message(message.chat.id, 'Unknown command. Please try again\n/help')
