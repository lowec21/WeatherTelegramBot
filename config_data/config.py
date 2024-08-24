import os
from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
    exit('Переменные окружения не загружены т.к отсутствует файл .env')
else:
    load_dotenv()


DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
DATABASE_URL_psycopg = f'postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

BOT_TOKEN = os.getenv('BOT_TOKEN')
RAPID_API_KEY = os.getenv('RAPID_API_KEY')
COMMANDS = (
    ('start', 'Запустить бота'),
    ('help', 'Вывести справку'),
    ('get_weather', 'Прогноз погоды на 5 дней'),
    ('weather_for_the_day', 'Подробный прогноз погоды на день'),
    ('history', 'История последних 10-и запросов'),
    ('change_home_city', 'Изменить ваш текущий город'),
)
