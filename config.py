from dotenv import load_dotenv
import os

# Загрузка переменных из .env файла
load_dotenv()

# Получение значения переменной окружения
DATABASE_URL = os.getenv('DATABASE_URL')
