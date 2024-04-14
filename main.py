import os
import telebot
import logging
from dotenv import load_dotenv, find_dotenv
import requests
import json
from helpers import wind
from helpers import weather_condition
from models import *
from pydantic import ValidationError
from datetime import date, datetime, timedelta
import time

# TODO: Need to use logging library to print logs. Log level must be adjustable via env variables. Detail logs needed
#  for debugging should use with debug log level. Logs that used to make clearly what is going on in the app,
#  can use info log level.

load_dotenv(find_dotenv())
# bot = telebot.TeleBot(os.environ['TOKEN'])


# TODO: need to check that TOKEN and API_KEY are defined via environment variables. In other case need to exit the app
# TOKEN = os.environ.get('TOKEN', None)
# if TOKEN is None:
#     print('TOKEN is not set. Please provide a telegram bot token.')
#     exit(1)
# If token is defined, we check that it's correct by accessing the API of telegram. Code that checks correctness of bot
# token should put to the separate function that return bool type. If token is not correct, the app must exit
TOKEN = os.environ['TOKEN']
if TOKEN:
    bot = telebot.TeleBot(os.environ['TOKEN'])
    response = requests.get(f'https://api.telegram.org/bot{os.environ["TOKEN"]}/getMe')

    if response.status_code == 200:
        info = response.json()
        if info['ok'] == True:
            print("Token tg bot verified: " + info['result']['username'])
        else:
            print('Error response. Please check the bot token')
    else:
        print('Problems accessing the API. Please check your token and internet connection')

# TODO: the same comment as for TOKEN
API_KEY_weather = (os.environ['API_KEY'])
# TODO: The app must write to the log error and exit in case when API_KEY or TOKEN is not defined via environment variables
if API_KEY_weather:
    response = requests.get(f'http://api.weatherapi.com/v1/current.json?key={API_KEY_weather}&q=Kazan')
    if response.status_code == 200:
        data = response.json()
        if 'error' in data:
            print("There was an error using the switch. Please check that the API switch is correct")
        else:
            print("The API key is correct. Weather data successfully received.")
    else:
        print("Problems accessing the API. Please check your key and internet connection.")
else:
    print("API_KEY_weather is not set. Please provide a valid API key.")


def get_response(message, api_url: str) -> json:
    try:
        response = requests.get(api_url)
        data = json.loads(response.text)
        if response.status_code == 200:
            return json.loads(response.text)
        elif response.status_code == 400:
            error_code = data['error']['code']
            if error_code == 1006:
                bot.send_message(message.chat.id, "Город не найден, проверьте правильность названия города")
                print("Город не найден Response 400: code 1006")
            elif error_code == 9999:
                bot.send_message("Сервер временно недоступен, попробуйте позже")
                print("Сервер временно недоступен Response 400: code 9999")
            elif error_code == 1005:
                print("URL-адрес запроса API недействителен. Response 400: code 1005")
            else:
                print("Неизвестная ошибка Response 400")
                bot.send_message("Неизвестная ошибка")
        elif response.status_code == 403:
            print(f"Response 403: {data['error']['message']}")
            bot.send_message("Произошла техническая ошибка, попробуйте позже или обратитесь в поддержку")
        else:
            print(f"Response {response.status_code}: {data['error']['message']}")
            bot.send_message("Ошибка получения данных о погоде, попробуйте позже")
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка")
        print(e)


cityy = str


@bot.message_handler(commands=['start'])
def start_message(message):
    kb_reply = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    kb_in_line = telebot.types.InlineKeyboardMarkup()  # Variable is not used -> need to remove
    btn1 = telebot.types.KeyboardButton(text="Определить местоположение",
                                        request_location=True)  # Variable is redeclared in the next line -> useless
    btn1 = telebot.types.KeyboardButton(text="Изменить город", request_location=True)
    kb_reply.add(btn1)

    bot.send_message(message.chat.id,
                     f'Привет! Я - WeatherForecastBot, твой личный помощник для получения точного прогноза погоды.'
                     f' Я могу предоставить тебе информацию о погоде в любом городе. Просто напиши мне название '
                     f'города, и я скажу тебе, что тебя ждет! Начнем?', reply_markup=kb_reply)

    # TODO: It's not clear what kind of bot it is for user. Need to add more context in the greeting message.
    # Something like: Hello, I am ...... I can help you with ... Press needed button...
    change_city(message)


# Обработчик местоположения пользователя
@bot.message_handler(content_types=['location'])
def get_coordinates(message):
    global cityy
    latitude, longitude = message.location.latitude, message.location.longitude
    local = f'{latitude},{longitude}'
    cityy = local
    print(f"Пользователь выбрал город по локации: {cityy}")
    weather(message)


@bot.message_handler(commands=['change_city'])
def change_city(message):
    bot.send_message(message.chat.id, "Введите название города:")
    bot.register_next_step_handler(message, add_city)


def add_city(message):
    city_user = message.text
    global cityy
    cityy = city_user
    print(f"Пользователь сменил город: {cityy}")

    weather(message)


@bot.message_handler(commands=['help'])
def help_message(message):
    help_messages = (
        ('help', 'помощь'),
        ('change_city', 'изменить город'),
        ('current_weather', 'погода сегодня'),
        ('weather_forecast', 'погода на нужную дату'),
        ('forecast_for_several_days', 'погода на несколько дней'),
        ('wheather_statistic', 'статистика за послдение 7 дней')
    )
    full_msg = '\n'.join([f'/{command} - {description}' for command, description in help_messages])

    bot.send_message(message.chat.id, full_msg)


@bot.message_handler(commands=['current_weather'])
def weather(message):
    url_current = f'http://api.weatherapi.com/v1/forecast.json?key={API_KEY_weather}&q={cityy}'
    try:

        data = get_response(message, url_current)
        # response.raise_for_status()
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
        bot.send_message(message.chat.id, current_msg)
        return print("current_weather: Данные успешно обработаны")
    except Exception as e:
        print(f"Произошла ошибка при выполнении запроса: {e}")
        bot.send_message(message.chat.id, f"Произошла ошибка при выполнении запроса")

date_difference = []  # list of days between today and specific date for weather forecast

today_date = date.today()


@bot.message_handler(commands=['weather_forecast'])
def weather_forecast(message):
    timedelta  # TODO: Statement seems to have no effect
    max_date = today_date + timedelta(days=10)
    bot.send_message(message.chat.id, f'Введите дату в формате ГГГГ-ММ-ДД в диапозоне от {today_date} до {max_date}:')
    bot.register_next_step_handler(message, add_day)


def add_day(message):
    try:
        input_date = datetime.strptime(message.text, "%Y-%m-%d").date()
        print(input_date)
        if (input_date - today_date).days <= 10:
            date_difference.append((input_date - today_date).days + 1)
            if len(date_difference) > 1:
                date_difference.pop(0)
            get_weather_forecast(message)
        else:
            max_date = today_date + timedelta(days=10)
            bot.send_message(message.chat.id, f'Введенная дата должна быть не дальше {max_date}.')
    except ValueError:
        bot.send_message(message.chat.id, "Неверный формат даты. Введите дату в формате ГГГГ-ММ-ДД")


def get_weather_forecast(message):
    # TODO: the same comment as before
    url_forecast = f'http://api.weatherapi.com/v1/forecast.json?key={API_KEY_weather}&q={cityy}&days={date_difference[0]}&aqi=no&alerts=no'
    try:
        data = get_response(message, url_forecast)
        weather_data = WeatherData.parse_obj(data)
        current_weather = weather_data.current
        correction_num = int(date_difference[0] - 1)
        forecast_data = ForecastForecastDay.parse_obj(data['forecast']['forecastday'][correction_num])
        location = weather_data.location
        precipitation = Condition.parse_obj(data['forecast']['forecastday'][0]['day']['condition'])
        forecast_weather_msg = (
            f"Предоставлен прогноз на {forecast_data.date}\n"
            f"{location.name} ({location.region}):\n"
            f"Максимальная температура: {forecast_data.day.maxtemp_c}°C\n"
            f"Минимальная температура: {forecast_data.day.mintemp_c}°C\n"
            f"{wind(current_weather.wind_dir, current_weather.wind_kph, forecast_data.day.maxwind_kph)}\n"
            f"Влажность {forecast_data.day.avghumidity}% \n"
            f"Веротность осадков: {forecast_data.day.daily_chance_of_rain if forecast_data.day.avgtemp_c > 0 else forecast_data.day.daily_chance_of_snow}%\n"
            f"{weather_condition(precipitation.text)}")
        bot.send_message(message.chat.id, forecast_weather_msg)
        print(f"weather_forecast: Данные успешно обработаны")
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка")
        print(e)
        print(f"weather_forecast: Ошибка при обработке данных")


@bot.message_handler(commands=['forecast_for_several_days'])
def forecast_for_several_days(message):
    bot.send_message(message.chat.id,
                     f'В данном разделе можно получить прогноз погоды на несколько дней.\n'
                     f' Введите количество дней(от 1 до 10):')
    bot.register_next_step_handler(message, get_forecast_several)


def get_forecast_several(message):
    try:
        qty_days = int(message.text)
        if qty_days >= 1 and qty_days <= 10:
            qty_days += 1
        else:
            bot.send_message(message.chat.id, 'Количество дней должно быть от 1 до 10')
    except ValueError:
        bot.send_message(message.chat.id, 'Неверный формат ввода')
        return

    url_forecast_several = f'http://api.weatherapi.com/v1/forecast.json?key={API_KEY_weather}&q={cityy}&days={qty_days}&aqi=no&alerts=no'
    try:
        print(qty_days)
        data = get_response(message, url_forecast_several)
        weather_data = WeatherData.parse_obj(data)
        current_weather = weather_data.current
        location = weather_data.location

        for day_num in range(1, len(data['forecast']['forecastday'])):
            precipitation = Condition.parse_obj(data['forecast']['forecastday'][day_num]['day']['condition'])
            print(precipitation.text)
            forecast_data = ForecastForecastDay.parse_obj(data['forecast']['forecastday'][day_num])
            forecast_msg = (
                f"Прогноз на {forecast_data.date}\n"
                f"{location.name} ({location.region}):\n"
                f"Максимальная температура: {forecast_data.day.maxtemp_c}°C\n"
                f"Минимальная температура: {forecast_data.day.mintemp_c}°C\n"
                f"{wind(current_weather.wind_dir, current_weather.wind_kph, forecast_data.day.maxwind_kph)}\n"
                f"Влажность {forecast_data.day.avghumidity}% \n"
                f"Вероятность осадков: {forecast_data.day.daily_chance_of_rain if forecast_data.day.avgtemp_c > 0 else forecast_data.day.daily_chance_of_snow}%\n"
                f"{weather_condition(precipitation.text)}")

            bot.send_message(message.chat.id, forecast_msg)
            print(f"several forecast : Данные успешно обработаны")
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка")
        print(e)
        print(f"several forecast : Ошибка при обработке данных")
    return


@bot.message_handler(commands=['wheather_statistic'])
def statistic(message):
    try:
        for days in range(7):
            statistic_date = today_date - timedelta(days=days)
            url_statistic = f'https://api.weatherapi.com/v1/history.json?key={API_KEY_weather}&q={cityy}&dt={statistic_date}'
            data = get_response(message, url_statistic)
            day_detailss = data['forecast']['forecastday'][0]['day']
            day_details = DayDetails.parse_obj(data['forecast']['forecastday'][0]['day'])
            day_details_data = data['forecast']['forecastday'][0]['date']
            precipitation = Condition.parse_obj(data['forecast']['forecastday'][0]['day']['condition'])

            location = Locations.parse_obj(data['location'])
            msg_statistic = (
                f"{location.name} ({location.region}):  {day_details_data}\n"
                f"Температура: Max: {day_details.maxtemp_c}°C, Min: {day_details.mintemp_c}°C, {weather_condition(precipitation.text)} \n"
            )

            bot.send_message(message.chat.id, msg_statistic)
            print(f"statistic : Данные успешно обработаны")

    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка")
        print(e)
        print(f"statistic : Ошибка при обработке данных")


bot.infinity_polling()
