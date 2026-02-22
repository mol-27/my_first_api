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


# --- МОДЕЛИ PYDANTIC ---
class UserCreate(BaseModel):
    username: str
    email: str


class ArticleCreate(BaseModel):
    title: str
    content: str


# --- 2. СОБЫТИЯ ЗАПУСКА И ОСТАНОВА ---
@app.on_event("startup")
async def startup():
    metadata.create_all(bind=engine)
    await database.connect()
    print("✅ База данных подключена")


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
    print("❌ База данных отключена")


# --- 3. ГЛАВНАЯ ---
@app.get("/")
def read_root():
    return {"message": "🚀 Продакшен API с PostgreSQL работает!"}


# --- 4. ПОЛЬЗОВАТЕЛИ ---
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


@app.get("/users/{user_id}")
async def get_user(user_id: int):
    query = users.select().where(users.c.id == user_id)
    user = await database.fetch_one(query)
    if user:
        return user
    return {"error": "Пользователь не найден"}


@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    query = users.delete().where(users.c.id == user_id)
    result = await database.execute(query)
    if result:
        return {"message": f"Пользователь {user_id} удалён"}
    return {"error": "Пользователь не найден"}


# --- 5. СТАТЬИ ---
@app.post("/articles")
async def create_article(article: ArticleCreate):
    # Для простоты назначаем автором "Anonymous"
    query = articles.insert().values(
        title=article.title,
        content=article.content,
        author="Anonymous",
        likes=0
    )
    article_id = await database.execute(query)
    return {"message": "Статья создана", "id": article_id}


@app.get("/articles")
async def get_articles():
    query = articles.select()
    all_articles = await database.fetch_all(query)
    return {"articles": all_articles}


@app.post("/articles/{article_id}/like")
async def like_article(article_id: int):
    # Сначала получаем текущее количество лайков
    select_query = articles.select().where(articles.c.id == article_id)
    article = await database.fetch_one(select_query)
    if not article:
        return {"error": "Статья не найдена"}

    # Увеличиваем лайки на 1
    new_likes = article["likes"] + 1
    update_query = articles.update().where(articles.c.id == article_id).values(likes=new_likes)
    await database.execute(update_query)

    return {"message": f"❤️ Лайк добавлен статье {article_id}", "likes": new_likes}


@app.get("/articles/search")
async def search_articles(q: str):
    query = articles.select().where(articles.c.title.ilike(f"%{q}%"))
    results = await database.fetch_all(query)
    return {"query": q, "count": len(results), "results": results}
