import os
import telebot
from dotenv import load_dotenv, find_dotenv
from helpers.helpers import wind, get_response, weather_condition,logging_config # check_bot_token, check_api_key,
from helpers.models import *
from pydantic import ValidationError
import asyncio
from telebot.async_telebot import AsyncTeleBot

# TODO: Need to use logging library to print logs. Log level must be adjustable via env variables. Detail logs needed
#  for debugging should use with debug log level. Logs that used to make clearly what is going on in the app,
#  can use info log level.

loger = logging_config()
load_dotenv(find_dotenv())

TOKEN = os.environ['TOKEN']
# if not check_bot_token(TOKEN):
#     logging.critical("TOKEN is not set or is empty. Please provide a valid token.")
#     exit()

bot = AsyncTeleBot(os.environ['TOKEN'])

API_KEY_weather = (os.environ['API_KEY'])
# if not check_api_key(API_KEY_weather):
#     logging.critical("API_KEY is not set or is empty. Please provide a valid Api key.")
#     exit()

city = "Moskva"  # default city to the bot.


@bot.message_handler(commands=['start'])
async def start_message(message):
    loger.info("Пользователь запустил бота")
    kb_reply = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    btn1 = telebot.types.KeyboardButton(text="Определить местоположение",
                                        request_location=True)  # Variable is redeclared in the next line -> useless
    kb_reply.add(btn1)
    await bot.send_message(message.chat.id,
                     f'Привет! Я - WeatherForecastBot, твой личный помощник для получения точного прогноза погоды.'
                     f' Я могу предоставить тебе информацию о погоде в любом городе. Просто напиши мне название '
                     f'города или поделитесь местоположением, и я скажу тебе, что тебя ждет! Начнем?'
                     f'Вот команды, которые я знаю: \n'
                     f'/help - помощь\n'
                     f'/change_city - изменение города\n'
                     f'/current_weather - текущая погода\n'
                     f'/weather_forecast - прогноз погоды на нужную дату\n'
                     f'/forecast_for_several_days - прогноз погоды на несколько дней (от 2 до 10)\n'
                     f'/weather_statistics - статистика погоды за последние 7 дней\n'
                     f'/prediction - предсказание средней температуры на 3 дня\n'
                     f'или просто нажмите меню для отображения всех команд \n', reply_markup=kb_reply)
    await change_city(message)


# Обработчик местоположения пользователя
@bot.message_handler(content_types=['location'])
def get_coordinates(message):
    global city
    latitude, longitude = message.location.latitude, message.location.longitude
    local = f'{latitude},{longitude}'
    city = local
    loger.debug(f"Пользователь выбрал город по локации: {city}")
    weather(message)


# @bot.message_handler(func=lambda message: message.text == "Изменить город")
@bot.message_handler(commands=['change_city'])
async def change_city(message):
    await bot.send_message(message.chat.id, "Введите название города:")
    await bot.register_next_step_handler(message, add_city)


async def add_city(message):
    city_user = message.text
    global city
    city = city_user
    loger.info(f"Пользователь сменил город: {city}")

    await weather(message)


@bot.message_handler(commands=['help'])
async def help_message(message):
    loger.info("Пользователь запросил помощь")
    help_messages = (
        ('help', 'помощь'),
        ('change_city', 'изменить город'),
        ('current_weather', 'погода сегодня'),
        ('weather_forecast', 'погода на нужную дату'),
        ('forecast_for_several_days', 'погода на несколько дней'),
        ('weather_statistic', 'статистика за послдение 7 дней'),
        ('prediction', 'предсказание на 3 дня'),
    )
    full_msg = '\n'.join([f'/{command} - {description}' for command, description in help_messages])

    await bot.send_message(message.chat.id, full_msg)


@bot.message_handler(commands=['current_weather'])
async def weather(message):
    loger.info(f"Пользователь запросил погоду сегодня: {city}")
    url_current = f'http://api.weatherapi.com/v1/forecast.json?key={API_KEY_weather}&q={city}'
    try:

        data = get_response(message, url_current, bot)
        weather_data = WeatherData.parse_obj(data)
        current_weather = weather_data.current
        forecast = DayDetails.parse_obj(data['forecast']['forecastday'][0]['day'])
        location = weather_data.location
        precipitation = Condition.parse_obj(data['forecast']['forecastday'][0]['day']['condition'])
        current_msg = (
            f"{location.name} ({location.region}): {location.localtime}\n"
            f"Температура: {current_weather.temp_c}°C (ощущается как {current_weather.feelslike_c}°C)\n"
            f"Максимальная температура: {forecast.maxtemp_c}°C\n"
            f"Минимальная температура: {forecast.mintemp_c}°C\n"
            f"{wind(current_weather.wind_dir, current_weather.wind_kph, forecast.maxwind_kph)}\n"
            f"Влажность {current_weather.humidity}% \n"
            f"Веротность осадков: {forecast.daily_chance_of_rain if current_weather.temp_c > 0 else forecast.daily_chance_of_snow}%\n"
            f"{weather_condition(precipitation.text)}")
        await bot.send_message(message.chat.id, current_msg)
        return loger.info("current_weather: Данные успешно обработаны")
    except Exception as e:
        loger.error(f"Произошла ошибка при выполнении запроса: {e}")
        await bot.send_message(message.chat.id, f"Произошла ошибка при выполнении запроса")
    except ValidationError as e:
        loger.error(f"Неверные данные: {e}")


# date_difference = []  # list of days between today and specific date for weather forecast
#
# today_date = date.today()
#
#
# @bot.message_handler(commands=['weather_forecast'])
# def weather_forecast(message):
#     max_date = today_date + timedelta(days=10)
#     bot.send_message(message.chat.id, f'Введите дату в формате ГГГГ-ММ-ДД в диапозоне от {today_date} до {max_date}:')
#     bot.register_next_step_handler(message, add_day)
#
#
# def add_day(message):
#     try:
#         input_date = datetime.strptime(message.text, "%Y-%m-%d").date()
#         if (input_date - today_date).days <= 10:
#             date_difference.append((input_date - today_date).days + 1)
#             if len(date_difference) > 1:
#                 date_difference.pop(0)
#             get_weather_forecast(message)
#             return
#         else:
#             max_date = today_date + timedelta(days=10)
#             bot.send_message(message.chat.id, f'Введенная дата должна быть не дальше {max_date}.')
#             loger.debug("add_day: Введенная дата должна быть не дальше {max_date}.")
#             return
#     except ValueError:
#         bot.send_message(message.chat.id, "Неверный формат даты. Введите дату в формате ГГГГ-ММ-ДД")
#         loger.debug("add_day: Неверный формат даты")
#     loger.info(f"Пользователь ввел дату (weather_forecast): {message.text}")
#
#
# def get_weather_forecast(message):
#     loger.info(f"Пользователь запросил прогноз на {date_difference[0]} дней: {city}")
#     url_forecast = f'http://api.weatherapi.com/v1/forecast.json?key={API_KEY_weather}&q={city}&days={date_difference[0]}&aqi=no&alerts=no'
#     try:
#         data = get_response(message, url_forecast, bot)
#         weather_data = WeatherData.parse_obj(data)
#         current_weather = weather_data.current
#         correction_num = int(date_difference[0] - 1)
#         forecast_data = ForecastForecastDay.parse_obj(data['forecast']['forecastday'][correction_num])
#         location = weather_data.location
#         precipitation = Condition.parse_obj(data['forecast']['forecastday'][0]['day']['condition'])
#         forecast_weather_msg = (
#             f"Предоставлен прогноз на {forecast_data.date}\n"
#             f"{location.name} ({location.region}):\n"
#             f"Максимальная температура: {forecast_data.day.maxtemp_c}°C\n"
#             f"Минимальная температура: {forecast_data.day.mintemp_c}°C\n"
#             f"{wind(current_weather.wind_dir, current_weather.wind_kph, forecast_data.day.maxwind_kph)}\n"
#             f"Влажность {forecast_data.day.avghumidity}% \n"
#             f"Веротность осадков: {forecast_data.day.daily_chance_of_rain if forecast_data.day.avgtemp_c > 0 else forecast_data.day.daily_chance_of_snow}%\n"
#             f"{weather_condition(precipitation.text)}")
#         bot.send_message(message.chat.id, forecast_weather_msg)
#         loger.info(f"weather_forecast: Данные успешно обработаны")
#     except Exception as e:
#         bot.send_message(message.chat.id, f"Произошла ошибка")
#         loger.error(f"weather_forecast: Ошибка при обработке данных {e}")
#     except ValidationError as e:
#         bot.send_message(message.chat.id, f"Произошла ошибка при обработке данных")
#         loger.error(f"weather_forecast: Неверные данные {e}")
#
#
# @bot.message_handler(commands=['forecast_for_several_days'])
# def forecast_for_several_days(message):
#     bot.send_message(message.chat.id,
#                      f'В данном разделе можно получить прогноз погоды на несколько дней.\n'
#                      f' Введите количество дней(от 1 до 10):')
#     bot.register_next_step_handler(message, get_forecast_several)
#
#
# def get_forecast_several(message):
#     try:
#         qty_days = int(message.text)
#         loger.info(f"Пользователь запросил прогноз на {qty_days} дней: {city}")
#         if qty_days >= 1 and qty_days <= 10:
#             qty_days += 1
#         else:
#             bot.send_message(message.chat.id, 'Количество дней должно быть от 1 до 10')
#     except ValueError:
#         bot.send_message(message.chat.id, 'Неверный формат ввода')
#         loger.debug("forecast_for_several_days: Неверный формат ввода")
#         return
#
#     url_forecast_several = f'http://api.weatherapi.com/v1/forecast.json?key={API_KEY_weather}&q={city}&days={qty_days}&aqi=no&alerts=no'
#     try:
#         data = get_response(message, url_forecast_several, bot)
#         weather_data = WeatherData.parse_obj(data)
#         current_weather = weather_data.current
#         location = weather_data.location
#
#         for day_num in range(1, len(data['forecast']['forecastday'])):
#             precipitation = Condition.parse_obj(data['forecast']['forecastday'][day_num]['day']['condition'])
#             forecast_data = ForecastForecastDay.parse_obj(data['forecast']['forecastday'][day_num])
#
#             forecast_msg = (
#                 f"Прогноз на {forecast_data.date}\n"
#                 f"{location.name} ({location.region}):\n"
#                 f"Максимальная температура: {forecast_data.day.maxtemp_c}°C\n"
#                 f"Минимальная температура: {forecast_data.day.mintemp_c}°C\n"
#                 f"{wind(current_weather.wind_dir, current_weather.wind_kph, forecast_data.day.maxwind_kph)}\n"
#                 f"Влажность {forecast_data.day.avghumidity}% \n"
#                 f"Вероятность осадков: {forecast_data.day.daily_chance_of_rain if forecast_data.day.avgtemp_c > 0 else forecast_data.day.daily_chance_of_snow}%\n"
#                 f"{weather_condition(precipitation.text)}")
#
#             bot.send_message(message.chat.id, forecast_msg)
#         loger.info(f"several forecast : Данные успешно обработаны")
#     except Exception as e:
#         bot.send_message(message.chat.id, f"Произошла ошибка")
#         loger.error(f"several forecast : Ошибка при обработке данных {e}")
#     except ValidationError as e:
#         loger.error(e)
#     return
#
#
# @bot.message_handler(commands=['weather_statistic'])
# def statistic(message):
#     try:
#         loger.info(f"Пользователь запросил статистику: {city}")
#         for days in range(7):
#             statistic_date = today_date - timedelta(days=days)
#             url_statistic = f'https://api.weatherapi.com/v1/history.json?key={API_KEY_weather}&q={city}&dt={statistic_date}'
#             data = get_response(message, url_statistic, bot)
#             day_details = DayDetails.parse_obj(data['forecast']['forecastday'][0]['day'])
#             day_details_data = data['forecast']['forecastday'][0]['date']
#             precipitation = Condition.parse_obj(data['forecast']['forecastday'][0]['day']['condition'])
#
#             location = Locations.parse_obj(data['location'])
#             msg_statistic = (
#                 f"{location.name} ({location.region}):  {day_details_data}\n"
#                 f"Температура: Max: {day_details.maxtemp_c}°C, Min: {day_details.mintemp_c}°C, {weather_condition(precipitation.text)} \n"
#             )
#
#             bot.send_message(message.chat.id, msg_statistic)
#         loger.info(f"statistic : Данные успешно обработаны")
#
#     except Exception as e:
#         bot.send_message(message.chat.id, f"Произошла ошибка")
#         loger.error(f"statistic : Ошибка при обработке данных {e}")
#     except ValidationError as e:
#         bot.send_message(message.chat.id, f"Произошла ошибка")
#         loger.error(f"statistic : Ошибка валидации {e}")
#
#
# @bot.message_handler(commands=['prediction'])
# def prediction(message):
#     loger.info(f"Пользователь запросил prediction: {city}")
#     avgtemp_c_7days = set()
#     for days in range(7):
#         statistic_date = today_date - timedelta(days=days)
#         url_prediction = f'https://api.weatherapi.com/v1/history.json?key={API_KEY_weather}&q={city}&dt={statistic_date}'
#         data = get_response(message, url_prediction, bot)
#         day_details = DayDetails.parse_obj(data['forecast']['forecastday'][0]['day'])
#         avgtemp_c_7days.add(day_details.avgtemp_c)
#     avgtemp_c_7days = round(sum(avgtemp_c_7days) / len(avgtemp_c_7days))
#     avgtemp_c_3days = set()
#     for days in range(3):
#         url_forecast_several = f'http://api.weatherapi.com/v1/forecast.json?key={API_KEY_weather}&q={city}&days=3&aqi=no&alerts=no'
#         try:
#             data = get_response(message, url_forecast_several, bot)
#             weather_data = WeatherData.parse_obj(data)
#             location = weather_data.location
#
#             for day_num in range(1, len(data['forecast']['forecastday'])):
#                 forecast_data = ForecastForecastDay.parse_obj(data['forecast']['forecastday'][day_num])
#                 avgtemp_c_3days.add(forecast_data.day.avgtemp_c)
#         except Exception as e:
#             bot.send_message(message.chat.id, f"Произошла ошибка {e}")
#             loger.error(f"statistic : Ошибка при обработке данных {e}")
#         except ValidationError as e:
#             bot.send_message(message.chat.id, f"Произошла ошибка")
#             loger.error(f"statistic : Ошибка валидации {e}")
#
#     avgtemp_c_3days = round(sum(avgtemp_c_3days) / len(avgtemp_c_3days))
#     try:
#         if avgtemp_c_7days < avgtemp_c_3days:
#             bot.send_message(message.chat.id,
#                              f"Средняя температура в ближайшие 3 дня будет {avgtemp_c_3days}°C, это на {avgtemp_c_3days - avgtemp_c_7days}°C  теплее чем за последнюю неделю")
#         elif avgtemp_c_7days > avgtemp_c_3days:
#             bot.send_message(message.chat.id,
#                              f"Средняя температура в ближайшие 3 дня будет {avgtemp_c_3days} °C, это на  {avgtemp_c_7days - avgtemp_c_3days}°C холоднее чем за последнюю неделю")
#         else:
#             bot.send_message(message.chat.id,
#                              f"Средняя температура в ближайшие 3 дня будет {avgtemp_c_3days}°C, температура сохранилась как в последние 7 дней")
#         loger.info(f"statistic : Данные успешно обработаны")
#
#     except ZeroDivisionError as e:
#         bot.send_message(message.chat.id, f"Произошла ошибка")
#         loger.error(f"statistic : Ошибка при обработке данных {e}")
#
#     except Exception as e:
#         loger.error(f"statistic : Ошибка при обработке данных {e}")


# bot.infinity_polling()
asyncio.run(bot.polling())
