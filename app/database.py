# app/database.py

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic_settings import BaseSettings

load_dotenv()

# 使用pydantic-settings来加载环境变量，这是更现代、更强大的方式
class Settings(BaseSettings):
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}
    database_url: str
    database_connect_args: dict


settings = Settings()

# 创建数据库引擎
# engine是SQLAlchemy与数据库交互的核心接口
engine = create_engine(
    settings.database_url,
    connect_args=settings.database_connect_args
)

# 创建一个会话工厂，用于创建新的数据库会话
# SessionLocal是一个类，每次调用它都会得到一个新的会话实例
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# SQLAlchemy会根据这个基础类来生成数据库表
Base = declarative_base()


# --- 数据库依赖 ---
# 这个函数用于获取数据库会话，并在请求结束后自动关闭
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()