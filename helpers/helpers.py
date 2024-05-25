import json
import requests
import sys
from telebot.async_telebot import AsyncTeleBot
import logging
import traceback
from typing import Any

log = logging.getLogger(__name__)



def check_bot_token(token: str) -> None:
    url = f"https://api.telegram.org/bot{token}/getMe"
    try:
        response = requests.get(url)
        response.raise_for_status()
        info = response.json()
        log.info("Token for Telegram bot verified: " + info['result']['username'])
    except requests.exceptions.RequestException as e:
        log.error("Error verifying Telegram bot token")
        log.debug(f"Exception: {e}")
        sys.exit(1)


def check_api_key(api_key: str) -> None:
    url = f'http://api.weatherapi.com/v1/current.json?key={api_key}&q=Kazan'
    # TODO: here can be exception -> need to catch it to avoid unexpected behaviour -> exit(1)
    try:
        response = requests.get(url)
        response.raise_for_status()
        info = response.json()
        log.info("The API key is correct.")
    except requests.exceptions.RequestException as e:
        log.error("Error verifying API key")
        log.debug(f"Exception: {e}")
        sys.exit(1)
    response = requests.get(url)
    if response.status_code == 200:
        log.info("The API key is correct.")
    else:
        log.error("The API key is incorrect.")
        log.debug(F"Exception traceback:\n", traceback.format_exc())
        sys.exit(1)


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
    #
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
        return f"Wind {win_dir} {wind_ms} m/s (with maximum wind speed of {max_wind_ms} m/s)"
    else:
        log.debug("Wind direction is unknown.")
        return "Wind direction is unknown."


def weather_condition(precipitation: str) -> str:
    # TODO: some messages send to chat using Russian, some using English. Need to use one language for interaction with user.
    # TODO: You can add command /set_language to adjust language by user. By default it can by English. Store use language in table in the future
    #  Need to prepare dictionary with of all sentences that used to communicate with user in English and Russian
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
        log.error(f"Unknown precipitation: {precipitation}")
        return precipitation


# TODO: Incorrect annotation of output type. json - it's a module name. Not type
def get_response(message, api_url: str, bot: AsyncTeleBot) -> Any:
    try:
        response = requests.get(api_url)
        data = json.loads(response.text)
        if response.status_code == 200:
            logging.debug(f"Response 200")
            return json.loads(response.text)
        elif response.status_code == 400:
            error_code = data.get('error', {}).get('code')
            if error_code == 1006:
                bot.send_message(message.chat.id, "City not found, please check the city name")
                logging.error("City not found - Response 400: code 1006")
                exit(1)
            elif error_code == 9999:
                bot.send_message(message.chat.id, "Server temporarily unavailable, please try again later")
                logging.error("Server temporarily unavailable - Response 400: code 9999")
            elif error_code == 1005:
                bot.send_message(message.chat.id, "Error in API request, please try again later")
                logging.error("Invalid API request URL - Response 400: code 1005")
            else:
                logging.error("Unknown error - Response 400")
                logging.error(traceback.format_exc())
                bot.send_message(message.chat.id, "Unknown error")
        elif response.status_code == 403:
            logging.error(f"Response 403: {data.get('error', {}).get('message')}")
            bot.send_message(message.chat.id, "Technical error occurred, please try again later or contact support")
        else:
            logging.error(f"Response {response.status_code}: {data.get('error', {}).get('message')}")
            bot.send_message(message.chat.id, "Error retrieving weather data, please try again later")
    except Exception as e:
        bot.send_message(message.chat.id, "An error occurred")
        logging.error(e)
        logging.error(f"Exception:\n",traceback.format_exc())



def logging_config(LOG_LEVEL):

    numeric_level = getattr(logging, LOG_LEVEL)
    logging.basicConfig(level=numeric_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log.info("Logging Configured")


