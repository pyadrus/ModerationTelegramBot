from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from loguru import logger


def link_to_channel(channel_name):
    try:
        rows = [
            [
                InlineKeyboardButton(text="Подписаться на канал", url=f"https://t.me/{channel_name}")
            ],
        ]
        link_to_channel = InlineKeyboardMarkup(inline_keyboard=rows)
        return link_to_channel
    except Exception as e:
        logger.error(f"Ошибка: {e}")
