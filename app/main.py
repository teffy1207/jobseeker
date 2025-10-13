# app/main.py

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session

# 从我们创建的模块中导入
from app.model import BaseEntity, Resume, User, InterviewRecord
from app.database import engine, SessionLocal


BaseEntity.Base.metadata.create_all(bind=engine)

app = FastAPI()

# --- 数据库依赖 ---
# 这个函数用于获取数据库会话，并在请求结束后自动关闭
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 你的API路由 ---
@app.get("/")
async def read_root():
    return {"message": "Hello, Job Seeker! Welcome to your AI Assistant."}

@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}