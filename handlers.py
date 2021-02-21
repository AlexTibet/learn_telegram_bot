from datetime import datetime
import logging
import ephem
from utils import WeatherInfoOpenWeatherMap, user_keyboard
import settings


def greet_user(update, context):
    update.message.reply_text('Привет!', reply_markup=user_keyboard())


def talk_to_me(update, context):
    text = update.message.text
    logging.info(text)
    update.message.reply_text(text, reply_markup=user_keyboard())


def user_coordinates(update, context):
    coordinates = update.message.location


def planet(update, context):
    planet_list = ['Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto', 'Sun', 'Moon']
    answer = f"Попробуйте написать /planet _Название-планеты_\n`Известные мне планеты: {', '.join(planet_list)}.`"

    if len(context.args) == 0:
        return update.message.reply_text(
            answer, parse_mode="Markdown",
            reply_markup=user_keyboard()
        )

    query = update.message.text.split()[1]
    if query not in planet_list:
        return update.message.reply_text(
            ("`Планета не найдена`\n" + answer),
            parse_mode="Markdown",
            reply_markup=user_keyboard()
        )

    date = datetime.now().strftime("%Y/%m/%d")
    target = getattr(ephem, query)(date)
    target_position, target_position_full = ephem.constellation(target)
    answer = f"`Планета` {target.name} `сегодня в созвездии` {target_position}\n" \
             f"`Также известном как` {target_position_full}"

    update.message.reply_text(answer, parse_mode="Markdown", reply_markup=user_keyboard())


def weather(update, context):
    try:
        city = update.message.text.split()[1]
    except IndexError:
        city = settings.DEFAULT_CITY

    info = WeatherInfoOpenWeatherMap(city)

    if not info.search():
        return update.message.reply_text('`Ошибка`\n`Нет данных`', parse_mode="Markdown", reply_markup=user_keyboard())

    answer = f"*{info.name} - {info.description}*\n`Температура:` {info.temp}°C  `По ощущениям` {info.temp_feel}°C\n" \
             f"`Давление: {info.pressure}, Влажность: {info.humidity}`\n" \
             f"`Скорость ветра {info.wind_speed}м/с`\n{info.icon_url}"

    update.message.reply_text(answer, parse_mode="Markdown", reply_markup=user_keyboard())


