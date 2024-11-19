from aiogram import Bot, Dispatcher, Router
from aiogram.fsm.storage.memory import MemoryStorage

from settings import get_bot_token

# Установка подключения к Telegram с использованием токена
bot = Bot(token=get_bot_token())

# Инициализация хранилища для состояния бота (в данном случае используется MemoryStorage)
storage = MemoryStorage()  # Хранилище для временного хранения состояний в памяти

# Создание диспетчера, который управляет обработкой всех входящих событий и сообщений
dp = Dispatcher(storage=storage)

# Создание маршрутизатора для обработки команд и сообщений
router = Router()

# Подключение маршрутизатора к диспетчеру
dp.include_router(router)
