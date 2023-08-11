import logging

import telegram
import vk_api as vk
from environs import Env
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkEventType, VkLongPoll
from vk_api.utils import get_random_id

from log_helpers import TelegramLogsHandler
from quiz_db import get_answer, get_random_question
from redis_helper import auth_redis

logger = logging.getLogger('vk_bot')


def handle_new_question_request(event, vk_api, keyboard, redis_db):
    chat_id = event.user_id
    question = get_random_question()
    redis_db.set(chat_id, question)
    vk_api.messages.send(peer_id=chat_id, random_id=get_random_id(), keyboard=keyboard.get_keyboard(), message=question)


def handle_defeat(event, vk_api, keyboard, redis_db):
    chat_id = event.user_id
    question = redis_db.get(chat_id)
    if not question:
        vk_api.messages.send(peer_id=chat_id, random_id=get_random_id(),
                             keyboard=keyboard.get_keyboard(), message='Нажми на кнопку "Новый вопрос"')
        return
    answer = get_answer(question)
    vk_api.messages.send(peer_id=chat_id, random_id=get_random_id(),
                         keyboard=keyboard.get_keyboard(), message=f'Правильный ответ: {answer}')
    handle_new_question_request(event, vk_api, keyboard, redis_db)


def handle_solution_attempt(event, vk_api, keyboard, redis_db):
    chat_id = event.user_id
    question = redis_db.get(chat_id)
    if not question:
        vk_api.messages.send(peer_id=chat_id, random_id=get_random_id(),
                             keyboard=keyboard.get_keyboard(), message='Нажми на кнопку "Новый вопрос"')
        return
    answer = get_answer(question)
    if answer == event.text:
        message = 'Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»'
        redis_db.set(chat_id, '')
    else:
        message = 'Неправильно… Попробуешь ещё раз?'
    vk_api.messages.send(
        peer_id=chat_id,
        random_id=get_random_id(),
        keyboard=keyboard.get_keyboard(),
        message=message
    )


def main():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    env = Env()
    env.read_env()

    tg_token = env('TG_TOKEN')
    tg_chat_id = env('TG_CHAT_ID')
    bot = telegram.Bot(token=tg_token)
    logger.addHandler(TelegramLogsHandler(bot, tg_chat_id))
    logger.info('Бот для логов запущен')

    vk_group_token = env('VK_GROUP_TOKEN')
    vk_session = vk.VkApi(token=vk_group_token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    redis_address = env('REDIS_ADDRESS')
    redis_port = env('REDIS_PORT')
    redis_user = env('REDIS_USER')
    redis_password = env('REDIS_PASSWORD')

    quiz_db = auth_redis(redis_address, redis_port, redis_user, redis_password)
    quiz_db.flushall()

    menu_keyboard = VkKeyboard(one_time=True)
    menu_keyboard.add_button('Новый вопрос', color=VkKeyboardColor.POSITIVE)
    menu_keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)
    menu_keyboard.add_line()
    menu_keyboard.add_button('Мой счет', color=VkKeyboardColor.PRIMARY)
    while True:
        try:
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    if event.text == 'Новый вопрос':
                        handle_new_question_request(event, vk_api, keyboard=menu_keyboard, redis_db=quiz_db)
                    elif event.text == 'Сдаться':
                        handle_defeat(event, vk_api, keyboard=menu_keyboard, redis_db=quiz_db)
                    else:
                        handle_solution_attempt(event, vk_api, keyboard=menu_keyboard, redis_db=quiz_db)
        except Exception as err:
            logger.exception(f'Произошла ошибка: {err=}, {type(err)=}')


if __name__ == "__main__":
    main()
