import logging
import random

import vk_api as vk
from environs import Env
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkEventType, VkLongPoll

logger = logging.getLogger('vk_bot')


def echo(event, vk_api, keyboard):
    vk_api.messages.send(
        user_id=event.user_id,
        message=event.text,
        keyboard=keyboard.get_keyboard(),
        random_id=random.randint(1, 1000)
    )


def main():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    env = Env()
    env.read_env()
    vk_group_token = env('VK_GROUP_TOKEN')
    vk_session = vk.VkApi(token=vk_group_token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    menu_keyboard = VkKeyboard(one_time=True)
    menu_keyboard.add_button('Новый вопрос', color=VkKeyboardColor.POSITIVE)
    menu_keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)
    menu_keyboard.add_line()
    menu_keyboard.add_button('Мой счет', color=VkKeyboardColor.PRIMARY)

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            echo(event, vk_api, keyboard=menu_keyboard)


if __name__ == "__main__":
    main()
