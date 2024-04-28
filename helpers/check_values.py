from waiting.status_of_values import (user_input)
from bot.actions import (add_city, start_message, change_city, weather, weather_forecast,
                         help_message, add_day, forecast_for_several_days, get_forecast_several, statistic, prediction)


async def check_chat_id(message):
    if message.chat.id not in user_input:
        user_input[message.chat.id] = {'city': 'Moskva',
                                       'location': None,
                                       'date_difference': None,
                                       'qty_days': None}
    else:
        # TODO: not functional part of code
        pass


async def check_waiting(message):
    if user_input[message.chat.id]['city'] == "waiting value":
        await add_city(message)
    # if user_input[message.chat.id]['location'] == "waiting value":
    #     print("waiting value: location")
    #     await get_coordinates(message)
    if user_input[message.chat.id]['date_difference'] == "waiting value":
        await add_day(message)
        user_input[message.chat.id]['date_difference'] = None
    if user_input[message.chat.id]['qty_days'] == "waiting value":
        await get_forecast_several(message)
        user_input[message.chat.id]['qty_days'] = None
    else:
        # TODO: not functional part of code
        pass


async def handlers(bot, message):
    if message.text == '/start':
        await start_message(message)
    elif message.text == '/help':
        await help_message(message)
    elif message.text == '/change_city':
        await change_city(message)
    elif message.text == '/current_weather':
        await weather(message)
    elif message.text == '/weather_forecast':
        await weather_forecast(message)
    elif message.text == '/forecast_for_several_days':
        await forecast_for_several_days(message)
    elif message.text == '/weather_statistic':
        await statistic(message)
    elif message.text == '/prediction':
        await prediction(message)

    else:
        await bot.send_message(message.chat.id, 'Unknown command. Please try again\n/help')
