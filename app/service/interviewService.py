# app/service/interviewService.py
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.model.InterviewRecord import InterviewRecord


class InterviewService:
    """
    面试服务类，负责处理与面试相关的业务逻辑
    """
    
    @staticmethod
    def create_interview_record(db: Session, user_id: int, job_position: str, 
                              question: str, user_answer: Optional[str] = None, 
                              ai_feedback: Optional[str] = None) -> InterviewRecord:
        """
        创建面试记录
        """
        db_record = InterviewRecord(
            job_position=job_position,
            question=question,
            user_answer=user_answer,
            ai_feedback=ai_feedback,
            user_id=user_id
        )
        db.add(db_record)
        db.commit()
        db.refresh(db_record)
        return db_record
    
    @staticmethod
    def get_interview_records_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[InterviewRecord]:
        """
        获取用户的所有面试记录
        """
        return db.query(InterviewRecord).filter(
            InterviewRecord.user_id == user_id
        ).order_by(InterviewRecord.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_interview_record_by_id(db: Session, record_id: int, user_id: int) -> Optional[InterviewRecord]:
        """
        根据ID获取面试记录
        """
        return db.query(InterviewRecord).filter(
            InterviewRecord.id == record_id,
            InterviewRecord.user_id == user_id
        ).first()
    
    @staticmethod
    def update_interview_answer(db: Session, record_id: int, user_id: int, 
                              user_answer: str) -> Optional[InterviewRecord]:
        """
        更新用户的面试回答
        """
        db_record = InterviewService.get_interview_record_by_id(db, record_id, user_id)
        if not db_record:
            return None
        
        db_record.user_answer = user_answer
        db.commit()
        db.refresh(db_record)
        return db_record
    
    @staticmethod
    def add_ai_feedback(db: Session, record_id: int, user_id: int, ai_feedback: str) -> Optional[InterviewRecord]:
        """
        添加AI反馈
        """
        db_record = InterviewService.get_interview_record_by_id(db, record_id, user_id)
        if not db_record:
            return None
        
        db_record.ai_feedback = ai_feedback
        db.commit()
        db.refresh(db_record)
        return db_record
    
    @staticmethod
    def generate_interview_questions(job_position: str, resume_content: Optional[str] = None) -> List[str]:
        """
        根据职位和简历生成面试问题
        这里可以集成OpenAI API来生成更智能的问题
        """
        # 示例问题，实际应用中可以调用AI API生成
        questions = [
            f"请介绍一下您为什么对{job_position}这个职位感兴趣？",
            "您认为您最适合这个职位的三个优势是什么？",
            "请描述一个您在过去工作中解决的技术难题。",
            "您如何处理工作中的压力和挑战？",
            "您对未来3-5年的职业规划是什么？"
        ]
        
        # 如果有简历内容，可以基于简历定制问题
        if resume_content:
            questions.append("请详细介绍一下您简历中提到的某个项目经验。")
        
        return questions
    
    @staticmethod
    def analyze_interview_answer(question: str, answer: str, job_position: str) -> Dict[str, Any]:
        """
        分析面试回答并提供反馈
        这里可以集成OpenAI API进行更智能的分析
        """
        # 示例反馈，实际应用中可以调用AI API生成
        feedback = {
            "score": 85,  # 0-100的评分
            "strengths": ["回答结构清晰", "提供了具体例子"],
            "weaknesses": ["可以更详细地解释技术细节", "缺乏与职位的相关性"],
            "suggestions": ["建议在回答中突出与该职位相关的技能", "可以准备更多相关的实际案例"]
        }
        
        return feedback
    
    @staticmethod
    def generate_interview_preparation_guide(job_description: str, resume_content: Optional[str] = None) -> str:
        """
        根据岗位JD自动生成面试准备建议
        """
        # 示例准备指南，实际应用中可以调用AI API生成
        guide = f"""# 面试准备指南

## 职位分析
根据提供的职位描述，这是一个需要重点关注以下方面的职位：
- 技术能力要求
- 项目经验要求
- 软技能要求

## 准备要点
1. 复习相关技术栈
2. 准备3-5个能展示你能力的项目案例
3. 了解公司业务和文化
4. 准备自己的问题清单

## 简历针对性调整
请确保你的简历重点突出与该职位相关的经验和技能。

## 常见面试问题预测
- 技术深度问题
- 项目经验细节
- 团队协作经历
- 职业规划
"""
        
        return guide