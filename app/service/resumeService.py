# app/service/resumeService.py
from typing import List, Optional
from sqlalchemy.orm import Session
from app.model.Resume import Resume
from app.model.User import User


class ResumeService:
    """
    简历服务类，负责处理与简历相关的业务逻辑
    """
    
    @staticmethod
    def create_resume(db: Session, user_id: int, title: str, content: str, original_filename: Optional[str] = None) -> Resume:
        """
        创建新简历
        """
        db_resume = Resume(
            title=title,
            content=content,
            original_filename=original_filename,
            owner_id=user_id
        )
        db.add(db_resume)
        db.commit()
        db.refresh(db_resume)
        return db_resume
    
    @staticmethod
    def get_resumes_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Resume]:
        """
        获取用户的所有简历
        """
        return db.query(Resume).filter(Resume.owner_id == user_id).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_resume_by_id(db: Session, resume_id: int, user_id: int) -> Optional[Resume]:
        """
        根据ID获取简历，确保属于当前用户
        """
        return db.query(Resume).filter(
            Resume.id == resume_id,
            Resume.owner_id == user_id
        ).first()
    
    @staticmethod
    def update_resume(db: Session, resume_id: int, user_id: int, title: Optional[str] = None, 
                     content: Optional[str] = None) -> Optional[Resume]:
        """
        更新简历内容
        """
        db_resume = ResumeService.get_resume_by_id(db, resume_id, user_id)
        if not db_resume:
            return None
        
        if title is not None:
            db_resume.title = title
        if content is not None:
            db_resume.content = content
        
        db.commit()
        db.refresh(db_resume)
        return db_resume
    
    @staticmethod
    def delete_resume(db: Session, resume_id: int, user_id: int) -> bool:
        """
        删除简历
        """
        db_resume = ResumeService.get_resume_by_id(db, resume_id, user_id)
        if not db_resume:
            return False
        
        db.delete(db_resume)
        db.commit()
        return True
    
    @staticmethod
    def update_resume_with_ai_suggestion(db: Session, resume_id: int, user_id: int, 
                                       conversation: str, ai_suggestion: str) -> Optional[Resume]:
        """
        通过对话交互方式修改简历内容
        """
        db_resume = ResumeService.get_resume_by_id(db, resume_id, user_id)
        if not db_resume:
            return None
        
        # 根据AI建议更新简历内容
        # 这里可以实现更复杂的内容分析和更新逻辑
        updated_content = db_resume.content + f"\n\n# AI更新建议\n{ai_suggestion}"
        db_resume.content = updated_content
        
        db.commit()
        db.refresh(db_resume)
        return db_resume