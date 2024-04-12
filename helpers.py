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
        return f"Ветер {direction[win_dir]} {wind_ms}м/с (с порывами до {max_wind_ms} м/с)"
    else:
        return "Направление ветра неизвестно"


def weather_condition(precipitation: str) -> str:
    weather_dict = {
        "Sunny": "Солнечно",
        "Partly Cloudy": "Переменная облачность",
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
    if precipitation in weather_dict:
        return weather_dict[precipitation]
    else:
        return precipitation
