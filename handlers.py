from datetime import datetime
import logging
import ephem
from utils import WeatherInfoOpenWeatherMap, CityGame, user_keyboard
import settings


def greet_user(update, context):
    update.message.reply_text(
        f'`Привет {update.effective_chat["username"]}!`\n'
        f'`Вот что я умею:\n`'
        f'{settings.DESCRIPTION}',
        parse_mode="Markdown",
        reply_markup=user_keyboard()
        )


def talk_to_me(update, context):
    text = update.message.text
    logging.info(text)
    update.message.reply_text(text, parse_mode="Markdown", reply_markup=user_keyboard())


def user_coordinates(update, context):
    coordinates = update.message.location


def wordcount(update, context):
    update.message.reply_text(f"`{len(context.args)}`", parse_mode="Markdown", reply_markup=user_keyboard())


def next_full_moon(update, context):
    date = datetime.now()

    if len(context.args) != 0:
        date = datetime.strptime(context.args[0].strip(), "%Y-%m-%d")

    full_moon_date = ephem.next_full_moon(date)

    update.message.reply_text(
        f"`Дата отсчета {date.date()}`\n"
        f"`Следующее полнолуние:` {full_moon_date}",
        parse_mode="Markdown",
        reply_markup=user_keyboard()
    )


def planet(update, context):
    planet_list = ['Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto', 'Sun', 'Moon']
    answer = f"Попробуйте написать /planet _Название-планеты_\n`Известные мне планеты: {', '.join(planet_list)}.`"

    if len(context.args) == 0:
        return update.message.reply_text(
            answer, parse_mode="Markdown"
        )

    query = update.message.text.split()[1]
    if query not in planet_list:
        return update.message.reply_text(
            ("`Планета не найдена`\n" + answer),
            parse_mode="Markdown"
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
        return update.message.reply_text('`Ошибка`\n`Нет данных`', parse_mode="Markdown")

    answer = f"*{info.name} - {info.description}*\n`Температура:` {info.temp}°C  `По ощущениям` {info.temp_feel}°C\n" \
             f"`Давление: {info.pressure}, Влажность: {info.humidity}`\n" \
             f"`Скорость ветра {info.wind_speed}м/с`\n{info.icon_url}"

    update.message.reply_text(answer, parse_mode="Markdown", reply_markup=user_keyboard())


def city_game(update, context):
    if 'city_game' not in context.user_data:
        game = CityGame()
        game.start_new_game()
        context.user_data['city_game'] = game

    try:
        city_name = update.message.text.split()[1]
    except IndexError:
        return update.message.reply_text(
            '`Введите после "Город" название города на русском языке.`'
            '`Если название города состоит из нескольких слов то разделяйте их дефисами "-"`',
            parse_mode="Markdown"
        )

    last_char = context.user_data['city_game'].last_char

    if city_name[0].lower() != last_char and last_char is not None:
        return update.message.reply_text(
            f"{city_name} `начинается не на` *{last_char}*", parse_mode="Markdown"
        )

    if not context.user_data['city_game'].check_city(city_name.lower()):
        return update.message.reply_text(
            f"`Города {city_name} нет в моей базе данных, попробуйте ещё раз`", parse_mode="Markdown"
        )

    new_city = context.user_data['city_game'].get_city(city_name.lower()[-1])

    if new_city is None:
        game = context.user_data.pop('city_game')
        answer = f"*Поздравляю* {update.effective_chat['username']}!\n" \
                 f"`Городов начинающихся на` *{city_name[-1]}* `больше нет в моей базе данных.`\n" \
                 f"`Вы выйграли назвав` *{game.score}* `города(ов).`"
        return update.message.reply_text(answer, parse_mode="Markdown")

    update.message.reply_text(
        f"`Ваш город:` {city_name} `заканчивается на букву` *{city_name[-1].upper()}*\n"
        f"`Мой ответ:` {new_city.capitalize()}.\n"
        f"`Теперь Вам город на букву` *{new_city[-1].upper()}*",
        parse_mode="Markdown",
        reply_markup=user_keyboard()
    )
