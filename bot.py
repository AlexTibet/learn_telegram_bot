import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import ephem
import settings
from datetime import datetime
from utils import WeatherInfoOpenWeatherMap


def greet_user(update, context):
    update.message.reply_text('Привет!')


def talk_to_me(update, context):
    text = update.message.text
    logging.info(text)
    update.message.reply_text(text)


def planet(update, context):
    planet_list = ['Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto', 'Sun', 'Moon']
    answer = f"Попробуйте написать /planet _Название-планеты_\n`Известные мне планеты: {', '.join(planet_list)}.`"
    query = update.message.text.split()[1]

    if len(context.args) == 0:
        return update.message.reply_text(answer, parse_mode="Markdown")

    if query not in planet_list:
        return update.message.reply_text(("`Планета не найдена`\n" + answer), parse_mode="Markdown")

    date = datetime.now().strftime("%Y/%m/%d")
    target = getattr(ephem, query)(date)
    target_position, target_position_full = ephem.constellation(target)
    answer = f"`Планета` {target.name} `сегодня в созвездии` {target_position}\n" \
             f"`Также известном как` {target_position_full}"

    update.message.reply_text(answer, parse_mode="Markdown")


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

    update.message.reply_text(answer, parse_mode="Markdown")


def main():
    logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s', filename='bot.log', level=logging.INFO)
    bot = Updater(settings.API_KEY, request_kwargs=settings.PROXY, use_context=True)
    dp = bot.dispatcher

    dp.add_handler(CommandHandler('start', greet_user))
    dp.add_handler(CommandHandler('weather', weather))
    dp.add_handler(CommandHandler('planet', planet))

    dp.add_handler(MessageHandler(Filters.text, talk_to_me))

    logging.info('Bot starting')
    bot.start_polling()
    bot.idle()


if __name__ == '__main__':
    main()
