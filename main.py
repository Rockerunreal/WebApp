
import asyncio

import pandas as pd
from aiogram import Bot
from aiogram import types
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.filters import Command
from aiogram.types import WebAppInfo, SuccessfulPayment
from aiogram.types.base import TelegramObject
from aiogram.types.message import ContentTypes, Message


BOT_TOKEN = '6882542931:AAH3dKkp3sa_GvbPgjRuaSRvLEjh1D7lQas'
PAYMENTS_PROVIDER_TOKEN = '381764678:TEST:74539'

bot = Bot(BOT_TOKEN)
dp = Dispatcher(bot)

pattern_url = "https://v2249831.hosted-by-vdsina.ru"

file_name = "database.xlsx"


@dp.message_handler(Command('start'))
async def start(message: Message):
    url = f'{pattern_url}/{message.chat.id}'
    web_app = WebAppInfo(url=f'{pattern_url}/{message.chat.id}')
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text='Site', web_app=web_app)]
        ],
        resize_keyboard=True
    )
    await bot.send_message(message.chat.id, 'Тестируем WebApp!',
                           reply_markup=keyboard)


@dp.message_handler(Command('id'))
async def get_id(message: Message):
    await bot.send_message(message.chat.id, message.chat.id)


@dp.pre_checkout_query_handler(lambda query: True)
async def checkout(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@dp.message_handler(content_types=ContentTypes.SUCCESSFUL_PAYMENT)
async def got_payment(message: types.Message):
    await bot.send_message(message.chat.id, "Оплата прошла",
                           parse_mode='Markdown')
    print(message.successful_payment.to_python()['invoice_payload'])


    if file_name.endswith('.xlsx'):
        df = pd.read_excel(
            file_name,
            engine='openpyxl',
        )
    elif file_name.endswith('.xls'):
        df = pd.read_excel(
            file_name,
            engine='xlrd'
        )
    elif file_name.endswith('.csv'):
        df = pd.read_csv(file_name)
    if file_name.endswith('.xlsx') or file_name.endswith('.xls'):
        for i in df.iloc:
            if str(i["id"]) == message.successful_payment.to_python()['invoice_payload']:
                await bot.send_message(message.chat.id, f"Ваш курс: {i['url_product']}\nБлагодарим за покупку",
                                       parse_mode='Markdown')
                break


async def main():
    try:
        await dp.start_polling()
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print('Bot stopped!')
