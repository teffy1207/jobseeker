from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.model.BaseEntity import BaseEntity


class InterviewSchedule(BaseEntity):
    """
    面试日程模型
    """
    __tablename__ = "interview_schedules"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    job_position = Column(String, index=True, nullable=False)  # 面试职位
    company_name = Column(String, index=True, nullable=False)  # 公司名称
    interview_time = Column(DateTime, nullable=False)  # 面试时间
    interview_location = Column(String)  # 面试地点
    interview_type = Column(String)  # 面试类型（视频、电话、现场等）
    description = Column(Text)  # 其他描述信息
    is_completed = Column(Boolean, default=False)  # 是否已完成
    is_reminder_set = Column(Boolean, default=False)  # 是否设置提醒
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 所属用户

    # 关系：每个面试日程都属于一个用户
    user = relationship("User", back_populates="interview_schedules")