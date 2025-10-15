# app/controller/interview.py
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.model.User import User
from app.service.interviewService import InterviewService
from app.controller.dependencies import get_current_active_user

router = APIRouter(prefix="/interviews", tags=["Interviews"])


# Pydantic模型
class InterviewRecordBase(BaseModel):
    job_position: str
    question: str
    user_answer: Optional[str] = None
    ai_feedback: Optional[str] = None


class InterviewRecordCreate(InterviewRecordBase):
    pass


class InterviewAnswerUpdate(BaseModel):
    user_answer: str


class InterviewFeedbackResponse(BaseModel):
    score: int
    strengths: List[str]
    weaknesses: List[str]
    suggestions: List[str]


class InterviewRecordResponse(InterviewRecordBase):
    id: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class InterviewPreparationRequest(BaseModel):
    job_description: str
    resume_id: Optional[int] = None


class InterviewPreparationResponse(BaseModel):
    guide: str


# 创建面试记录
@router.post("/", response_model=InterviewRecordResponse, status_code=status.HTTP_201_CREATED)
def create_interview_record(
    record_data: InterviewRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    创建面试记录
    """
    db_record = InterviewService.create_interview_record(
        db=db,
        user_id=current_user.id,
        job_position=record_data.job_position,
        question=record_data.question,
        user_answer=record_data.user_answer,
        ai_feedback=record_data.ai_feedback
    )
    return db_record


# 获取用户的所有面试记录
@router.get("/", response_model=List[InterviewRecordResponse])
def get_interview_records(
    skip: int = 0,
    limit: int = 100,
    job_position: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取当前用户的所有面试记录
    可选按职位筛选
    """
    records = InterviewService.get_interview_records_by_user(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )
    
    # 如果指定了职位，进行筛选
    if job_position:
        records = [r for r in records if job_position.lower() in r.job_position.lower()]
    
    return records


# 获取单个面试记录详情
@router.get("/{record_id}", response_model=InterviewRecordResponse)
def get_interview_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取面试记录详情
    """
    db_record = InterviewService.get_interview_record_by_id(
        db=db,
        record_id=record_id,
        user_id=current_user.id
    )
    if not db_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="面试记录不存在"
        )
    return db_record


# 更新面试回答
@router.put("/{record_id}/answer", response_model=InterviewRecordResponse)
def update_interview_answer(
    record_id: int,
    answer_update: InterviewAnswerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    更新面试回答
    """
    db_record = InterviewService.update_interview_answer(
        db=db,
        record_id=record_id,
        user_id=current_user.id,
        user_answer=answer_update.user_answer
    )
    if not db_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="面试记录不存在"
        )
    return db_record


# 获取AI面试反馈
@router.post("/{record_id}/feedback", response_model=InterviewFeedbackResponse)
def get_interview_feedback(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取AI对面试回答的反馈
    """
    # 首先获取面试记录
    db_record = InterviewService.get_interview_record_by_id(
        db=db,
        record_id=record_id,
        user_id=current_user.id
    )
    if not db_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="面试记录不存在"
        )
    
    if not db_record.user_answer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请先提交面试回答"
        )
    
    # 分析回答并获取反馈
    feedback = InterviewService.analyze_interview_answer(
        question=db_record.question,
        answer=db_record.user_answer,
        job_position=db_record.job_position
    )
    
    # 保存反馈到数据库
    feedback_text = f"评分: {feedback['score']}/100\n\n"
    feedback_text += "优势:\n- " + "\n- ".join(feedback['strengths']) + "\n\n"
    feedback_text += "改进点:\n- " + "\n- ".join(feedback['weaknesses']) + "\n\n"
    feedback_text += "建议:\n- " + "\n- ".join(feedback['suggestions'])
    
    InterviewService.add_ai_feedback(
        db=db,
        record_id=record_id,
        user_id=current_user.id,
        ai_feedback=feedback_text
    )
    
    return feedback


# 生成面试问题
@router.post("/generate-questions", response_model=List[str])
def generate_interview_questions(
    job_position: str,
    resume_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    生成面试问题
    可选提供简历ID以生成更匹配的问题
    """
    resume_content = None
    
    # 如果提供了简历ID，获取简历内容
    if resume_id:
        from app.service.resumeService import ResumeService
        resume = ResumeService.get_resume_by_id(db, resume_id, current_user.id)
        if resume:
            resume_content = resume.content
    
    # 生成问题
    questions = InterviewService.generate_interview_questions(
        job_position=job_position,
        resume_content=resume_content
    )
    
    # 自动创建面试记录
    for question in questions:
        InterviewService.create_interview_record(
            db=db,
            user_id=current_user.id,
            job_position=job_position,
            question=question
        )
    
    return questions


# 生成面试准备指南
@router.post("/preparation-guide", response_model=InterviewPreparationResponse)
def generate_preparation_guide(
    request: InterviewPreparationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    根据岗位JD自动生成面试准备建议
    可选提供简历ID以生成更个性化的建议
    """
    resume_content = None
    
    # 如果提供了简历ID，获取简历内容
    if request.resume_id:
        from app.service.resumeService import ResumeService
        resume = ResumeService.get_resume_by_id(db, request.resume_id, current_user.id)
        if resume:
            resume_content = resume.content
    
    # 生成准备指南
    guide = InterviewService.generate_interview_preparation_guide(
        job_description=request.job_description,
        resume_content=resume_content
    )
    
    return InterviewPreparationResponse(guide=guide)