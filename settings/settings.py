import configparser

config = configparser.ConfigParser(empty_lines_in_values=False, allow_no_value=True)
# Считываем токен бота с файла config.ini
config.read("data/config.ini")
bot_token = config.get("BOT_TOKEN", "BOT_TOKEN")
time_delete_messages = int(config.get("TIME_DELETE_MESSAGES", "TIME_DELETE_MESSAGES"))
