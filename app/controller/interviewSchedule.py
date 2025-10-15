# app/controller/interviewSchedule.py
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.database import get_db
from app.model.User import User
from app.service.interviewScheduleService import InterviewScheduleService
from app.controller.dependencies import get_current_active_user

router = APIRouter(prefix="/interview-schedules", tags=["Interview Schedules"])


# Pydantic模型
class InterviewScheduleBase(BaseModel):
    job_position: str
    company_name: str
    interview_time: datetime
    interview_location: Optional[str] = None
    interview_type: Optional[str] = None
    description: Optional[str] = None


class InterviewScheduleCreate(InterviewScheduleBase):
    pass


class InterviewScheduleUpdate(BaseModel):
    job_position: Optional[str] = None
    company_name: Optional[str] = None
    interview_time: Optional[datetime] = None
    interview_location: Optional[str] = None
    interview_type: Optional[str] = None
    description: Optional[str] = None
    is_completed: Optional[bool] = None
    is_reminder_set: Optional[bool] = None


class InterviewScheduleResponse(InterviewScheduleBase):
    id: int
    is_completed: bool
    is_reminder_set: bool
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


# 创建面试日程
@router.post("/", response_model=InterviewScheduleResponse, status_code=status.HTTP_201_CREATED)
def create_interview_schedule(
    schedule_data: InterviewScheduleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    创建面试日程
    """
    # 验证面试时间不能早于当前时间
    if schedule_data.interview_time <= datetime.now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="面试时间不能早于当前时间"
        )
    
    db_schedule = InterviewScheduleService.create_schedule(
        db=db,
        user_id=current_user.id,
        job_position=schedule_data.job_position,
        company_name=schedule_data.company_name,
        interview_time=schedule_data.interview_time,
        interview_location=schedule_data.interview_location,
        interview_type=schedule_data.interview_type,
        description=schedule_data.description
    )
    return db_schedule


# 获取用户的所有面试日程
@router.get("/", response_model=List[InterviewScheduleResponse])
def get_interview_schedules(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_completed: Optional[bool] = Query(None, description="筛选已完成/未完成的日程"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取当前用户的所有面试日程
    """
    schedules = InterviewScheduleService.get_schedules_by_user(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        is_completed=is_completed
    )
    return schedules


# 获取单个面试日程详情
@router.get("/{schedule_id}", response_model=InterviewScheduleResponse)
def get_interview_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取面试日程详情
    """
    db_schedule = InterviewScheduleService.get_schedule_by_id(
        db=db,
        schedule_id=schedule_id,
        user_id=current_user.id
    )
    if not db_schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="面试日程不存在"
        )
    return db_schedule


# 更新面试日程
@router.put("/{schedule_id}", response_model=InterviewScheduleResponse)
def update_interview_schedule(
    schedule_id: int,
    schedule_update: InterviewScheduleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    更新面试日程
    """
    # 构建更新参数字典，过滤掉None值
    update_data = schedule_update.model_dump(exclude_unset=True)
    
    # 如果更新面试时间，验证不能早于当前时间
    if "interview_time" in update_data and update_data["interview_time"] <= datetime.now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="面试时间不能早于当前时间"
        )
    
    db_schedule = InterviewScheduleService.update_schedule(
        db=db,
        schedule_id=schedule_id,
        user_id=current_user.id,
        **update_data
    )
    
    if not db_schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="面试日程不存在"
        )
    
    return db_schedule


# 删除面试日程
@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_interview_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    删除面试日程
    """
    success = InterviewScheduleService.delete_schedule(
        db=db,
        schedule_id=schedule_id,
        user_id=current_user.id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="面试日程不存在"
        )
    
    return None


# 获取即将到来的面试
@router.get("/upcoming/list", response_model=List[InterviewScheduleResponse])
def get_upcoming_interviews(
    days: int = Query(7, ge=1, le=30, description="查询未来几天内的面试"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取未来几天内的面试日程
    """
    schedules = InterviewScheduleService.get_upcoming_interviews(
        db=db,
        user_id=current_user.id,
        days=days
    )
    return schedules


# 标记面试为已完成
@router.post("/{schedule_id}/complete", response_model=InterviewScheduleResponse)
def mark_interview_as_completed(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    将面试标记为已完成
    """
    db_schedule = InterviewScheduleService.mark_as_completed(
        db=db,
        schedule_id=schedule_id,
        user_id=current_user.id
    )
    
    if not db_schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="面试日程不存在"
        )
    
    return db_schedule


# 设置面试提醒
@router.post("/{schedule_id}/reminder", response_model=InterviewScheduleResponse)
def set_interview_reminder(
    schedule_id: int,
    reminder: bool = Query(True, description="是否开启提醒"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    设置或取消面试提醒
    """
    db_schedule = InterviewScheduleService.set_reminder(
        db=db,
        schedule_id=schedule_id,
        user_id=current_user.id,
        reminder=reminder
    )
    
    if not db_schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="面试日程不存在"
        )
    
    return db_schedule