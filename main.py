#!/usr/bin/env python

import random
from typing import Any

from config import BOT_TOKEN_API, ADMIN_IDS

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import Command, BaseFilter


# Вместо BOT TOKEN HERE нужно вставить токен вашего бота,
# полученный у @BotFather
BOT_TOKEN: str = BOT_TOKEN_API

# Создаем объекты бота и диспетчера
bot: Bot = Bot(BOT_TOKEN)
dp: Dispatcher = Dispatcher()


# Количество попыток, доступных пользователю в игре
ATTEMPTS: int = 5

# Словарь, в котором будут храниться данные пользователя
users: dict = {}
admin_ids: list[int] = ADMIN_IDS


# Функция возвращающая случайное целое число от 1 до 100
def get_random_number() -> int:
    return random.randint(1, 100)

# Проверка юзера на админа
class IsAdmin(BaseFilter):
    def __init__(self, admin_ids: list[int]) -> None:
        self.admin_ids = admin_ids

    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in self.admin_ids


# Этот хэндлер будет срабатывать, если апдейт от админа
@dp.message(IsAdmin(admin_ids))
async def answer_if_admins_update(message: Message):
    await message.answer(text='Вы админ')


# Этот хэндлер будет срабатывать, если апдейт не от админа
# @dp.message()
# async def answer_if_not_admins_update(message: Message):
#     await message.answer(text='Вы не админ')


# Этот хэндлер будет срабатывать на команду "/start"
@dp.message(Command(commands=['start']))
async def process_start_command(message: Message):
    await message.answer('Привет!\nДавай сыграем в игру "Угадай число"?\n\n'
                        'Чтобы получить правила игры и список доступных '
                        'команд - отправьте команду /help')
    # Если пользователь только запустил бота и его нет в словаре '
    # 'users - добавляем его в словарь
    if message.from_user.id not in users:
        users[message.from_user.id] = {'in_game': False,
                                        'secret_number': None,
                                        'attempts': None,
                                        'total_games': 0,
                                        'wins': 0}


# Этот хэндлер будет срабатывать на команду "/help"
@dp.message(Command(commands=['help']))
async def process_help_command(message: Message):
    await message.answer(f'Правила игры:\n\nЯ загадываю число от 1 до 100, '
                        f'а вам нужно его угадать\nУ вас есть {ATTEMPTS} '
                        f'попыток\n\nДоступные команды:\n/help - правила '
                        f'игры и список команд\n/cancel - выйти из игры\n'
                        f'/stat - посмотреть статистику\n\nДавай сыграем?')


# Этот хэндлер будет срабатывать на команду "/stat"
@dp.message(Command(commands=['stat']))
async def process_stat_command(message: Message):
    await message.answer(
                    f'Всего игр сыграно: '
                    f'{users[message.from_user.id]["total_games"]}\n'
                    f'Игр выиграно: {users[message.from_user.id]["wins"]}')
    print(users)


# Этот хэндлер будет срабатывать на команду "/cancel"
@dp.message(Command(commands=['cancel']))
async def process_cancel_command(message: Message):
    if users[message.from_user.id]['in_game']:
        await message.answer('Вы вышли из игры. Если захотите сыграть '
                            'снова - напишите об этом')
        users[message.from_user.id]['in_game'] = False
    else:
        await message.answer('А мы итак с вами не играем. '
                            'Может, сыграем разок?')


# Этот хэндлер будет срабатывать на согласие пользователя сыграть в игру
@dp.message(F.text.lower().in_(['да', 'давай', 'сыграем', 'игра', 'играть', 'хочу играть']))
async def process_positive_answer(message: Message):
    if not users[message.from_user.id]['in_game']:
        await message.answer('Ура!\n\nЯ загадал число от 1 до 100, '
                            'попробуй угадать!')
        users[message.from_user.id]['in_game'] = True
        users[message.from_user.id]['secret_number'] = get_random_number()
        users[message.from_user.id]['attempts'] = ATTEMPTS
    else:
        await message.answer('Пока мы играем в игру я могу '
                            'реагировать только на числа от 1 до 100 '
                            'и команды /cancel и /stat')


# Этот хэндлер будет срабатывать на отказ пользователя сыграть в игру
@dp.message(F.text.lower().in_(['нет', 'не', 'не хочу', 'не буду']))
async def process_negative_answer(message: Message):
    if not users[message.from_user.id]['in_game']:
        await message.answer('Жаль :(\n\nЕсли захотите поиграть - просто '
                            'напишите об этом')
    else:
        await message.answer('Мы же сейчас с вами играем. Присылайте, '
                            'пожалуйста, числа от 1 до 100')


# Этот хэндлер будет срабатывать на отправку пользователем чисел от 1 до 100
@dp.message(lambda x: x.text and x.text.isdigit() and 1 <= int(x.text) <= 100)
async def process_numbers_answer(message: Message):
    if users[message.from_user.id]['in_game']:
        if int(message.text) == users[message.from_user.id]['secret_number']:
            await message.answer('Ура!!! Вы угадали число!\n\n'
                                'Может, сыграем еще?')
            users[message.from_user.id]['in_game'] = False
            users[message.from_user.id]['total_games'] += 1
            users[message.from_user.id]['wins'] += 1
        elif int(message.text) > users[message.from_user.id]['secret_number']:
            await message.answer('Мое число меньше')
            users[message.from_user.id]['attempts'] -= 1
        elif int(message.text) < users[message.from_user.id]['secret_number']:
            await message.answer('Мое число больше')
            users[message.from_user.id]['attempts'] -= 1

        if users[message.from_user.id]['attempts'] == 0:
            await message.answer(
                    f'К сожалению, у вас больше не осталось '
                    f'попыток. Вы проиграли :(\n\nМое число '
                    f'было {users[message.from_user.id]["secret_number"]}'
                    f'\n\nДавайте сыграем еще?')
            users[message.from_user.id]['in_game'] = False
            users[message.from_user.id]['total_games'] += 1
    else:
        await message.answer('Мы еще не играем. Хотите сыграть?')


# Этот хэндлер будет срабатывать на остальные текстовые сообщения
@dp.message()
async def process_other_text_answers(message: Message):
    if users[message.from_user.id]['in_game']:
        await message.answer('Мы же сейчас с вами играем. '
                            'Присылайте, пожалуйста, числа от 1 до 100')
    else:
        await message.answer('Я довольно ограниченный бот, давайте '
                            'просто сыграем в игру?')





if __name__ == '__main__':
    dp.run_polling(bot)



























# import random

# from aiogram import Bot, Dispatcher, F
# from aiogram.types import Message
# from aiogram.filters import Command #, Text



# # Вместо BOT TOKEN HERE нужно вставить токен вашего бота,
# # полученный у @BotFather
# BOT_TOKEN: str = '6406401823:AAEVOu_-k2QwJXdR-bEmUeTZiFuW4mKa1os'

# # Создаем объекты бота и диспетчера
# bot: Bot = Bot(BOT_TOKEN)
# dp: Dispatcher = Dispatcher()

# # Количество попыток, доступных пользователю в игре
# ATTEMPTS: int = 5

# # Словарь, в котором будут храниться данные пользователя
# user: dict = {'in_game': False,
#               'secret_number': None,
#               'attempts': None,
#               'total_games': 0,
#               'wins': 0}


# # Функция возвращающая случайное целое число от 1 до 100
# def get_random_number() -> int:
#     return random.randint(1, 100)


# # Этот хэндлер будет срабатывать на команду "/start"
# @dp.message(Command(commands=['start']))
# async def process_start_command(message: Message):
#     await message.answer('Привет!\nДавай сыграем в игру "Угадай число"?\n\n'
#                          'Чтобы получить правила игры и список доступных '
#                          'команд - отправьте команду /help')


# # Этот хэндлер будет срабатывать на команду "/help"
# @dp.message(Command(commands=['help']))
# async def process_help_command(message: Message):
#     await message.answer(f'Правила игры:\n\nЯ загадываю число от 1 до 100, '
#                          f'а вам нужно его угадать\nУ вас есть {ATTEMPTS} '
#                          f'попыток\n\nДоступные команды:\n/help - правила '
#                          f'игры и список команд\n/cancel - выйти из игры\n'
#                          f'/stat - посмотреть статистику\n\nДавай сыграем?')


# # Этот хэндлер будет срабатывать на команду "/stat"
# @dp.message(Command(commands=['stat']))
# async def process_stat_command(message: Message):
#     await message.answer(f'Всего игр сыграно: {user["total_games"]}\n'
#                          f'Игр выиграно: {user["wins"]}')


# # Этот хэндлер будет срабатывать на команду "/cancel"
# @dp.message(Command(commands=['cancel']))
# async def process_cancel_command(message: Message):
#     if user['in_game']:
#         await message.answer('Вы вышли из игры. Если захотите сыграть \nснова - напишите об этом')
#         user['in_game'] = False
#     else:
#         await message.answer('А мы итак с вами не играем. \nМожет, сыграем разок?')


# # Этот хэндлер будет срабатывать на согласие пользователя сыграть в игру
# @dp.message(F.text.lower().in_(['да', 'давай', 'сыграем', 'игра', 'играть', 'хочу играть']))
# async def process_positive_answer(message: Message):
#     print(message.model_dump_json(indent=4))
#     if not user['in_game']:
#         await message.answer('Ура!\n\nЯ загадал число от 1 до 100,\nпопробуй угадать!')
#         user['in_game'] = True
#         user['secret_number'] = get_random_number()
#         user['attempts'] = ATTEMPTS
#     else:
#         await message.answer('Пока мы играем в игру я могу \nреагировать только на числа от 1 до 100 \nи команды /cancel и /stat')


# # Этот хэндлер будет срабатывать на отказ пользователя сыграть в игру
# @dp.message(F.text.lower().in_(['нет', 'не', 'не хочу', 'не буду']))
# async def process_negative_answer(message: Message):
#     if not user['in_game']:
#         await message.answer('Жаль :(\n\nЕсли захотите поиграть - просто \nнапишите об этом')
#     else:
#         await message.answer('Мы же сейчас с вами играем. Присылайте, \nпожалуйста, числа от 1 до 100')


# # Этот хэндлер будет срабатывать на отправку пользователем чисел от 1 до 100
# @dp.message(lambda x: x.text and x.text.isdigit() and 1 <= int(x.text) <= 100)
# async def process_numbers_answer(message: Message):
#     if user['in_game']:
#         if int(message.text) == user['secret_number']:
#             await message.answer('Ура!!! Вы угадали число!\n\nМожет, сыграем еще?')
#             user['in_game'] = False
#             user['total_games'] += 1
#             user['wins'] += 1
#         elif int(message.text) > user['secret_number']:
#             await message.answer('Мое число меньше')
#             user['attempts'] -= 1
#         elif int(message.text) < user['secret_number']:
#             await message.answer('Мое число больше')
#             user['attempts'] -= 1

#         if user['attempts'] == 0:
#             await message.answer(f'К сожалению, у вас больше не осталось '
#                                  f'попыток. Вы проиграли :(\n\nМое число '
#                                  f'было {user["secret_number"]}\n\nДавайте '
#                                  f'сыграем еще?')
#             user['in_game'] = False
#             user['total_games'] += 1
#     else:
#         await message.answer('Мы еще не играем. Хотите сыграть?')


# # Этот хэндлер будет срабатывать на остальные любые сообщения
# @dp.message()
# async def process_other_text_answers(message: Message):
#     # print(message.model_dump_json(indent=4))
#     if user['in_game']:
#         await message.answer('Мы же сейчас с вами играем. '
#                              'Присылайте, пожалуйста, числа от 1 до 100')
#     else:
#         await message.answer('Я довольно ограниченный бот, давайте '
#                              'просто сыграем в игру?')


# if __name__ == '__main__':
#     dp.run_polling(bot)





























# from aiogram import Bot, Dispatcher, F
# from aiogram.filters import Command
# from aiogram.types import Message

# # Вместо BOT TOKEN HERE нужно вставить токен вашего бота, полученный у @BotFather
# API_TOKEN: str = '6406401823:AAEVOu_-k2QwJXdR-bEmUeTZiFuW4mKa1os'

# # Создаем объекты бота и диспетчера
# bot: Bot = Bot(token=API_TOKEN)
# dp: Dispatcher = Dispatcher()


# # Этот хэндлер будет срабатывать на команду "/start"
# # @dp.message(Command(commands=["start"]))
# async def process_start_command(message: Message):
#     await message.answer('Привет!\nМеня зовут Эхо-бот!\nНапиши мне что-нибудь')


# # Этот хэндлер будет срабатывать на команду "/help"
# # @dp.message(Command(commands=['help']))
# async def process_help_command(message: Message):
#     await message.answer('Напиши мне что-нибудь и в ответ \nя пришлю тебе твое сообщение')

# # Этот хэндлер будет срабатывать на отправку боту фото
# async def send_photo_echo(message: Message):
#     print(message.model_dump_json(indent=4, exclude_none=True))
#     await message.reply_photo(message.photo[0].file_id)

# # Этот хэндлер будет срабатывать на любые ваши текстовые сообщения,
# # кроме команд "/start" и "/help"
# # @dp.message()
# async def send_echo(message: Message):
#     print(message.model_dump_json(indent=4, exclude_none=True))
#     await message.reply(text=message.text)

# # Регистрируем хэндлеры
# dp.message.register(process_start_command, Command(commands=["start"]))
# dp.message.register(process_help_command, Command(commands=['help']))
# dp.message.register(send_photo_echo, F.photo)
# dp.message.register(send_echo)


# if __name__ == '__main__':
#     dp.run_polling(bot)



















# import requests
# import time


# API_URL: str = 'https://api.telegram.org/bot'
# API_CATS_URL: str = 'https://api.thecatapi.com/v1/images/search'
# BOT_TOKEN: str = '6406401823:AAEVOu_-k2QwJXdR-bEmUeTZiFuW4mKa1os'
# ERROR_TEXT: str = 'Здесь должна была быть картинка с котиком :('

# offset: int = -2
# counter: int = 0
# chat_id: int
# cat_response: requests.Response
# cat_link: str


# while counter < 100:
#     print('attempt =', counter)
#     updates = requests.get(f'{API_URL}{BOT_TOKEN}/getUpdates?offset={offset + 1}').json()

#     if updates['result']:
#         for result in updates['result']:
#             offset = result['update_id']
#             chat_id = result['message']['from']['id']
#             cat_response = requests.get(API_CATS_URL)
#             if cat_response.status_code == 200:
#                 cat_link = cat_response.json()[0]['url']
#                 requests.get(f'{API_URL}{BOT_TOKEN}/sendPhoto?chat_id={chat_id}&photo={cat_link}')
#             else:
#                 requests.get(f'{API_URL}{BOT_TOKEN}/sendMessage?chat_id={chat_id}&text={ERROR_TEXT}')

#     time.sleep(1)
#     counter += 1