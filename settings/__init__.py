"""
Инициализация пакета для работы с конфигурационными файлами.

Этот файл содержит логику для чтения конфигурационного файла и извлечения нужных параметров.
"""

from .config_reader import get_bot_token, get_time_delete_messages

__all__ = ['get_bot_token', 'get_time_delete_messages']
