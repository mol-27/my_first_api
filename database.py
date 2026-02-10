# database.py
from sqlalchemy import create_engine, MetaData
from databases import Database
import os

# Берём строку подключения из переменной окружения
DATABASE_URL = os.getenv("DATABASE_URL")

# Создаём "движок" и объекты для работы с базой
engine = create_engine(DATABASE_URL)
metadata = MetaData()
database = Database(DATABASE_URL)