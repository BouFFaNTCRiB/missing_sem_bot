from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.dispatcher.filters import Command
import requests
from bs4 import BeautifulSoup

import config

bot_token = config.Token
bot = Bot(token=bot_token)
dp = Dispatcher(bot)
hello = 'Приветик, напиши /help чтоб узнать что я умею'


def city_checking(message):
    request = requests.get('https://www.meteoservice.ru/location/search?q=' + message + '&force=0')
    request_soup = BeautifulSoup(request.text, "html.parser")
    if request.status_code != 200:
        return request_soup, 1
    else:
        if len(request_soup.findAll('i', class_='material-icons font-4x color-alert float-left')) != 0:
            return request_soup, 2
        found_refs = request_soup.find_all('a', href=True)
        found_city_request = requests.get('https://www.meteoservice.ru' + found_refs[30]['href'])
        found_city_request_soup = BeautifulSoup(found_city_request.text, "html.parser")
    return found_city_request_soup, 0


@dp.message_handler(commands=["weather"])
async def weather(message: types.Message, command: Command):
    soup, checker = city_checking(command.args)
    if checker == 0:
        temp = soup.findAll('span', {"class": 'value'})[0].text.strip()
        await message.reply(f"В городе {command.args} сейчас {temp}")
    elif checker == 1:
        await message.reply('Упс, случилась ошибочка во время запроса')
    elif checker == 2:
        await message.reply('Напишите /weather название существующего города')


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.answer(hello)


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.answer("Я умею рассказывать температуру по команде weather!")


if __name__ == '__main__':
    executor.start_polling(dp)
