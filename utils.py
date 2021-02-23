from telegram import ReplyKeyboardMarkup, KeyboardButton
import requests
import settings


class WeatherInfoOpenWeatherMap:
    _api_key = settings.WEATHER_APIKEY

    def __init__(self, name):
        self._city_name = name

    def _weather_info_separates(self, weather_info: dict):
        self.name = weather_info['name']

        main_info = weather_info['main']
        self.temp = main_info['temp']
        self.temp_feel = main_info['feels_like']
        self.pressure = main_info['pressure']
        self.humidity = main_info['humidity']

        self.wind_speed = weather_info['wind']['speed']

        description_and_icon = weather_info['weather'][0]
        self.description = description_and_icon['description']
        self.icon_url = f"http://openweathermap.org/img/wn/{description_and_icon['icon']}@2x.png"

    def search(self) -> bool:
        weather_info = requests.get(
            f'http://api.openweathermap.org/data/2.5/weather?'
            f'q={self._city_name}'
            f'&appid={self._api_key}&lang=ru&units=metric'
        )

        if weather_info.status_code != requests.codes.ok:
            return False

        self._weather_info_separates(weather_info.json())
        return True


def user_keyboard() -> ReplyKeyboardMarkup:
    keyboard = [
        ['/start'],
        ['/planet', '/weather', '/wordcount'],
        [KeyboardButton('Мои координаты', request_location=True)]
    ]
    return ReplyKeyboardMarkup(keyboard)
