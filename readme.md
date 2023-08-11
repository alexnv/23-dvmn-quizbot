# Бот-викторина для Telegram и VK.

## Примеры работы программы:

Пример работы в Telegram:
[Ссылка на бота](http://t.me/dvmnQuiz999Bot)

![tg](https://dvmn.org/media/filer_public/e9/eb/e9ebd8aa-17dd-4e82-9f00-aad21dc2d16c/examination_tg.gif)

Пример рабоы в VK:
[Ссылка на бота](https://vk.com/club221573776)

![vk](https://dvmn.org/media/filer_public/aa/c8/aac86f90-29b6-44bb-981e-02c8e11e69f7/examination_vk.gif)

## Установка и настройка

* Скачайте код.
* Установите зависимости командой:

```
pip install -r requirements.txt
```

#### Переменные окружения

Запишите переменные окружения в файле .env в формате КЛЮЧ=ЗНАЧЕНИЕ:

* `TG_TOKEN` - Телеграм токен. Получить у [BotFather](https://telegram.me/BotFather).
* `VK_GROUP_TOKEN` - Токен группы в VK. Получить в настройках группы, в меню “Работа с API”.
* `TG_CHAT_ID` - ID чата в телеграм, в который будут приходить логи.
* `REDIS_ADDRESS` - Адрес базы данных redis.
* `REDIS_PORT` - Порт базы данных redis
* `REDIS_USER` - Пользователь базы данных redis
* `REDIS_PASSWORD` - Пароль базы данных redis

#### Подготовка данных для викторины

* [Скачайте](https://devman.org/encyclopedia/python_intermediate/python_files/) вопросы для викторины.
* Перенесете необходимые файлы в папку `quiz_questions`, которую необходимо создать в корне проекта. (Вы можете создать
  свои вопросы для викторины, но их формат должен полностью соответствовать формату скачаных файлов).
* Запустите создание quiz_bank.json файла командой:

```
python create_quiz_questions_base.py
```

## Запуск:

Запустить телеграм бота:

```
python tg_bot.py
```

Запустить бота в VK:

```
python vk_bot.py
```