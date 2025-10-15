# app/api/v1/endpoints/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel  # 用于定义请求/响应模型

# 导入我们之前写的模块
from app.database import get_db
from app.model.User import User  # 数据库用户模型
from app.service.userService import UserService
from app.security import verify_password, create_access_token
from datetime import timedelta
from app.security import jwt_settings

# 1. 创建API路由实例（前缀为 /users，标签为 Users，方便文档分类）
router = APIRouter(prefix="/users", tags=["Users"])


# ------------------------------
# Pydantic模型：定义注册请求的格式
# ------------------------------
class UserCreate(BaseModel):
    email: str  # 自动验证邮箱格式（FastAPI+Pydantic的特性）
    password: str  # 后续可加验证：min_length=8
    full_name: str | None = None  # 可选字段


# ------------------------------
# Pydantic模型：定义登录响应的格式（返回Token和用户信息）
# ------------------------------
class Token(BaseModel):
    access_token: str
    token_type: str  # 固定为 "bearer"


class UserOut(BaseModel):
    id: int
    email: str
    full_name: str | None = None
    is_active: bool

    # 重要：告诉Pydantic这是ORM模型的输出（支持从SQLAlchemy对象转换）
    class Config:
        orm_mode = True


# ------------------------------
# 接口1：用户注册（POST /users/register）
# ------------------------------
@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register_user(
        user_in: UserCreate,  # 接收用户输入（自动验证格式）
        db: Session = Depends(get_db)  # 依赖注入：获取数据库会话
):
    # 1. 检查邮箱是否已被注册（避免重复）
    db_user = UserService.get_user_by_email(db, user_in.email)
    if db_user:
        # 抛出自定义异常：400 Bad Request，提示邮箱已存在
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # 2. 使用UserService创建新用户
    new_user = UserService.create_user(
        db=db,
        email=user_in.email,
        password=user_in.password,
        full_name=user_in.full_name
    )

    # 3. 返回用户信息（注意：不会返回密码！）
    return new_user


# ------------------------------
# 接口2：用户登录（POST /users/login）
# ------------------------------
@router.post("/login", response_model=Token)
def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),  # 接收登录表单（username=邮箱，password=密码）
        db: Session = Depends(get_db)
):
    # 1. 检查用户是否存在（按邮箱查询）
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},  # 符合OAuth2标准的响应头
        )

    # 2. 验证密码是否正确
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. 生成JWT Token（设置过期时间）
    access_token_expires = timedelta(minutes=jwt_settings.access_token_expire_minutes)
    access_token = create_access_token(
        subject=user.id,  # Token的核心：存储用户ID（后续验证时用）
        expires_delta=access_token_expires
    )

    # 4. 返回Token（符合OAuth2标准：access_token + token_type）
    return {"access_token": access_token, "token_type": "bearer"}