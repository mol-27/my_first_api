# main.py
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from database import database, metadata, engine
from sqlalchemy import Table, Column, Integer, String, DateTime

app = FastAPI(title="Мой продакшен API", version="2.0")

# --- 1. ОПРЕДЕЛЯЕМ ТАБЛИЦЫ В БАЗЕ (СХЕМА) ---
users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String),
    Column("email", String),
    Column("created_at", DateTime, default=datetime.utcnow),
)

articles = Table(
    "articles",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String),
    Column("content", String),
    Column("author", String),
    Column("likes", Integer, default=0),
    Column("created_at", DateTime, default=datetime.utcnow),
)

# Модели Pydantic остаются прежними
class UserCreate(BaseModel):
    username: str
    email: str

class ArticleCreate(BaseModel):
    title: str
    content: str

# --- 2. СОБЫТИЯ ЗАПУСКА И ОСТАНОВА ---
@app.on_event("startup")
async def startup():
    # Создаём таблицы в базе (если их нет)
    metadata.create_all(bind=engine)
    # Подключаемся к базе данных
    await database.connect()
    print("✅ База данных подключена")

@app.on_event("shutdown")
async def shutdown():
    # Отключаемся от базы при остановке
    await database.disconnect()
    print("❌ База данных отключена")

# --- 3. ПЕРЕПИСЫВАЕМ ENDPOINTS ДЛЯ РАБОТЫ С БАЗОЙ ---
@app.post("/users")
async def create_user(user: UserCreate):
    query = users.insert().values(
        username=user.username,
        email=user.email
    )
    user_id = await database.execute(query)
    return {"message": "Пользователь создан", "id": user_id}

@app.get("/users")
async def get_users():
    query = users.select()
    all_users = await database.fetch_all(query)
    return {"users": all_users}

# (По аналогии переписываем endpoints для статей /articles, /articles/{id}/like)

@app.get("/")
def read_root():
    return {"message": "🚀 Продакшен API с PostgreSQL работает!"}

@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    query = users.delete().where(users.c.id == user_id)
    result = await database.execute(query)
    if result:
        return {"message": f"Пользователь {user_id} удалён"}
    return {"error": "Пользователь не найден"}
