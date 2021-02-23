import datetime
from collections import defaultdict
from telegram import ReplyKeyboardMarkup, KeyboardButton
import requests
import settings


def user_keyboard() -> ReplyKeyboardMarkup:
    keyboard = [
        ['/start'],
        ['/planet', '/weather', '/wordcount'],
        [KeyboardButton('Мои координаты', request_location=True)]
    ]
    return ReplyKeyboardMarkup(keyboard)


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


class CityGame:

    def __init__(self):
        self.score = 0
        self.last_char = None
        self.__city_list = defaultdict(set)

    def _create_city_list(self):
        with open('cities.db', 'r', encoding='utf-8') as file:
            for line in file:
                city = line.strip().lower()
                self.__city_list[city[0]].add(city)

    def start_new_game(self):
        self.score = 0
        self._create_city_list()

    def check_city(self, name: str) -> bool:
        try:
            self.__city_list[name[0]].remove(name)
            self.score += 1
            return True
        except KeyError:
            return False

    def get_city(self, last_char):
        try:
            new_city = self.__city_list[last_char].pop()
        except KeyError:
            return None
        self.last_char = new_city[-1].lower()
        return new_city.capitalize()


if __name__ == '__main__':
    game = CityGame()
    game.start_new_game()
    print(game.__city_list)
    for i in range(35):
        print(game.get_city("ю"))

