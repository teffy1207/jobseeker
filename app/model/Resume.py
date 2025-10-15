from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.model.BaseEntity import BaseEntity


class Resume(BaseEntity):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, index=True, nullable=False)  # 简历标题，如 "我的技术简历"
    content = Column(Text)  # 简历的完整文本内容
    original_filename = Column(String) # 上传的原始文件名
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # 关系：每个简历都属于一个用户
    owner = relationship("User", back_populates="resumes")