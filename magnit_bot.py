from aiogram import Dispatcher, Bot ,executor, types
from aiogram.dispatcher.filters import Text
from data_bot import bot_token
from main import collect_data
from aiofiles import os

bot = Bot(token=bot_token)
dp = Dispatcher(bot)

@dp.message_handler(commands='start')
async def start(message: types.Message):
    start_buttons = ['Moscow', 'St.Petersburg']
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*start_buttons)

    await message.answer('Please select a City', reply_markup=keyboard)

@dp.message_handler(Text(equals='Moscow'))
async def moscow_city(message: types.Message):
    await message.answer('Estimated waiting time 1 min\nPlease waiting...')
    chat_id = message.chat.id
    await send_data(city_code='2398', chat_id=chat_id)

@dp.message_handler(Text(equals='St.Petersburg'))
async def piter_city(message: types.Message):
    await message.answer('Estimated waiting time 1 min\nPlease waiting...')
    chat_id = message.chat.id
    await send_data(city_code='1645', chat_id=chat_id)

async def send_data(city_code='2398', chat_id =''):
    file = await collect_data(city_code=city_code)
    await bot.send_document(chat_id=chat_id, document=open(file, 'rb'))
    await os.remove(file)


if __name__ == '__main__':
    executor.start_polling(dp)