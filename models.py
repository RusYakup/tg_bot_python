from pydantic import BaseModel, conlist
from typing import List


class Condition(BaseModel):
    text: str
    icon: str
    code: int


class DayDetails(BaseModel):
    maxtemp_c: float
    maxtemp_f: float
    mintemp_c: float
    mintemp_f: float
    avgtemp_c: float
    avgtemp_f: float
    maxwind_mph: float
    maxwind_kph: float
    totalprecip_mm: float
    totalprecip_in: float
    totalsnow_cm: float
    avgvis_km: float
    avgvis_miles: float
    avghumidity: int
    daily_will_it_rain: int
    daily_chance_of_rain: int
    daily_will_it_snow: int
    daily_chance_of_snow: int
    condition: dict
    uv: float


class Location(BaseModel):
    name: str
    region: str
    country: str
    lat: float
    lon: float
    tz_id: str
    localtime_epoch: int
    localtime: str


class Current(BaseModel):
    last_updated: str
    temp_c: float
    temp_f: float
    is_day: int
    condition: dict
    wind_kph: float
    wind_dir: str
    feelslike_c: float
    humidity: int


class ForecastForecastDay(BaseModel):
    date: str
    date_epoch: int
    day: DayDetails


class WeatherData(BaseModel):
    location: Location
    current: Current
    forecast: dict


class Locations(BaseModel):
    name: str
    region: str
    country: str
    lat: float
    lon: float
    tz_id: str
    localtime_epoch: int
    localtime: str


class StatisticsWeather(BaseModel):
    Location: Locations
    forecast: dict
