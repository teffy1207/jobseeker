from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.model.BaseEntity import Base

class InterviewRecord(Base):
    __tablename__ = "interview_records"

    id = Column(Integer, primary_key=True, index=True)
    job_position = Column(String, index=True, nullable=False) # 面试的岗位
    question = Column(Text, nullable=False) # AI提出的问题
    user_answer = Column(Text) # 用户的回答
    ai_feedback = Column(Text) # AI的反馈和评分
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系：每个面试记录都属于一个用户
    user = relationship("User", back_populates="interview_records")