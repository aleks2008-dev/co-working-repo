import os
from datetime import datetime, timedelta, timezone
from typing import Annotated, Any, Union
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from config import Settings

import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from database import UserORM, get_session
from model import CurrentUser

load_dotenv()

class AuthConfig:
    SECRET_KEY = os.getenv("SECRET_KEY")
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY not set in environment variables")

    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password) -> str:
    """Generate a password hash."""
    return pwd_context.hash(password)


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

    except JWTError:
        raise credentials_exception
    except AttributeError:
        # Отдельная обработка для AttributeError
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user attributes",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None


class RoleChecker:
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    async def __call__(self, current_user: Annotated[dict, Depends(get_current_user)]):
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=403,
                detail="Operation not permitted for your role",
                headers={"WWW-Authenticate": "Bearer"}
            )


def generate_reset_token(email: str) -> str:
    expires = datetime.utcnow() + timedelta(hours=1)
    return jwt.encode(
        {"sub": email, "exp": expires},
        AuthConfig.SECRET_KEY,
        algorithm="HS256"
    )


def verify_reset_token(token: str) -> str:
    try:
        payload = jwt.decode(token, AuthConfig.SECRET_KEY, algorithms=["HS256"])
        return payload["sub"]
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid token")


async def send_reset_email(email: str, token: str):
    reset_link = f"https://yourapp.com/reset-password?token={token}"
    message = MessageSchema(
        subject="Password Reset",
        recipients=[email],
        body=f"Click to reset: {reset_link}",
    )
    await FastMail(Settings.email_conf).send_message(message)