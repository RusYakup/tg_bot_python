import os
import telebot
from dotenv import load_dotenv, find_dotenv
import requests
import json

load_dotenv(find_dotenv())

bot = telebot.TeleBot(os.environ['TOKEN'])

API_KEY_weather = (os.environ['API_KEY'])


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "Добро пожаловать в наш бот! ")
    bot.send_message(message.chat.id, "Введите название города")
    bot.register_next_step_handler(message, weather)


@bot.message_handler(commands=['change_city'])
def change_city(message):
    bot.send_message(message.chat.id, "Введите название города")
    bot.register_next_step_handler(message, weather)



@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.chat.id, "/help - помощь\n/change_city - изменить город\n/Current_weather - погода сегодня")



@bot.message_handler(comands=['Current weather'])
def weather(message):
    city = message.text
    # bot.send_message(message.chat.id, f'Город настроен на: {city.title()}')
    response = requests.get(f'http://api.weatherapi.com/v1/current.json?key={API_KEY_weather}&q={city}')
    data = json.loads(response.text)
    print(data)
    try:
        if response.status_code == 200:
            bot.send_message(message.chat.id, f'Город настроен на: {city.title()}')
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
                     f'Сейчас в {location["name"]} ({location["region"]}):\n\n Температура {current_weather["temp_c"]}°C (ощущается как {current_weather["feelslike_c"]}°C)\n Ветер {wind()} '
                     f'{round(current_weather["wind_kph"] / 3.6)} м/с\n Влажность {current_weather["humidity"]} %')


@bot.message_handler(commands=['weather_forecast'])
def get_weather(message):
    bot.send_message(message.chat.id, f'Введите дату в формате ГГГГ-ММ-ДД')
    bot.register_next_step_handler(message, )


bot.infinity_polling()
