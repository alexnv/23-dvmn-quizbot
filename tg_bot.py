import logging
from functools import partial

import telegram
from environs import Env
from telegram.ext import (CallbackContext, CommandHandler, Filters,
                          MessageHandler, Updater, ConversationHandler)

from quiz_db import get_random_question, get_answer
from redis_helper import auth_redis

logger = logging.getLogger(__name__)

NEW_QUESTION, SOLUTION_ATTEMPT = range(2)

menu_keyboard = [['Новый вопрос', 'Сдаться'], ['Мой счет']]
reply_markup = telegram.ReplyKeyboardMarkup(menu_keyboard)


def start(update: telegram.Update, context: CallbackContext):
    update.message.reply_text(text='Привет, я бот для викторин!', reply_markup=reply_markup)
    return NEW_QUESTION


def handle_new_question_request(update: telegram.Update, context: CallbackContext, redis_db):
    chat_id = update.effective_user.id
    question = get_random_question()
    redis_db.set(chat_id, question)
    update.message.reply_text(text=question, reply_markup=reply_markup)

    return SOLUTION_ATTEMPT


def handle_solution_attempt(update: telegram.Update, context: CallbackContext, redis_db):
    chat_id = update.effective_user.id
    question = redis_db.get(chat_id)
    message_text = update.message.text
    if not question:
        return NEW_QUESTION
    answer = get_answer(question)
    if answer == message_text:
        update.message.reply_text('Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»',
                                  reply_markup=reply_markup)
        return NEW_QUESTION
    else:
        update.message.reply_text('Неправильно… Попробуешь ещё раз?', reply_markup=reply_markup)
        return SOLUTION_ATTEMPT


def handle_defeat(update: telegram.Update, context: CallbackContext, redis_db):
    chat_id = update.effective_user.id
    question = redis_db.get(chat_id)
    if not question:
        return NEW_QUESTION
    answer = get_answer(question)
    update.message.reply_text(f'Правильный ответ: {answer}')
    handle_new_question_request(update, context, redis_db=redis_db)


def handle_other_text(update: telegram.Update, context: CallbackContext):
    update.message.reply_text('Нажми на одну из кнопок', reply_markup=reply_markup)
    return NEW_QUESTION


def main():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    env = Env()
    env.read_env()
    tg_token = env('TG_TOKEN')

    redis_address = env('REDIS_ADDRESS')
    redis_port = env('REDIS_PORT')
    redis_user = env('REDIS_USER')
    redis_password = env('REDIS_PASSWORD')

    updater = Updater(tg_token)
    dispatcher = updater.dispatcher

    quiz_db = auth_redis(redis_address, redis_port, redis_user, redis_password)
    quiz_db.flushall()

    handle_solution_attempt_with_args = partial(handle_solution_attempt, redis_db=quiz_db)
    handle_new_question_request_with_args = partial(handle_new_question_request, redis_db=quiz_db)
    handle_defeat_with_args = partial(handle_defeat, redis_db=quiz_db)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NEW_QUESTION: [MessageHandler(Filters.regex('Новый вопрос'), handle_new_question_request_with_args)],
            SOLUTION_ATTEMPT: [
                MessageHandler(Filters.regex('Сдаться'), handle_defeat_with_args),
                MessageHandler(Filters.text, handle_solution_attempt_with_args)
            ],
        },
        fallbacks=[MessageHandler(Filters.text, handle_other_text)]
    )
    dispatcher.add_handler(conv_handler)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
