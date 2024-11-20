from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from loguru import logger


def link_to_channel(channel_name):
    """
    Функция для создания кнопки с ссылкой на Telegram канал.

    Args:
        channel_name (str): Имя канала (без символа '@'), на который нужно дать ссылку.

    Returns:
        InlineKeyboardMarkup: Разметка для отображения кнопки с ссылкой на канал.
    """
    try:
        # Создание разметки кнопок
        rows = [
            [
                InlineKeyboardButton(
                    text="Подписаться на канал",  # Текст кнопки
                    url=f"https://t.me/{channel_name}"  # URL-ссылка на канал
                )
            ],
        ]

        # Создание клавиатуры с одной кнопкой
        link_to_channel = InlineKeyboardMarkup(inline_keyboard=rows)

        # Возвращаем разметку кнопки
        return link_to_channel
    except Exception as e:
        # Логируем ошибку, если она возникла
        logger.exception(f"Ошибка: {e}")
