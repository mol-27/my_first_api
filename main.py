# main.py
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

app = FastAPI(title="Мой первый рабочий API", version="1.0")


# ========== МОДЕЛИ ДАННЫХ ==========
class UserCreate(BaseModel):
    username: str
    email: str


class ArticleCreate(BaseModel):
    title: str
    content: str


# ========== "БАЗА ДАННЫХ" В ПАМЯТИ ==========
fake_db = {
    "users": [],
    "articles": []
}


# ========== ГЛАВНАЯ И HEALTHCHECK ==========
@app.get("/")
def read_root():
    return {
        "message": "🚀 Мой API работает в интернете!",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "users": "/users",
            "articles": "/articles"
        },
        "deployed": True
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "My Deployed API"
    }


# ========== РАБОТА С ПОЛЬЗОВАТЕЛЯМИ ==========
@app.get("/users", response_model=dict)
def get_users():
    return {
        "count": len(fake_db["users"]),
        "users": fake_db["users"]
    }


@app.post("/users", response_model=dict)
def create_user(user: UserCreate):
    user_id = len(fake_db["users"]) + 1
    user_data = {
        "id": user_id,
        **user.dict(),
        "created_at": datetime.now().isoformat()
    }

    fake_db["users"].append(user_data)
    return {
        "message": "✅ Пользователь создан",
        "user": user_data
    }


@app.get("/users/{user_id}")
def get_user(user_id: int):
    if user_id <= 0 or user_id > len(fake_db["users"]):
        return {"error": "Пользователь не найден"}
    return fake_db["users"][user_id - 1]


# ========== РАБОТА СО СТАТЬЯМИ ==========
@app.get("/articles")
def get_articles():
    return {
        "count": len(fake_db["articles"]),
        "articles": fake_db["articles"]
    }


@app.post("/articles")
def create_article(article: ArticleCreate, author_id: int = 1):
    author = fake_db["users"][0] if fake_db["users"] else {"username": "Anonymous"}

    article_id = len(fake_db["articles"]) + 1
    article_data = {
        "id": article_id,
        **article.dict(),
        "author": author.get("username", "Anonymous"),
        "author_id": author_id,
        "created_at": datetime.now().isoformat(),
        "likes": 0
    }

    fake_db["articles"].append(article_data)
    return {
        "message": "✅ Статья создана",
        "article": article_data
    }


@app.post("/articles/{article_id}/like")
def like_article(article_id: int):
    if article_id <= 0 or article_id > len(fake_db["articles"]):
        return {"error": "Статья не найдена"}

    fake_db["articles"][article_id - 1]["likes"] += 1
    return {
        "message": f"❤️ Лайк добавлен статье {article_id}",
        "likes": fake_db["articles"][article_id - 1]["likes"]
    }


# ========== НОВЫЙ ENDPOINT ДЛЯ ПОИСКА ==========
@app.get("/articles/search")
def search_articles(q: str):
    """Поиск статей по ключевому слову в заголовке"""
    if not q:
        return {"results": []}

    results = [
        article for article in fake_db["articles"]
        if q.lower() in article["title"].lower()
    ]

    return {
        "query": q,
        "count": len(results),
        "results": results
    }