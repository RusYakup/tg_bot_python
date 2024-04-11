import os
import telebot
from dotenv import load_dotenv, find_dotenv
import requests
import json
from helpers import *
from models import *
from pydantic import ValidationError
from datetime import date, datetime, timedelta

# TODO: Need to use logging library to print logs. Log level must be adjustable via env variables. Detail logs needed
#  for debugging should use with debug log level. Logs that used to make clearly what is going on in the app,
#  can use info log level.

load_dotenv(find_dotenv())
# bot = telebot.TeleBot(os.environ['TOKEN'])
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

cityy = []


@bot.message_handler(commands=['start'])
def start_message(message):
    # TODO: need to add possibility to choose language bu user: Russian/English. Be default use English.
    #  All further interaction with user must be using requested language

    bot.send_message(message.chat.id,
                     f'Привет! Я - WeatherForecastBot, твой личный помощник для получения точного прогноза погоды.'
                     f' Я могу предоставить тебе информацию о погоде в любом городе. Просто напиши мне название '
                     f'города, и я скажу тебе, что тебя ждет! Начнем?')
    # TODO: It's not clear what kind of bot it is for user. Need to add more context in the greeting message.
    # Something like: Hello, I am ...... I can help you with ... Press needed button...

    change_city(message)


@bot.message_handler(commands=['change_city'])
def change_city(message):
    bot.send_message(message.chat.id, "Введите название города:")
    bot.register_next_step_handler(message, add_city)


def add_city(message):
    city_user = message.text
    cityy.append(city_user)
    if len(cityy) > 1:
        cityy.pop(0)
    print(f"Пользователь сменил город: {cityy}")
    weather(message)


@bot.message_handler(commands=['help'])
def help_message(message):
    help_messages = (
        ('help', 'помощь'),
        ('change_city', 'изменить город'),
        ('current_weather', 'погода сегодня'),
        ('weather_forecast', 'погода на нужную дату')
    )
    full_msg = '\n'.join([f'/{command} - {description}' for command, description in help_messages])

    bot.send_message(message.chat.id, full_msg)


@bot.message_handler(commands=['current_weather'])
def weather(message):
    response = requests.get(f'http://api.weatherapi.com/v1/forecast.json?key={API_KEY_weather}&q={cityy[0]}')
    data = json.loads(response.text)

    try:
        if response.status_code == 200:
            weather_data = WeatherData.parse_obj(data)
            current_weather = weather_data.current
            forecast = DayDetails.parse_obj(data['forecast']['forecastday'][0]['day'])
            location = weather_data.location

            weather_msg = (
                f"{location.name} ({location.region}): {location.localtime}\n"
                f"Температура: {current_weather.temp_c}°C (ощущается как {current_weather.feelslike_c}°C)\n"
                f"Максимальная температура: {forecast.maxtemp_c}°C\n"
                f"Минимальная температура: {forecast.mintemp_c}°C\n"
                f"{wind(current_weather.wind_dir, current_weather.wind_kph, forecast.maxwind_kph)}\n"
                f"Влажность {current_weather.humidity}% \n"
                f"Веротность осадков: {forecast.daily_chance_of_rain if current_weather.temp_c > 0 else forecast.daily_chance_of_snow}%")

            bot.send_message(message.chat.id, weather_msg)
            return print("current_weather: Данные успешно обработаны")

        elif response.status_code == 400:
            error_code = data['error']['code']
            if error_code == 1006:
                bot.send_message(message.chat.id, "Город не найден, проверьте правильность названия города")
                print("Город не найден Response 400: code 1006")
            elif error_code == 9999:
                bot.send_message(message.chat.id, "Сервер временно недоступен, попробуйте позже")
                print("Сервер временно недоступен Response 400: code 9999")
            elif error_code == 1005:
                print("URL-адрес запроса API недействителен. Response 400: code 1005")
            else:
                print("Неизвестная ошибка Response 400")
                bot.send_message(message.chat.id, "Неизвестная ошибка")
        elif response.status_code == 403:
            print(f"Response 403: {data['error']['message']}")
            bot.send_message(message.chat.id,
                             "Произошла техническая ошибка, попробуйте позже или обратитесь в поддержку")
        else:
            print(f"Response {response.status_code}: {data['error']['message']}")
            bot.send_message(message.chat.id, "Ошибка получения данных о погоде, попробуйте позже")
        return "Произошла ошибка"
    except ValidationError as e:
        print(f"Ошибка валидации данных: {e}")
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка")
        print(e)
    return print("Произошла ошибка")


date_difference = []  # list of days between today and specific date for weather forecast

today_date = date.today()
@bot.message_handler(commands=['weather_forecast'])
def weather_forecast(message):

    max_date = today_date + timedelta(days=10)
    bot.send_message(message.chat.id, f'Введите дату в формате ГГГГ-ММ-ДД в диапозоне от {today_date} до {max_date}:')
    bot.register_next_step_handler(message, add_day)


def add_day(message):

    try:
        input_date = datetime.strptime(message.text, "%Y-%m-%d").date()
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
    response = requests.get(
        f'http://api.weatherapi.com/v1/forecast.json?key={API_KEY_weather}&q={cityy[0]}&days={date_difference[0]}&aqi=no&alerts=no')
    data = json.loads(response.text)
    correction_num = int(date_difference[0] - 1)
    try:
        if response.status_code == 200:
            weather_data = WeatherData.parse_obj(data)
            current_weather = weather_data.current
            forecast_data = ForecastForecastDay.parse_obj(data['forecast']['forecastday'][correction_num])
            location = weather_data.location

            forecast_weather_msg = (
                f"Предоставлен прогноз на {forecast_data.date}\n"
                f"{location.name} ({location.region}):\n"
                f"Максимальная температура: {forecast_data.day.maxtemp_c}°C\n"
                f"Минимальная температура: {forecast_data.day.mintemp_c}°C\n"
                f"{wind(current_weather.wind_dir, current_weather.wind_kph, forecast_data.day.maxwind_kph)}\n"
                f"Влажность {forecast_data.day.avghumidity}% \n"
                f"Веротность осадков: {forecast_data.day.daily_chance_of_rain if forecast_data.day.avgtemp_c > 0 else forecast_data.day.daily_chance_of_snow}%")

            bot.send_message(message.chat.id, forecast_weather_msg)
            print(f"weather_forecast: Данные успешно обработаны")
        elif response.status_code == 400:
            error_code = data['error']['code']
            if error_code == 1006:
                bot.send_message(message.chat.id, "Город не найден, проверьте правильность названия города")
                print("Город не найден Response 400: code 1006")
            elif error_code == 9999:
                bot.send_message(message.chat.id, "Сервер временно недоступен, попробуйте позже")
                print("Сервер временно недоступен Response 400: code 9999")
            elif error_code == 1005:
                print("URL-адрес запроса API недействителен. Response 400: code 1005")
            else:
                print("Неизвестная ошибка Response 400")
                bot.send_message(message.chat.id, "Неизвестная ошибка")
        elif response.status_code == 403:
            print(f"Response 403: {data['error']['message']}")
            bot.send_message(message.chat.id,
                             "Произошла техническая ошибка, попробуйте позже или обратитесь в поддержку")
        else:
            print(f"Response {response.status_code}: {data['error']['message']}")
            bot.send_message(message.chat.id, "Ошибка получения данных о погоде, попробуйте позже")
        return "Произошла ошибка"
    except ValidationError as e:
        print(f"Ошибка валидации данных: {e}")
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка:")
        print(e)
    return "Произошла ошибка"


bot.infinity_polling()
