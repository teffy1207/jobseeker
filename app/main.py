# app/main.py

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session

# 从我们创建的模块中导入
from app.model.BaseEntity import BaseEntity
from app.model.Resume import Resume
from app.model.User import User
from app.model.InterviewRecord import InterviewRecord
from app.model.InterviewSchedule import InterviewSchedule
from app.database import engine, SessionLocal, Base


Base.metadata.create_all(bind=engine)

# 1. 导入我们刚刚创建的API根路由
from app.controller.api import api_router

# 2. 创建FastAPI实例
app = FastAPI(title="Job Seeker AI Assistant", version="1.0")

# 3. 只注册这一个总路由！
#    所有API的路径都会自动带上 /api/v1 前缀
app.include_router(api_router, prefix="/api/v1")

# --- 你的API路由 ---
@app.get("/")
async def read_root():
    return {"message": "Hello, Job Seeker! Welcome to your AI Assistant."}

@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
