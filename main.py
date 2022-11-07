from aiogram import Bot, executor, Dispatcher
from aiogram.types import Message
from setting import token
from binance import AsyncClient


bot = Bot(token)
dispatcher = Dispatcher(bot)
binance_client = AsyncClient()


@dispatcher.message_handler()
async def handle_coin_price(message: Message):
    pass
