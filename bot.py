import logging

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from handlers import greet_user, weather, planet, talk_to_me, user_coordinates, wordcount, next_full_moon, city_game
import settings


def main():
    logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s', filename='bot.log', level=logging.INFO)
    bot = Updater(settings.API_KEY, request_kwargs=settings.PROXY, use_context=True)
    dp = bot.dispatcher

    dp.add_handler(CommandHandler('start', greet_user))
    dp.add_handler(CommandHandler('wordcount', wordcount))
    dp.add_handler(CommandHandler('planet', planet))
    dp.add_handler(CommandHandler('next_full_moon', next_full_moon))

    dp.add_handler(MessageHandler(Filters.regex('^(test)$'), talk_to_me))
    dp.add_handler(MessageHandler(Filters.regex('^[Пп]огода'), weather))
    dp.add_handler(MessageHandler(Filters.regex('^[Гг]ород'), city_game))

    dp.add_handler(MessageHandler(Filters.location, user_coordinates))

    logging.info('Bot starting')
    bot.start_polling()
    bot.idle()


if __name__ == '__main__':
    main()
