from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

# Вместо BOT TOKEN HERE нужно вставить токен вашего бота, полученный у @BotFather
API_TOKEN: str = '6406401823:AAEVOu_-k2QwJXdR-bEmUeTZiFuW4mKa1os'

# Создаем объекты бота и диспетчера
bot: Bot = Bot(token=API_TOKEN)
dp: Dispatcher = Dispatcher()


# Этот хэндлер будет срабатывать на команду "/start"
@dp.message(Command(commands=["start"]))
async def process_start_command(message: Message):
    await message.answer('Привет!\nМеня зовут Эхо-бот!\nНапиши мне что-нибудь')


# Этот хэндлер будет срабатывать на команду "/help"
@dp.message(Command(commands=['help']))
async def process_help_command(message: Message):
    await message.answer('Напиши мне что-нибудь и в ответ '
                         'я пришлю тебе твое сообщение')


# Этот хэндлер будет срабатывать на любые ваши текстовые сообщения,
# кроме команд "/start" и "/help"
@dp.message()
async def send_echo(message: Message):
    await message.reply(text=message.text)


if __name__ == '__main__':
    dp.run_polling(bot)



















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