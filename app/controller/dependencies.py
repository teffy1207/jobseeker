# app/controller/dependencies.py
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.model.User import User
from app.security import jwt_settings

# OAuth2密码Bearer流程
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login")


class TokenData(BaseModel):
    """
    Token数据模型
    """
    user_id: Optional[int] = None


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    获取当前用户
    这是一个依赖项，用于保护需要认证的API端点
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 解码JWT Token
        payload = jwt.decode(token, jwt_settings.secret_key, algorithms=[jwt_settings.algorithm])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=int(user_id))
    except JWTError:
        raise credentials_exception
    
    # 查询用户
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if user is None:
        raise credentials_exception
    
    # 检查用户是否激活
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    获取当前活跃用户
    这是一个额外的验证层，确保用户是活跃的
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user