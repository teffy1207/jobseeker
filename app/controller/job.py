# app/controller/job.py
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.model.User import User
from app.service.jobService import JobService
from app.controller.dependencies import get_current_active_user

router = APIRouter(prefix="/jobs", tags=["Jobs"])


# Pydantic模型
class JobSearchRequest(BaseModel):
    keyword: str
    location: Optional[str] = None
    job_type: Optional[str] = None


class JobResponse(BaseModel):
    id: str
    title: str
    company: str
    location: str
    description: str
    salary: Optional[str] = None
    posted_date: Optional[str] = None
    apply_url: Optional[str] = None


class JobDetailsResponse(JobResponse):
    requirements: Optional[List[str]] = None
    benefits: Optional[List[str]] = None
    interview_location: Optional[str] = None


class RoutePlanRequest(BaseModel):
    start_location: str
    destination: str
    departure_time: Optional[str] = None


class RouteStep(BaseModel):
    instruction: str


class RoutePlanResponse(BaseModel):
    start: str
    destination: str
    distance: str
    duration: str
    steps: List[str]
    transportation: str


class ResumeJobMatchRequest(BaseModel):
    resume_id: int
    job_description: str


class ResumeJobMatchResponse(BaseModel):
    match_score: int
    matched_skills: List[str]
    missing_skills: List[str]
    recommendations: List[str]


# 创建服务实例
job_service = JobService()


# 搜索工作
@router.get("/search", response_model=List[JobResponse])
async def search_jobs(
    keyword: str = Query(..., description="搜索关键词"),
    location: Optional[str] = Query(None, description="工作地点"),
    job_type: Optional[str] = Query(None, description="工作类型"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    搜索匹配的应聘岗位
    """
    try:
        jobs = await job_service.search_jobs(
            keyword=keyword,
            location=location,
            job_type=job_type
        )
        return jobs
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"搜索失败: {str(e)}"
        )


# 获取工作详情
@router.get("/{job_id}", response_model=JobDetailsResponse)
async def get_job_details(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取职位详细信息
    """
    job = await job_service.get_job_details(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="职位不存在"
        )
    return job


# 规划面试路线
@router.post("/route-plan", response_model=RoutePlanResponse)
async def plan_interview_route(
    request: RoutePlanRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    规划面试路线
    """
    try:
        route = await job_service.plan_interview_route(
            start_location=request.start_location,
            destination=request.destination,
            departure_time=request.departure_time
        )
        return route
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"路线规划失败: {str(e)}"
        )


# 匹配简历与职位
@router.post("/match-resume", response_model=ResumeJobMatchResponse)
def match_resume_with_job(
    request: ResumeJobMatchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    匹配简历与职位的契合度
    """
    # 首先获取简历内容
    from app.service.resumeService import ResumeService
    resume = ResumeService.get_resume_by_id(db, request.resume_id, current_user.id)
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="简历不存在"
        )
    
    # 进行匹配分析
    match_result = job_service.match_resume_with_job(
        resume_content=resume.content,
        job_description=request.job_description
    )
    
    return match_result