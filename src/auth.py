from datetime import datetime, timedelta, timezone
from typing import Optional, Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from jose import JWTError
from jwt import PyJWTError
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from model import UserItemCreate, CurrentUser
from database import UserORM
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_session
from sqlalchemy import select
from typing import Any, Dict, Union
load_dotenv()

class AuthConfig:
    SECRET_KEY = os.getenv("SECRET_KEY")
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY not set in environment variables")

    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)

async def get_password_hash(password) -> str:
    """Generate a password hash."""
    return pwd_context.hash(password)

# def create_access_token(
#     data: dict,  # Добавляем параметр data
#     expires_delta: timedelta = None,
# ) -> str:
#     """Create a JWT access token."""
#     to_encode = data.copy()
#     expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=AuthConfig.ACCESS_TOKEN_EXPIRE_MINUTES))
#     to_encode.update({"exp": expire})
#     to_encode["exp"]= expire
#     return jwt.encode(to_encode, AuthConfig.SECRET_KEY, algorithm=AuthConfig.ALGORITHM)

def create_access_token(
        subject: Union[str, int],  # ID пользователя (обязательный)
        role: str = None,  # Роль пользователя
        expires_delta: timedelta = None,
        **extra_data: Any  # Дополнительные поля для токена
) -> str:
    """
    Создает JWT токен с обязательным subject (sub claim)

    Args:
        subject: Уникальный идентификатор пользователя (str/int)
        role: Роль пользователя (добавится в токен как 'role')
        expires_delta: Время жизни токена
        **extra_data: Дополнительные данные для включения в токен

    Returns:
        Закодированный JWT токен
    """
    payload = {
        "sub": str(subject),  # Гарантируем строковый формат
        **extra_data
    }

    if role is not None:
        payload["role"] = role

    expire = datetime.now(timezone.utc) + (
            expires_delta or timedelta(minutes=AuthConfig.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload["exp"] = expire

    return jwt.encode(
        payload,
        AuthConfig.SECRET_KEY,
        algorithm=AuthConfig.ALGORITHM
    )

# async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_session)) -> CurrentUser:
#     """Get the current authenticated user from the JWT token."""
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = jwt.decode(token, AuthConfig.SECRET_KEY, algorithms=[AuthConfig.ALGORITHM])
#         username: str = payload.get("sub")
#         if username is None:
#             raise credentials_exception
#     except JWTError:
#         raise credentials_exception
#
#     result = await db.execute(select(UserORM).where(UserORM.name == username))
#     user = result.scalar_one_or_none()
#     if not user:
#         raise credentials_exception
#
#     return CurrentUser(
#         id=user.id,
#         email=user.email,
#         name=user.name,
#         role=user.role,
#         disabled=user.disabled,
#         access_token=token,
#         token_type="bearer"
#     )

async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_session)
) -> CurrentUser:
    """Получает пользователя из JWT токена с проверкой структуры"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, AuthConfig.SECRET_KEY, algorithms=[AuthConfig.ALGORITHM])

        # Обязательная проверка наличия sub
        user_id = payload.get("sub")
        if not user_id:
            raise credentials_exception

        # Ищем пользователя по ID
        user = await db.get(UserORM, user_id)
        if not user:
            raise credentials_exception

        # Проверяем роль (если есть в токене)
        if "role" in payload and payload["role"] != user.role:
            raise credentials_exception

        return CurrentUser(
            id=user.id,
            email=user.email,
            name=user.name,
            role=user.role,
            disabled=user.disabled,
            access_token=token,
            token_type="bearer"
        )

    except (JWTError, AttributeError) as e:
        raise credentials_exception

async def get_current_active_user(current_user: Annotated[UserItemCreate, Depends(get_current_user)]) -> UserItemCreate:
    """Verify that the current user is active."""
    if current_user.disabled:
        raise HTTPException(status_code=403, detail="Inactive user")
    return current_user

class RoleChecker:
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    async def __call__(self, current_user: Annotated[dict, Depends(get_current_user)]):
        # if current_user.get("role") not in self.allowed_roles:
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=403,
                detail="Operation not permitted for your role",
                headers={"WWW-Authenticate": "Bearer"}
            )