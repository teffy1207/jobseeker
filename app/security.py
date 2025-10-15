# app/core/security.py
from datetime import datetime, timedelta
from typing import Any, Union, Optional
from pydantic import Field

from jose import jwt
from passlib.context import CryptContext

# 1. 配置密码哈希上下文（使用bcrypt算法）
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 2. JWT相关配置（从.env文件读取，避免硬编码！）
# 先去你的.env文件添加这3行配置
# SECRET_KEY = "your-secret-key-here"  # 生成方法：openssl rand -hex 32
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Token有效期30分钟
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()  # 加载.env文件


class JWTSettings(BaseSettings):
    secret_key: str = Field(..., alias="JWT_SECRET_KEY")
    algorithm: str = Field(..., alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(..., alias="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")

    class Config:
        env_file = ".env"
        extra = "allow"  # 或 "allow"


jwt_settings = JWTSettings()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # 与哈希时保持一致，截断密码到72字节
    truncated_password = plain_password[:72]
    return pwd_context.verify(truncated_password, hashed_password)


def get_password_hash(password: str) -> str:
    # bcrypt算法限制密码长度为72字节
    # 截断密码以避免ValueError异常
    truncated_password = password[:72]
    return pwd_context.hash(truncated_password)


def create_access_token(
        subject: Union[str, Any],  # 通常是用户ID（作为Token的核心标识）
        expires_delta: Optional[timedelta] = None
) -> str:
    # 1. 设置Token过期时间
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(
            minutes=jwt_settings.access_token_expire_minutes
        )

    # 2. 构造Token的"载荷"（Payload）：包含用户ID和过期时间
    to_encode = {"exp": expire, "sub": str(subject)}

    # 3. 用密钥和算法签名Token（确保不被篡改）
    encoded_jwt = jwt.encode(
        to_encode,
        jwt_settings.secret_key,
        algorithm=jwt_settings.algorithm
    )
    return encoded_jwt