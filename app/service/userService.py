# app/service/userService.py
from typing import Optional
from sqlalchemy.orm import Session
from app.model.User import User
from app.security import get_password_hash, verify_password


class UserService:
    """
    用户服务类，负责处理与用户相关的业务逻辑
    """
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """
        根据邮箱获取用户
        
        Args:
            db: 数据库会话
            email: 用户邮箱
            
        Returns:
            用户对象或None
        """
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """
        根据ID获取用户
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            
        Returns:
            用户对象或None
        """
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def create_user(db: Session, email: str, password: str, full_name: Optional[str] = None) -> User:
        """
        创建新用户
        
        Args:
            db: 数据库会话
            email: 用户邮箱
            password: 用户密码（明文，会在内部进行哈希处理）
            full_name: 用户全名（可选）
            
        Returns:
            创建的用户对象
        """
        db_user = User(
            email=email,
            hashed_password=get_password_hash(password),
            full_name=full_name,
            is_active=True
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """
        用户认证
        
        Args:
            db: 数据库会话
            email: 用户邮箱
            password: 用户密码（明文）
            
        Returns:
            认证成功返回用户对象，失败返回None
        """
        user = UserService.get_user_by_email(db, email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
    
    @staticmethod
    def update_user_password(db: Session, user_id: int, new_password: str) -> Optional[User]:
        """
        更新用户密码
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            new_password: 新密码（明文）
            
        Returns:
            更新后的用户对象或None
        """
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            return None
        
        user.hashed_password = get_password_hash(new_password)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def update_user_info(db: Session, user_id: int, full_name: Optional[str] = None) -> Optional[User]:
        """
        更新用户信息
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            full_name: 用户全名（可选）
            
        Returns:
            更新后的用户对象或None
        """
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            return None
        
        if full_name is not None:
            user.full_name = full_name
        
        db.commit()
        db.refresh(user)
        return user