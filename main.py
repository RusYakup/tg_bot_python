import os
import telebot
from dotenv import load_dotenv, find_dotenv
import requests
import json
from helpers import *

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
                     'Привет! WeatherForecastBot - ваш надежный помощник для получения прогноза погоды.')
    # TODO: It's not clear what kind of bot it is for user. Need to add more context in the greeting message.
    # Something like: Hello, I am ...... I can help you with ... Press needed button...

    change_city(message)


@bot.message_handler(commands=['change_city'])
def change_city(message):
    bot.send_message(message.chat.id, "Введите название города:")
    bot.register_next_step_handler(message, add_city)


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


@bot.message_handler(content_types=['new_city'])
def add_city(message):
    city_user = message.text
    cityy.append(city_user)
    if len(cityy) > 1:
        cityy.pop(0)
    print(cityy)
    weather(message)


@bot.message_handler(comands=['current_weather'])
def weather(message):
    response = requests.get(f'http://api.weatherapi.com/v1/forecast.json?key={API_KEY_weather}&q={cityy[0]}')
    data = json.loads(response.text)
    print(data)
    print(today_date)
    try:
        if response.status_code == 200:
            data = json.loads(response.text)
            print(data)
            current_weather = data["current"]
            # forecast_date = data['forecast']['forecastday'][0]['date']
            forecast = data['forecast']['forecastday'][0]['day']
            location = data['location']

            if forecast["maxtemp_c"] > 2:
                bot.send_message(message.chat.id, f'{location["name"]} ({location["region"]}): {location["localtime"]}\n'
                                                  f'Температура {current_weather["temp_c"]}°C (ощущается как {current_weather["feelslike_c"]}°C)\n'
                                                  f'Максимальная температура сегодня: {round(forecast["maxtemp_c"])}°C\nМинимальная температура сегодня: {round(forecast["mintemp_c"])}°C\n'
                                                  f'Ветер {wind(current_weather["wind_dir"])} {round(current_weather["wind_kph"] / 3.6)} м/с (с порывами до '
                                                  f'{round(current_weather["gust_kph"] / 3.6)} м/с)\n'
                                                  f'Влажность {current_weather["humidity"]} %\n'
                                                  f'Вероятность дождя {forecast["daily_chance_of_rain"]}%')

            else:
                bot.send_message(message.chat.id, f'{location["name"]} ({location["region"]}): {location["localtime"]}\n'
                                                  f'Температура {current_weather["temp_c"]}°C (ощущается как {current_weather["feelslike_c"]}°C)\n'
                                                  f'Максимальная температура сегодня: {forecast["maxtemp_c"]}°C\nМинимальная температура сегодня: {forecast["mintemp_c"]}°C\n'
                                                  f'Ветер {wind(current_weather["wind_dir"])} {round(current_weather["wind_kph"] / 3.6)} м/с (с порывами до '
                                                  f'{round(current_weather["gust_kph"] / 3.6)} м/с)\n'
                                                  f'Влажность {current_weather["humidity"]} %\n'
                                                  f'Вероятность снега {forecast["daily_chance_of_snow"]}%')
        else:
            #         # TODO: is it possible to check what kind of error happened? For example: 404 - may be city not found.
            #         # 400 - bad request. 500 - server error.... We have to print proper message to the user. If some internal
            #         # error happened, we should use common context messsage
            bot.send_message(message.chat.id, "Ошибка получения данных о погоде, проверьте название города")
    #         # TODO: Need to return here?
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка: {e}")
    #     # TODO: Need to return here?


date = []


#
@bot.message_handler(commands=['weather_forecast'])
def weather_forecast(message):
    bot.send_message(message.chat.id, f'Введите дату в формате ГГГГ-ММ-ДД')
    bot.register_next_step_handler(message, get_weather_date(message))

#
# def get_weather_date(message):
#     get_date = message.text
#     date.append(get_date)
#     if len(date) > 1:
#         date.pop(0)
#     print(date)
#
#     get_weather(message)


# def get_weather(message):
#     # bot.send_message(message.chat.id, f'Введите дату в формате ГГГГ-ММ-ДД')
#     # bot.register_next_step_handler(message, get_weather_date)
#     # date = get_weather_date(message)
#     # weather_forecast_date = message.text
#     response = requests.get(
#         f'http://api.weatherapi.com/v1/future.json?key={API_KEY_weather}&q={cityy[0]}${today_date}')
#     data = json.loads(response.text)
#     print(data)
#     current_weather = data["current"]
#     forecast_date = data['forecast']['forecastday'][0]['date']
#     forecast = data['forecast']['forecastday'][0]['day']
#     location = data['location']
#
#     if forecast["maxtemp_c"] > 2:
#         bot.send_message(message.chat.id, f'{location["name"]} ({location["region"]}): {forecast_date}\n'
#                                           f'Температура {current_weather["temp_c"]}°C (ощущается как {current_weather["feelslike_c"]}°C)\n'
#                                           f'Максимальная температура сегодня: {round(forecast["maxtemp_c"])}°C\nМинимальная температура сегодня: {round(forecast["mintemp_c"])}°C\n'
#                                           f'Ветер {wind(current_weather["wind_dir"])} {round(current_weather["wind_kph"] / 3.6)} м/с (с порывами до '
#                                           f'{round(current_weather["gust_kph"] / 3.6)} м/с)\n'
#                                           f'Влажность {current_weather["humidity"]} %\n'
#                                           f'Вероятность дождя {forecast["daily_chance_of_rain"]}%')
#
#     else:
#         bot.send_message(message.chat.id, f'{location["name"]} ({location["region"]}): {forecast_date}\n'
#                                           f'Температура {current_weather["temp_c"]}°C (ощущается как {current_weather["feelslike_c"]}°C)\n'
#                                           f'Максимальная температура сегодня: {forecast["maxtemp_c"]}°C\nМинимальная температура сегодня: {forecast["mintemp_c"]}°C\n'
#                                           f'Ветер {wind(current_weather["wind_dir"])} {round(current_weather["wind_kph"] / 3.6)} м/с (с порывами до '
#                                           f'{round(current_weather["gust_kph"] / 3.6)} м/с)\n'
#                                           f'Влажность {current_weather["humidity"]} %\n'
#                                           f'Вероятность снега {forecast["daily_chance_of_snow"]}%')


#
#
bot.infinity_polling()
