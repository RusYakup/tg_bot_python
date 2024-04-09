import datetime

def wind(key: str) -> str:
    direction = {
        'N': "Северный",
        'NE': "Северо восточный",
        'E': "Восточный",
        'ENE': "Восточно-северо-восточный",
        'S': "Южный",
        'SW': "Юго западный",
        'W': "Западный",
        'NW': "Северо западный",
        'SSE': "Юго-юго-восточный ",
        'SE': "Северный юго-восточный",
        'SSW': "Юго-юго-западный ",
        'SW': "Юго западный",
        'WSW': "Западно-юго-западный ",
        'WNW': "Западно-северо-западный ",
        'NW': "Северный западный",
        'NNW': "Северо-северо-западный "
    }

    if key in direction:
        return direction[key]
    else:
        return "Направление ветра неизвестно"



def get_today_date():
    return datetime.date.today().strftime('%Y-%m-%d')

today_date = get_today_date()





