from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from loguru import logger

def link_to_channel():
    try:

        rows = [
            [
                InlineKeyboardButton(
                    text="Подписаться на канал", url=f"t.me/{info[1]}"
                ),
            ],
        ]
        link_to_channel = InlineKeyboardMarkup(inline_keyboard=rows)
        return link_to_channel
    except Exception as e:
        logger.error(f"Ошибка: {e}")


if __name__ == "__main__":
    link_to_channel()
