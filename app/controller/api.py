# app/controller/api.py

from fastapi import APIRouter

# 导入所有的子路由
from app.controller.user import router as users_router
from app.controller.resume import router as resumes_router
from app.controller.interview import router as interviews_router
from app.controller.job import router as jobs_router
from app.controller.interviewSchedule import router as interview_schedules_router

# 创建一个API根路由实例
api_router = APIRouter()

# 将所有子路由注册到根路由上
# 注意：这里的prefix是相对于根路由的
api_router.include_router(users_router, prefix="/users", tags=["Users"])
api_router.include_router(resumes_router, prefix="/resumes", tags=["Resumes"])
api_router.include_router(interviews_router, prefix="/interviews", tags=["Interviews"])
api_router.include_router(jobs_router, prefix="/jobs", tags=["Jobs"])
api_router.include_router(interview_schedules_router, prefix="/schedules", tags=["Interview Schedules"])