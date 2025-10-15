# app/controller/resume.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel
import io
import PyPDF2
from docx import Document

from app.database import get_db
from app.model.User import User
from app.model.Resume import Resume
from app.service.resumeService import ResumeService
from app.controller.dependencies import get_current_active_user

router = APIRouter(prefix="/resumes", tags=["Resumes"])


# Pydantic模型
class ResumeBase(BaseModel):
    title: str
    content: Optional[str] = None


class ResumeCreate(ResumeBase):
    pass


class ResumeUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None


class ResumeAIUpdate(BaseModel):
    conversation: str
    ai_suggestion: str


class ResumeResponse(ResumeBase):
    id: int
    original_filename: Optional[str] = None
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


# 工具函数：从上传的文件中提取文本内容
async def extract_text_from_file(file: UploadFile) -> str:
    """
    从PDF或DOCX文件中提取文本
    """
    content = ""
    if file.filename.endswith('.pdf'):
        # 读取PDF文件
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(await file.read()))
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            content += page.extract_text() or ""
    elif file.filename.endswith('.docx'):
        # 读取DOCX文件
        doc = Document(io.BytesIO(await file.read()))
        for para in doc.paragraphs:
            content += para.text + "\n"
    else:
        # 尝试读取为纯文本
        content = (await file.read()).decode('utf-8', errors='replace')
    
    return content


# 创建简历
@router.post("/", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
def create_resume(
    resume_data: ResumeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    创建新简历
    """
    db_resume = ResumeService.create_resume(
        db=db,
        user_id=current_user.id,
        title=resume_data.title,
        content=resume_data.content
    )
    return db_resume


# 上传简历文件
@router.post("/upload", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    title: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    上传简历文件（支持PDF、DOCX、TXT）
    """
    try:
        content = await extract_text_from_file(file)
        db_resume = ResumeService.create_resume(
            db=db,
            user_id=current_user.id,
            title=title,
            content=content,
            original_filename=file.filename
        )
        return db_resume
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文件处理失败: {str(e)}"
        )


# 获取用户的所有简历
@router.get("/", response_model=List[ResumeResponse])
def get_resumes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取当前用户的所有简历列表
    """
    resumes = ResumeService.get_resumes_by_user(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )
    return resumes


# 获取单个简历详情
@router.get("/{resume_id}", response_model=ResumeResponse)
def get_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取简历详情
    """
    db_resume = ResumeService.get_resume_by_id(
        db=db,
        resume_id=resume_id,
        user_id=current_user.id
    )
    if not db_resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="简历不存在"
        )
    return db_resume


# 更新简历
@router.put("/{resume_id}", response_model=ResumeResponse)
def update_resume(
    resume_id: int,
    resume_update: ResumeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    更新简历内容
    """
    db_resume = ResumeService.update_resume(
        db=db,
        resume_id=resume_id,
        user_id=current_user.id,
        title=resume_update.title,
        content=resume_update.content
    )
    if not db_resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="简历不存在"
        )
    return db_resume


# 通过AI对话修改简历
@router.post("/{resume_id}/ai-update", response_model=ResumeResponse)
def update_resume_with_ai(
    resume_id: int,
    ai_update: ResumeAIUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    通过对话交互方式修改简历内容
    """
    db_resume = ResumeService.update_resume_with_ai_suggestion(
        db=db,
        resume_id=resume_id,
        user_id=current_user.id,
        conversation=ai_update.conversation,
        ai_suggestion=ai_update.ai_suggestion
    )
    if not db_resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="简历不存在"
        )
    return db_resume


# 删除简历
@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    删除简历
    """
    success = ResumeService.delete_resume(
        db=db,
        resume_id=resume_id,
        user_id=current_user.id
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="简历不存在"
        )
    return None