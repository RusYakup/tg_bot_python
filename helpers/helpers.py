import json
import requests
import logging
import sys
from telebot.async_telebot import AsyncTeleBot


def check_bot_token(token):
    url = f"https://api.telegram.org/bot{token}/getMe"
    response = requests.get(url)
    info = response.json()

    if response.status_code == 200:
        logging.info("Token tg bot verified: " + info['result']['username'])
    else:
        logging.error("Token tg bot not verified")


def check_api_key(api_key):
    url = f'http://api.weatherapi.com/v1/current.json?key={api_key}&q=Kazan'
    response = requests.get(url)
    if response.status_code == 200:
        logging.info("The API key is correct.")
    else:
        logging.error("The API key is incorrect.")


def wind(win_dir: str, wind_kph: float, max_wind_kph: float) -> str:
    """
        1) translates wind direction from English to Russian
        2) converts wind speed km/h to m/s
        Args:
        win_dir (str): The direction of the wind in English.
        wind_kph (float): The speed of the wind in kilometers per hour.
        max_wind_kph (float): The maximum speed of the wind in kilometers per hour.
        Returns:
        str: Sentence indicating wind direction, m/s speed and maximum wind speed on that day
        """
    direction = {
        'N': "Северный",
        'NNE': "Северо-северо-восточный",
        'NE': "Северо восточный",
        'ENE': "Восточно-северо-восточный",
        'E': "Восточный",
        'ESE': "Восточно-юго-восточный",
        'SE': "Северный юго-восточный",
        'SSE': "Юго-юго-восточный",
        'S': "Южный",
        'SSW': "Юго-юго-западный",
        'SW': "Юго западный",
        'WSW': "Западно-юго-западный",
        'W': "Западный",
        'WNW': "Западно-северо-западный",
        'NW': "Северный западный",
        'NNW': "Северо-северо-западный"
    }
    wind_ms = round(wind_kph / 3.6)
    max_wind_ms = round(max_wind_kph / 3.6)
    if win_dir in direction:
        return f"Wind {direction[win_dir]} {wind_ms} m/s (with maximum wind speed of {max_wind_ms} m/s)"
    else:
        logging.debug("Wind direction is unknown.")
        return "Wind direction is unknown."


def weather_condition(precipitation: str) -> str:
    weather_dict = {
        "Sunny": "Солнечно",
        "Partly cloudy": "Переменная облачность",
        "Cloudy": "Облачно",
        "Overcast": "Пасмурная погода",
        "Mist": "Туман",
        "Patchy rain possible": "Возможен кратковременный дождь",
        "Patchy snow possible": "Возможен кратковременный снег",
        "Patchy sleet possible": "Возможен кратковременный мокрый снег",
        "Patchy freezing drizzle possible": "Возможен кратковременный ледяной дождь",
        "Thundery outbreaks possible": "Возможны грозовые вспышки",
        "Blowing Snow": "Низовая метель",
        "Blizzard": "Метель",
        "Fog": "Туман",
        "Freezing fog": "Ледяной туман",
        "Patchy light drizzle": "Небольшой мелкий дождь",
        "Light drizzle": "Легкая морось",
        "Freezing drizzle": "Изморозь",
        "Heavy freezing drizzle": "Сильный ледяной дождь",
        "Patchy light rain": "Небольшой дождь",
        "Light rain": "Легкий дождь",
        "Moderate rain at times": "Временами умеренный дождь",
        "Moderate rain": "Умеренный дождь",
        "Heavy rain at times": "Временами сильный дождь",
        "Heavy rain": "Ливень",
        "Light freezing rain": "Легкий ледяной дождь",
        "Moderate or heavy freezing rain": "Умеренный или сильный ледяной дождь",
        "Light sleet": "Легкий мокрый снег",
        "Moderate or heavy sleet": "Умеренный или сильный мокрый снег",
        "Patchy light snow": "Небольшой мелкий снег",
        "Light snow": "Легкий снег",
        "Patchy moderate snow": "Неровный умеренный снег",
        "Moderate snow": "Умеренный снег",
        "Patchy heavy snow": "Неровный сильный снег",
        "Heavy snow": "Сильный снегопад",
        "Ice pellets": "Ледяная крупа",
        "Light rain shower": "Небольшой дождь моросит",
        "Moderate or heavy rain shower": "Умеренный или сильный ливень",
        "Torrential rain shower": "Проливной ливень",
        "Light sleet showers": "Небольшой ливень с мокрым снегом",
        "Moderate or heavy sleet showers": "Умеренный или сильный ливень с мокрым снегом",
        "Light snow showers": "Легкий снегопад",
        "Moderate or heavy snow showers": "Умеренный или сильный снегопад",
        "Light showers of ice pellets": "Легкий дождь ледяных крупинок",
        "Moderate or heavy showers of ice pellets": "Умеренные или сильные ливни ледяной крупы",
        "Patchy light rain with thunder": "Небольшой дождь с грозой",
        "Moderate or heavy rain with thunder": "Умеренный или сильный дождь с грозой",
        "Patchy light snow with thunder": "Небольшой снег с грозой",
        "Moderate or heavy snow with thunder": "Умеренный или сильный снег с грозой",
        "Patchy rain nearby": "Возможен кратковременный дождь",
    }
    if precipitation.capitalize() in weather_dict:
        return weather_dict[precipitation]
    else:
        logging.error(f"Unknown precipitation: {precipitation}")
        return precipitation


def get_response(message, api_url: str, bot: AsyncTeleBot) -> json:
    try:
        response = requests.get(api_url)
        data = json.loads(response.text)
        if response.status_code == 200:
            logging.debug(f"Response 200")
            return json.loads(response.text)
        elif response.status_code == 400:
            error_code = data['error']['code']
            if error_code == 1006:
                bot.send_message(message.chat.id, "Город не найден, проверьте правильность названия города")
                logging.error("Город не найден Response 400: code 1006")
                exit(1)
            elif error_code == 9999:
                bot.send_message("Сервер временно недоступен, попробуйте позже")
                logging.error("Сервер временно недоступен Response 400: code 9999")
            elif error_code == 1005:
                logging.error("URL-адрес запроса API недействителен. Response 400: code 1005")
            else:
                logging.error("Неизвестная ошибка Response 400")
                bot.send_message("Неизвестная ошибка")
        elif response.status_code == 403:
            logging.error(f"Response 403: {data['error']['message']}")
            bot.send_message("Произошла техническая ошибка, попробуйте позже или обратитесь в поддержку")
        else:
            logging.error(f"Response {response.status_code}: {data['error']['message']}")
            bot.send_message("Ошибка получения данных о погоде, попробуйте позже")
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка")
        logging.error(e)


# async def get_response(message, api_url: str, bot: AsyncTeleBot) -> json:
#     try:
#         async with aiohttp.ClientSession() as session:
#             async with session.get(api_url) as response:
#                 data = await response.json()
#                 if response.status == 200:
#                     logging.debug(f"Response 200")
#                     return data
#                 elif response.status == 400:
#                     error_code = data['error']['code']
#                     if error_code == 1006:
#                         await bot.send_message(message.chat.id, "Город не найден, проверьте правильность названия города")
#                         logging.error("Город не найден Response 400: code 1006")
#                         exit(1)
#                 elif response.status == 403:
#                     logging.error(f"Response 403: {data['error']['message']}")
#                     await bot.send_message(message.chat.id, "Произошла техническая ошибка, попробуйте позже или обратитесь в поддержку")
#                 else:
#                     logging.error(f"Response {response.status}: {data['error']['message']}")
#                     await bot.send_message(message.chat.id, "Ошибка получения данных о погоде, попробуйте позже")
#     except Exception as e:
#         await bot.send_message(message.chat.id, f"Произошла ошибка")
#         logging.error(e)


def logging_config():
    loger = logging.getLogger()
    loger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    loger.addHandler(handler)
    logging.info("Logging Configured")
    return loger
