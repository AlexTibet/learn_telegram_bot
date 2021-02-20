import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import ephem
import requests
import settings
from datetime import datetime


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
    city = 'Tomsk'
    req = requests.get(
        f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={settings.WEATHER_APIKEY}&lang=ru&units=metric'
    )
    if req.status_code == requests.codes.ok:
        info = req.json()
        city_name = info['name']
        weather_info = info['weather']
        icon_url = f"http://openweathermap.org/img/wn/{weather_info[0]['icon']}@2x.png"
        descr = weather_info[0]['description']
        temp = info['main']['temp']
        temp_feel = info['main']['feels_like']
        pressure = info['main']['pressure']
        humidity = info['main']['humidity']
        wind_speed = info['wind']['speed']
        answer = f"*{city_name} - {descr}*\n`Температура:` {temp}°C  `По ощущениям` {temp_feel}°C\n" \
                 f"`Давление: {pressure}, Влажность: {humidity}`\n`Скорость ветра {wind_speed}м/с`\n{icon_url}"
        update.message.reply_text(answer, parse_mode="Markdown")
    else:
        update.message.reply_text("`Неудачная попытка связаться с openweathermap api`", parse_mode="Markdown")


def main():
    logging.basicConfig(filename='bot.log', level=logging.INFO)
    bot = Updater(settings.API_KEY, use_context=True)
    dp = bot.dispatcher
    dp.add_handler(CommandHandler('start', greet_user))
    dp.add_handler(CommandHandler('weather', weather))
    dp.add_handler(MessageHandler(Filters.text, talk_to_me))
    logging.info('Bot starting')
    bot.start_polling()
    bot.idle()


if __name__ == '__main__':
    main()
