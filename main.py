import os
import telebot
from dotenv import load_dotenv, find_dotenv
import requests
import json

load_dotenv(find_dotenv())

bot = telebot.TeleBot(os.environ['TOKEN'])

API_KEY_weather = (os.environ['API_KEY'])

cityy = []


@bot.message_handler(commands=['start'])
def start_message(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton('/help')
    btn2 = telebot.types.KeyboardButton('/change_city')
    btn3 = telebot.types.KeyboardButton('/Current_weather')
    btn4 = telebot.types.KeyboardButton('/weather_forecast')
    markup.add(btn1, btn2, btn3, btn4)
    bot.send_message(message.chat.id, "Введите название города")
    bot.register_next_step_handler(message, add_city)


@bot.message_handler(commands=['change_city'])
def change_city(message):
    bot.send_message(message.chat.id, "Введите название города")
    bot.register_next_step_handler(message, add_city)


@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.chat.id,
                     "/help - помощь\n/change_city - изменить город\n/Current_weather - погода сегодня\n/weather_forecast - погода на нужную дату")


@bot.message_handler(content_types=['new_city'])
def add_city(message):
    city_user = message.text
    cityy.append(city_user)
    if len(cityy) > 1:
        cityy.pop(0)
    print(cityy)
    weather(message)
    print('123')


@bot.message_handler(comands=['Current weather'])
def weather(message):
    response = requests.get(f'http://api.weatherapi.com/v1/current.json?key={API_KEY_weather}&q={cityy[0]}')
    data = json.loads(response.text)
    print(data)
    try:
        if response.status_code == 200:
            # bot.send_message(message.chat.id, f'Город настроен на: {cityy[0].title()}')
            data = json.loads(response.text)
            current_weather = data["current"]
            location = data["location"]
        else:
            bot.send_message(message.chat.id, "Ошибка получения данных о погоде, проверьте название города")
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка: {e}")

    def wind():
        if current_weather["wind_dir"] == "N":
            return "Северный"
        if current_weather["wind_dir"] == "NE":
            return "Северо восточный"
        if current_weather["wind_dir"] == "E":
            return "Восточный"
        if current_weather["wind_dir"] == "ENE":
            return "Восточно-северо-восточный"
        if current_weather["wind_dir"] == "S":
            return "Южный"
        if current_weather["wind_dir"] == "SW":
            return "Юго западный"
        if current_weather["wind_dir"] == "W":
            return "Западный"
        if current_weather["wind_dir"] == "NW":
            return "Северо западный"
        if current_weather["wind_dir"] == "SSE":
            return "Юго-юго-восточный "
        if current_weather["wind_dir"] == "SE":
            return "Северный юго-восточный"
        if current_weather["wind_dir"] == "SSW":
            return "Юго-юго-западный "
        if current_weather["wind_dir"] == "SW":
            return "Юго западный"
        if current_weather["wind_dir"] == "WSW":
            return "Западно-юго-западный "
        if current_weather["wind_dir"] == "WNW":
            return "Западно-северо-западный "
        if current_weather["wind_dir"] == "NW":
            return "Северный западный"
        if current_weather["wind_dir"] == "NNW":
            return "Северо-северо-западный "
        else:
            return "Направление ветра неизвестно"

    bot.send_message(message.chat.id,
                     f'Сейчас в {location["name"]} ({location["region"]}):\n\n '
                     f'Температура {current_weather["temp_c"]}°C (ощущается как {current_weather["feelslike_c"]}°C)\n '
                     f'Ветер {wind()} {round(current_weather["wind_kph"] / 3.6)} м/с (с порывами до '
                     f'{round(current_weather["gust_kph"] / 3.6)} м/с)\n'
                     f'Влажность {current_weather["humidity"]} %')


#
# @bot.message_handler(commands=['weather_forecast'])
# def get_weather(message):
#     bot.send_message(message.chat.id, f'Введите дату в формате ГГГГ-ММ-ДД')
#     weather_date = message.text
#     response = requests.get(f'http://api.weatherapi.com/v1/current.json?key={API_KEY_weather}&q={city}&dt={weather_date}')
#     data = json.loads(response.text)
#     print(data)
#
#
#
bot.infinity_polling()
