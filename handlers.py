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
    answer = (
        f"`Планета` {target.name} `сегодня в созвездии` {target_position}\n"
        f"`Также известном как` {target_position_full}"
    )

    update.message.reply_text(answer, parse_mode="Markdown", reply_markup=user_keyboard())


def weather(update, context):
    try:
        city = update.message.text.split()[1]
    except IndexError:
        city = settings.DEFAULT_CITY

    info = WeatherInfoOpenWeatherMap(city)

    if not info.search():
        return update.message.reply_text('`Ошибка`\n`Нет данных`', parse_mode="Markdown")

    answer = (
        f"*{info.name} - {info.description}*\n`Температура:` {info.temp}°C  `По ощущениям` {info.temp_feel}°C\n"
        f"`Давление: {info.pressure}, Влажность: {info.humidity}`\n"
        f"`Скорость ветра {info.wind_speed}м/с`\n{info.icon_url}"
    )
    update.message.reply_text(answer, parse_mode="Markdown", reply_markup=user_keyboard())


def city_game(update, context):
    game = context.user_data.get('city_game')

    if game is None:
        game = CityGame()
        game.start_new_game()

    try:
        player_city = update.message.text.split()[1]
    except IndexError:
        answer = (
            '`Введите после "Город" название города на русском языке.`\n'
            '`Если название города состоит из нескольких слов то разделяйте их дефисами "-"`'
        )
        return update.message.reply_text(answer, parse_mode="Markdown")

    if not game.check_last_char(player_city):
        return update.message.reply_text(f"{player_city} `начинается не на` *{game.last_char}*", parse_mode="Markdown")

    if not game.check_city(player_city.lower()):
        return update.message.reply_text(
            f"`Города {player_city} нет в моей базе данных, попробуйте ещё раз`", parse_mode="Markdown"
        )

    new_city = game.get_city(player_city.lower())
    if new_city is None:
        username = update.effective_chat['username']
        answer = (
            f"*Поздравляю* {username}!\n"
            f"`Городов начинающихся на` *{game.last_char}* `больше нет в моей базе данных.`\n"
            f"`Вы выйграли назвав` *{game.score}* `города(ов).`"
        )
        context.user_data.pop('city_game')
        return update.message.reply_text(answer, parse_mode="Markdown")

    context.user_data['city_game'] = game
    last_char = player_city[-1].upper()
    new_last_char = game.last_char
    answer = (
        f"`Ваш город:` {player_city} `заканчивается на букву` *{last_char}*\n"
        f"`Мой ответ:` {new_city.capitalize()}.\n`Теперь Вам город на букву` *{new_last_char}*\n"
        f"На данный момент ваш счёт равен` *{game.score}*"
    )
    update.message.reply_text(answer, parse_mode="Markdown", reply_markup=user_keyboard())
