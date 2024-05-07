from helpers.status_of_values import (user_input)
from bot.actions import (add_city, start_message, change_city, weather, weather_forecast,
                         help_message, add_day, forecast_for_several_days, get_forecast_several, statistic, prediction)
from helpers.config import Settings
from telebot.async_telebot import AsyncTeleBot

async def check_chat_id(message):
    if message.chat.id not in user_input:
        user_input[message.chat.id] = {'city': 'Moskva',
                                       'location': None,
                                       'date_difference': None,
                                       'qty_days': None}


async def check_waiting(message, bot: AsyncTeleBot, config: Settings):
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


async def handlers(message, bot, config):
    if message.text == '/start':
        await start_message(message, bot)
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
