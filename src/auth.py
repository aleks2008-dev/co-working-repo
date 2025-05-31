from datetime import datetime, timedelta, timezone
from typing import Optional, Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt import PyJWTError
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from model import UserItemCreate
from database import UserORM

SECRET_KEY = "secret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRY_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

async def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(
    data: dict,  # Добавляем параметр data
    expires_delta: timedelta = None,
    secret_key: str = SECRET_KEY,
    algorithm: str = ALGORITHM
) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    #to_encode.update({"exp": expire})
    to_encode["exp"]= expire
    return jwt.encode(to_encode, secret_key, algorithm=algorithm)

async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserItemCreate:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        surname: str = payload.get("surname")
        phone: str = payload.get("phone")
        role = payload.get("role")
        disabled: bool = payload.get("disabled", False)
        password: str = payload.get("password")
        if not username or not role:
            raise credentials_exception

        return UserItemCreate(  # Возвращаем объект модели
            username=username,
            surname=surname,
            phone=phone,
            role=role,
            disabled=disabled,
            password=password
        )
    except InvalidTokenError:
        raise credentials_exception

async def get_current_active_user(current_user: Annotated[UserItemCreate, Depends(get_current_user)]):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

class RoleChecker:
  def __init__(self, allowed_roles: list[str]):
    self.allowed_roles = allowed_roles

  def __call__(self, user: Annotated[UserItemCreate, Depends(get_current_active_user)]):
    if user.role not in self.allowed_roles:
     raise HTTPException(status_code=403, detail="Operation not permitted")