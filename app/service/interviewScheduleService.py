# app/service/interviewScheduleService.py
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.model.InterviewSchedule import InterviewSchedule


class InterviewScheduleService:
    """
    面试日程服务类，负责处理与面试日程相关的业务逻辑
    """
    
    @staticmethod
    def create_schedule(db: Session, user_id: int, job_position: str, company_name: str,
                       interview_time: datetime, interview_location: Optional[str] = None,
                       interview_type: Optional[str] = None, description: Optional[str] = None) -> InterviewSchedule:
        """
        创建面试日程
        """
        db_schedule = InterviewSchedule(
            job_position=job_position,
            company_name=company_name,
            interview_time=interview_time,
            interview_location=interview_location,
            interview_type=interview_type,
            description=description,
            user_id=user_id
        )
        db.add(db_schedule)
        db.commit()
        db.refresh(db_schedule)
        return db_schedule
    
    @staticmethod
    def get_schedules_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100,
                            is_completed: Optional[bool] = None) -> List[InterviewSchedule]:
        """
        获取用户的所有面试日程
        可选筛选已完成/未完成的日程
        """
        query = db.query(InterviewSchedule).filter(InterviewSchedule.user_id == user_id)
        
        if is_completed is not None:
            query = query.filter(InterviewSchedule.is_completed == is_completed)
        
        # 按面试时间排序，即将到来的面试排在前面
        query = query.order_by(InterviewSchedule.interview_time)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_schedule_by_id(db: Session, schedule_id: int, user_id: int) -> Optional[InterviewSchedule]:
        """
        根据ID获取面试日程
        """
        return db.query(InterviewSchedule).filter(
            InterviewSchedule.id == schedule_id,
            InterviewSchedule.user_id == user_id
        ).first()
    
    @staticmethod
    def update_schedule(db: Session, schedule_id: int, user_id: int, **kwargs) -> Optional[InterviewSchedule]:
        """
        更新面试日程
        """
        db_schedule = InterviewScheduleService.get_schedule_by_id(db, schedule_id, user_id)
        if not db_schedule:
            return None
        
        # 更新提供的字段
        for key, value in kwargs.items():
            if hasattr(db_schedule, key):
                setattr(db_schedule, key, value)
        
        db.commit()
        db.refresh(db_schedule)
        return db_schedule
    
    @staticmethod
    def delete_schedule(db: Session, schedule_id: int, user_id: int) -> bool:
        """
        删除面试日程
        """
        db_schedule = InterviewScheduleService.get_schedule_by_id(db, schedule_id, user_id)
        if not db_schedule:
            return False
        
        db.delete(db_schedule)
        db.commit()
        return True
    
    @staticmethod
    def get_upcoming_interviews(db: Session, user_id: int, days: int = 7) -> List[InterviewSchedule]:
        """
        获取未来几天内的面试日程
        """
        end_date = datetime.now() + timedelta(days=days)
        
        return db.query(InterviewSchedule).filter(
            and_(
                InterviewSchedule.user_id == user_id,
                InterviewSchedule.is_completed == False,
                InterviewSchedule.interview_time >= datetime.now(),
                InterviewSchedule.interview_time <= end_date
            )
        ).order_by(InterviewSchedule.interview_time).all()
    
    @staticmethod
    def mark_as_completed(db: Session, schedule_id: int, user_id: int) -> Optional[InterviewSchedule]:
        """
        将面试标记为已完成
        """
        return InterviewScheduleService.update_schedule(
            db=db,
            schedule_id=schedule_id,
            user_id=user_id,
            is_completed=True
        )
    
    @staticmethod
    def set_reminder(db: Session, schedule_id: int, user_id: int, reminder: bool = True) -> Optional[InterviewSchedule]:
        """
        设置或取消面试提醒
        """
        return InterviewScheduleService.update_schedule(
            db=db,
            schedule_id=schedule_id,
            user_id=user_id,
            is_reminder_set=reminder
        )