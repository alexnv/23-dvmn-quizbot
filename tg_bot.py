import logging

import telegram
from environs import Env
from telegram.ext import (CallbackContext, CommandHandler, Filters,
                          MessageHandler, Updater)

logger = logging.getLogger(__name__)


def start(update: telegram.Update, context: CallbackContext):
    update.message.reply_text('Привет!')


def echo(update: telegram.Update, context: CallbackContext):
    update.message.reply_text(update.message.text)


def main():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    env = Env()
    env.read_env()
    tg_token = env('TG_TOKEN')

    updater = Updater(tg_token)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(MessageHandler(Filters.text, echo))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()