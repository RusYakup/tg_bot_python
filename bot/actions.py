import os
import telebot
from dotenv import load_dotenv, find_dotenv
from helpers.helpers import wind, get_response # weather_condition, # check_bot_token, check_api_key,
from helpers.models import *
from pydantic import ValidationError
from telebot.async_telebot import AsyncTeleBot
from waiting.status_of_values import user_input
import requests
from datetime import datetime, date, timedelta
import logging
import aiohttp
import traceback

# logging = logging.getLogger()
#  TODO: Need to use logging library to print logs. Log level must be adjustable via env variables. Detail logs needed
#  for debugging should use with debug log level. Logs that used to make clearly what is going on in the app,
#  can use info log level.


load_dotenv(find_dotenv())
log = logging.getLogger(__name__)

# TODO: don't re-read the same env variable several times. Need to build config of application only one time during startup
#  Then, all parts of application must use this config. Review how should do it here: https://fastapi.tiangolo.com/advanced/settings/#settings-and-environment-variables
TOKEN = os.environ['TOKEN']
bot = AsyncTeleBot(os.environ['TOKEN'])
API_KEY_weather = (os.environ['API_KEY'])


@bot.message_handler(commands=['start'])
async def start_message(message):
    try:
        log.info("User %s started bot", message.from_user.first_name)
        kb_reply = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        # btn1 = telebot.types.KeyboardButton(text="Location",
        #                                     request_location=True)
        # kb_reply.add(btn1)
        msg = (
            f'Hello {message.from_user.first_name}! I am WeatherForecastBot, your personal assistant for getting an accurate'
            f' weather forecast. I can provide you with weather information for any city. Just type the name of the city '
            f'or share your location, and I will tell you what to expect! Shall we begin?'
            f'Here are the commands I know: \n'
            f'/help - help\n'
            f'/change_city - change city\n'
            f'/current_weather - current weather\n'
            f'/weather_forecast - weather forecast for a specific date\n'
            f'/forecast_for_several_days - weather forecast for several days (from 2 to 10)\n'
            f'/weather_statistics - weather statistics for the last 7 days\n'
            f'/prediction - prediction of the average temperature for 3 days\n'
            f'or simply press the menu to display all commands \n')
        await bot.send_message(message.chat.id, msg)  ###, reply_markup=kb_reply###
        user_input[message.chat.id] = {'city': None, 'location': None, 'date_difference': None, 'qty_days': None}
    except Exception as e:
        log.error("An error occurred: %s", str(e))
        log.error(traceback.format_exc())
        await bot.send_message(message.chat.id, 'An error occurred. Please try again later.')


# @bot.message_handler(content_types=['location'])
# async def get_coordinates(message):
#     latitude, longitude = message.location.latitude, message.location.longitude
#     local = f'{latitude},{longitude}'
#     city = local
#     loger.debug(f"User {message.chat.id} added new city: {city}")


@bot.message_handler(commands=['change_city'])
async def change_city(message):
    try:
        log.debug("User {message.chat.id} wants to change city")
        await bot.send_message(message.chat.id, 'Please enter the new city')
        user_input[message.chat.id]['city'] = 'waiting value'
        log.debug(f" User {message.chat.id} waiting value: city")
    except Exception as e:
        log.error("An error occurred: %s", str(e))
        log.error(traceback.format_exc())
        await bot.send_message(message.chat.id, 'An error occurred. Please try again later.')


async def add_city(message):
    try:
        log.debug("verify city")
        url = f'http://api.weatherapi.com/v1/forecast.json?key={API_KEY_weather}&q={message.text}'
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    user_input[message.chat.id]['city'] = message.text
                    log.debug(f"User {message.chat.id} added new city: {message.text}")
                    await bot.send_message(message.chat.id, 'City added successfully. Select the next command.')
                else:
                    await bot.send_message(message.chat.id, 'City not found. Please try again')
    except Exception as e:
        log.error("An error occurred: %s", str(e))
        log.error(traceback.format_exc())
        await bot.send_message(message.chat.id, 'An error occurred. Please try again later.')


@bot.message_handler(commands=['help'])
async def help_message(message):
    try:
        log.debug("User requested help")
        help_messages = (
            ('help', 'help'),
            ('change_city', 'change city'),
            ('current_weather', 'current weather'),
            ('weather_forecast', 'weather forecast for a specific date'),
            ('forecast_for_several_days', 'weather forecast for multiple days'),
            ('weather_statistic', 'weather statistics for the last 7 days'),
            ('prediction', 'prediction for 3 days')
        )
        full_msg = '\n'.join([f'/{command} - {description}' for command, description in help_messages])

        await bot.send_message(message.chat.id, full_msg)
    except Exception as e:
        log.error("An error occurred: %s", str(e))
        log.error(traceback.format_exc())
        await bot.send_message(message.chat.id, 'An error occurred. Please try again later.')


@bot.message_handler(commands=['current_weather'])
async def weather(message):
    try:
        log.debug(f"User requested current weather for': {user_input[message.chat.id]['city']}")
        url_current = f'http://api.weatherapi.com/v1/forecast.json?key={API_KEY_weather}&q={user_input[message.chat.id]["city"]}'
        data = get_response(message, url_current, bot)
        weather_data = WeatherData.parse_obj(data)
        forecast = weather_data.forecast.forecastday[0].day

        current_msg = (
            f"{weather_data.location.name} ({weather_data.location.region}): {weather_data.location.localtime}\n"
            f"Temperature: {weather_data.current.temp_c}°C (feels like {weather_data.current.feelslike_c}°C)\n"
            f"Maximum temperature: {forecast.maxtemp_c}°C\n"
            f"Minimum temperature: {forecast.mintemp_c}°C\n"
            f"{wind(weather_data.current.wind_dir, weather_data.current.wind_kph, weather_data.forecast.forecastday[0].day.maxwind_kph)}\n"
            f"Humidity: {weather_data.current.humidity}% \n"
            f"Precipitation: {forecast.daily_chance_of_rain if weather_data.current.temp_c > 0 else forecast.daily_chance_of_snow}%\n"
            f"{forecast.condition.text}"
        )
        await bot.send_message(message.chat.id, current_msg)
        return log.info("current_weather: Success")
    except Exception as e:
        log.error("An error occurred: %s", str(e))
        log.error(traceback.format_exc())
        await bot.send_message(message.chat.id, f"Error")
    except ValidationError as e:
        log.error(f"Data validation error {e}")
        await bot.send_message(message.chat.id, 'An error occurred. Please try again later.')


@bot.message_handler(commands=['weather_forecast'])
async def weather_forecast(message):
    try:
        today_date = date.today()
        max_date = today_date + timedelta(days=10)
        await bot.send_message(message.chat.id,
                               f'Input the date from {today_date} до {max_date}:')
        user_input[message.chat.id]['date_difference'] = 'waiting value'
        log.debug(f" User {message.chat.id} waiting value: city")
    except Exception as e:
        log.error("An error occurred: %s", str(e))
        log.error(traceback.format_exc())
        await bot.send_message(message.chat.id, 'An error occurred. Please try again later.')


async def add_day(message):
    try:
        today_date = date.today()
        input_date = datetime.strptime(message.text, "%Y-%m-%d").date()
        if (input_date - today_date).days <= 10:
            user_input[message.chat.id]['date_difference'] = (input_date - today_date).days + 2
            await get_weather_forecast(message)
            return
        else:
            max_date = today_date + timedelta(days=10)
            await bot.send_message(message.chat.id, f'The entered date must be no later than {max_date}.')
            log.debug("add_day: The entered date must be no later than {max_date}.")
            return
    except ValueError:
        await bot.send_message(message.chat.id, "Date must be in the format YYYY-MM-DD.")
        log.debug("add_day: Does not match the format YYYY-MM-DD.")
    except Exception as e:
        log.error("An error occurred: %s", str(e))
        log.error(traceback.format_exc())
    log.debug(f"User input (weather_forecast): {message.text}")


async def get_weather_forecast(message):
    try:
        log.debug(
            f"User requested weather forecast {user_input[message.chat.id]['date_difference']} дней: {user_input[message.chat.id]['city']}")
        url_forecast = f'http://api.weatherapi.com/v1/forecast.json?key={API_KEY_weather}&q={user_input[message.chat.id]["city"]}&days={user_input[message.chat.id]["date_difference"]}&aqi=no&alerts=no'
        data = get_response(message, url_forecast, bot)
        weather_data = WeatherData.parse_obj(data)
        correction_num = int(user_input[message.chat.id]['date_difference']) - 2
        forecast_msg = (
            f"{weather_data.location.name} ({weather_data.location.region}):{weather_data.forecast.forecastday[correction_num].date}\n"
            f"Maximum temperature: {weather_data.forecast.forecastday[correction_num].day.maxtemp_c}°C\n"
            f"Minimum temperature: {weather_data.forecast.forecastday[correction_num].day.mintemp_c}°C\n"
            f"Wind up to {round(weather_data.forecast.forecastday[correction_num].day.maxwind_kph / 3.6)} m/s\n"
            f"Precipitation: {weather_data.forecast.forecastday[correction_num].day.daily_chance_of_rain if weather_data.current.temp_c > 0 else weather_data.forecast.forecastday[1].day.daily_chance_of_snow}%\n"
            f"{weather_data.forecast.forecastday[correction_num].day.condition.text}")
        await bot.send_message(message.chat.id, forecast_msg)
        log.info(f"weather_forecast: Success")
    except Exception as e:
        log.error("An error occurred: %s", str(e))
        log.error(traceback.format_exc())
        await bot.send_message(message.chat.id, f"Error")
    except ValidationError as e:
        await bot.send_message(message.chat.id, f"Error data validation")
        log.error(f"weather_forecast: Validation error {e}")


@bot.message_handler(commands=['forecast_for_several_days'])
async def forecast_for_several_days(message):
    try:
        await bot.send_message(message.chat.id,
                               f'In this section, you can get the weather forecast for several days.\n'
                               f'Enter the number of days (from 1 to 10):')
        user_input[message.chat.id]['qty_days'] = 'waiting value'
    except Exception as e:
        log.error("An error occurred: %s", str(e))
        log.error(traceback.format_exc())
        await bot.send_message(message.chat.id, 'An error occurred. Please try again later.')


async def get_forecast_several(message):
    try:
        qty_days = int(message.text)
        log.debug(f"User requested weather forecast {qty_days} days: {user_input[message.chat.id]['city']}")
        if 1 <= qty_days <= 10:
            qty_days += 1
        else:
            await bot.send_message(message.chat.id, 'Qty days must be от 1 до 10')
            return
    except ValueError:
        await bot.send_message(message.chat.id, 'Invalid input format')
        log.debug("forecast_for_several_days: Invalid input format")
        return
    except Exception as e:
        log.error("An error occurred: %s", str(e))
        log.error(traceback.format_exc())

    url_forecast_several = f'http://api.weatherapi.com/v1/forecast.json?key={API_KEY_weather}&q={user_input[message.chat.id]["city"]}&days={qty_days}&aqi=no&alerts=no'
    try:
        data = get_response(message, url_forecast_several, bot)
        weather_data = WeatherData.parse_obj(data)
        for day_num in range(1, len(weather_data.forecast.forecastday)):
            forecast = weather_data.forecast.forecastday[day_num]
            precipitation = weather_data.forecast.forecastday[day_num].day.condition
            await bot.send_message(message.chat.id,
                f"{weather_data.location.name} ({weather_data.location.region}):{weather_data.forecast.forecastday[day_num].date}\n"
                f"Maximum temperature: {forecast.day.maxtemp_c}°C\n"
                f"Minimum temperature: {forecast.day.mintemp_c}°C\n"
                f"Wind up to {round(forecast.day.maxwind_kph / 3.6)} m/s\n"
                f"Humidity: {forecast.day.avghumidity}% \n"
                f"Precipitation probability: {forecast.day.daily_chance_of_rain if forecast.day.avgtemp_c > 0 else forecast.day.daily_chance_of_snow}%\n"
                f"{precipitation.text}"
            )
        log.info(f"several forecast : Success")
    except Exception as e:
        log.error("An error occurred: %s", str(e))
        log.error(traceback.format_exc())
        await bot.send_message(message.chat.id, f"Error")
    except ValidationError as e:
        log.error(e)
    return


@bot.message_handler(commands=['weather_statistic'])
async def statistic(message):
    try:
        today_date = date.today()
        log.debug(f"User requested weather statistic: {user_input[message.chat.id]['city']}")
        for days in range(1, 8):
            #  TODO: duplication of code
            statistic_date = today_date - timedelta(days=days)
            url_statistic = f'https://api.weatherapi.com/v1/history.json?key={API_KEY_weather}&q={user_input[message.chat.id]["city"]}&dt={statistic_date}'
            data = get_response(message, url_statistic, bot)
            day_details = DayDetails.parse_obj(data['forecast']['forecastday'][0]['day'])
            day_details_data = data['forecast']['forecastday'][0]['date']
            precipitation = Condition.parse_obj(data['forecast']['forecastday'][0]['day']['condition'])
            location = Location.parse_obj(data['location'])
            msg_statistic = (
                f"{location.name} ({location.region}): {day_details_data}\n"
                f"Temperature: Max: {day_details.maxtemp_c}°C, Min: {day_details.mintemp_c}°C, {precipitation.text} \n"
            )
            await bot.send_message(message.chat.id, msg_statistic)
        log.info(f"statistic : Success")
    except Exception as e:
        log.error("An error occurred: %s", str(e))
        log.error(traceback.format_exc())
        await bot.send_message(message.chat.id, f"Error")
    except ValidationError as e:
        await bot.send_message(message.chat.id, f"Error")
        log.error(f"statistic : Validation error {e}")


@bot.message_handler(commands=['prediction'])
async def prediction(message):
    try:
        today_date = date.today()
        log.debug(f"User requested weather prediction: {user_input[message.chat.id]['city']}")
        avgtemp_c_7days = set()
        for days in range(1, 8):
            statistic_date = today_date - timedelta(days=days)
            url_prediction = f'https://api.weatherapi.com/v1/history.json?key={API_KEY_weather}&q={user_input[message.chat.id]["city"]}&dt={statistic_date}'
            data = get_response(message, url_prediction, bot)
            day_details = DayDetails.parse_obj(data['forecast']['forecastday'][0]['day'])
            avgtemp_c_7days.add(day_details.avgtemp_c)
        avgtemp_c_7days = round(sum(avgtemp_c_7days) / len(avgtemp_c_7days))
        avgtemp_c_3days = set()
        for days in range(3):
            url_forecast_several = f'http://api.weatherapi.com/v1/forecast.json?key={API_KEY_weather}&q={user_input[message.chat.id]["city"]}&days=3&aqi=no&alerts=no'
            data = get_response(message, url_forecast_several, bot)
            for day_num in range(1, len(data['forecast']['forecastday'])):
                weather_data = WeatherData.parse_obj(data)
                forecast_data = weather_data.forecast.forecastday[day_num]
                avgtemp_c_3days.add(forecast_data.day.avgtemp_c)

        avgtemp_c_3days = round(sum(avgtemp_c_3days) / len(avgtemp_c_3days))
        if avgtemp_c_7days < avgtemp_c_3days:
            await bot.send_message(message.chat.id,
                                   f"The average temperature in the next 3 days will be {avgtemp_c_3days}°C, which is {avgtemp_c_3days - avgtemp_c_7days}°C warmer than the last week")
        elif avgtemp_c_7days > avgtemp_c_3days:
            await bot.send_message(message.chat.id,
                                   f"The average temperature in the next 3 days will be {avgtemp_c_3days}°C, which is {avgtemp_c_7days - avgtemp_c_3days}°C colder than the last week")
        else:
            await bot.send_message(message.chat.id,
                                   f"The average temperature in the next 3 days will be {avgtemp_c_3days}°C, the temperature remains the same as in the last 7 days")
        log.info(f"Prediction : Success")

    except ZeroDivisionError as e:
        await bot.send_message(message.chat.id, f"Error, please try again")
        log.error(f"statistic : Validation error {e}")
    except Exception as e:
        log.error("An error occurred: %s", str(e))
        log.error(traceback.format_exc())
        await bot.send_message(message.chat.id, f"Error, please try again")