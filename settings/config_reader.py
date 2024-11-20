import configparser
from loguru import logger

# Создание объекта ConfigParser для работы с конфигурационным файлом
config = configparser.ConfigParser(empty_lines_in_values=False, allow_no_value=True)

# Считываем конфигурационный файл config.ini
config.read("data/config.ini")


def get_bot_token():
    """
    Получение токена бота из конфигурационного файла.
    :return: str - токен бота.
    """
    try:
        return config.get("BOT_TOKEN", "BOT_TOKEN")
    except Exception as e:
        # Логируем ошибку, если она возникла
        logger.exception(f"Ошибка: {e}")


def get_time_delete_messages():
    """
    Получение времени для удаления сообщений из конфигурационного файла.
    :return: int - время удаления сообщений в секундах.
    """
    try:
        return int(config.get("TIME_DELETE_MESSAGES", "TIME_DELETE_MESSAGES"))
    except Exception as e:
        # Логируем ошибку, если она возникла
        logger.exception(f"Ошибка: {e}")
