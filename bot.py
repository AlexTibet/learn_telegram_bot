import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import settings


def greet_user(update, context):
    update.message.reply_text('Привет!')


def talk_to_me(update, context):
    text = update.message.text
    logging.info(text)
    update.message.reply_text(text)


def main():
    logging.basicConfig(filename='bot.log', level=logging.INFO)
    bot = Updater(settings.API_KEY, use_context=True)
    dp = bot.dispatcher
    dp.add_handler(CommandHandler('start', greet_user))
    dp.add_handler(MessageHandler(Filters.text, talk_to_me))
    logging.info('Bot starting')
    bot.start_polling()
    bot.idle()


if __name__ == '__main__':
    main()
