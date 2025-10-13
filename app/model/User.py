from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.model.BaseEntity import Base

# 用户模型
class User(Base):
    __tablename__ = "users"  # 数据库表名

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系：一个用户可以有多个简历
    resumes = relationship("Resume", back_populates="owner", cascade="all, delete-orphan")
    # 关系：一个用户可以有多个面试记录
    interview_records = relationship("InterviewRecord", back_populates="user", cascade="all, delete-orphan")
