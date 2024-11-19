import configparser

# Создание объекта ConfigParser для работы с конфигурационным файлом
config = configparser.ConfigParser(empty_lines_in_values=False, allow_no_value=True)

# Считываем конфигурационный файл config.ini
config.read("data/config.ini")

# Получаем токен бота из секции "BOT_TOKEN" и ключа "BOT_TOKEN" в файле config.ini
bot_token = config.get("BOT_TOKEN", "BOT_TOKEN")

# Получаем значение времени удаления сообщений из секции "TIME_DELETE_MESSAGES" и ключа "TIME_DELETE_MESSAGES"
# Преобразуем полученное значение в целое число с помощью int()
time_delete_messages = int(config.get("TIME_DELETE_MESSAGES", "TIME_DELETE_MESSAGES"))
