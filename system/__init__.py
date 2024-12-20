"""
Инициализация пакета для работы с Telegram-ботом.

Этот файл содержит логику создания бота, диспетчера и маршрутизатора.
"""

from .bot_config import bot, dp, router

__all__ = ['bot', 'dp', 'router']
