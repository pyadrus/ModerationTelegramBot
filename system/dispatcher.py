from aiogram import Bot, Dispatcher, Router
from aiogram.fsm.storage.memory import MemoryStorage
from settings.settings import bot_token

# Установка подключение с telegram
bot = Bot(token=bot_token)

storage = MemoryStorage()  # Хранилище
dp = Dispatcher(storage=storage)


router = Router()
dp.include_router(router)
