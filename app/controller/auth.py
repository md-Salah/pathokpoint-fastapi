from datetime import datetime, timedelta, timezone
import jwt
import bcrypt
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from typing import Literal, Annotated, TypedDict

from app.config.database import Session
from app.constant.role import Role
from app.config.settings import settings
from app.models.user import User
from app.controller.exception import UnauthorizedException, NotFoundException

oauth_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


class Token(TypedDict):
    id: UUID
    role: str
    expires: datetime
    type: Literal['access', 'refresh']


def create_jwt_token(id: UUID, role: Role, type: Literal['access', 'refresh'], minutes: int | None = None) -> str:
    minutes = minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES
    payload = {
        "id": str(id),
        'role': role.value,
        "expires": (datetime.now(timezone.utc) + timedelta(minutes=minutes)).timestamp(),
        "type": type
    }
    token = jwt.encode(payload, settings.JWT_SECRET,
                       algorithm=settings.JWT_ALGORITHM)
    return token


def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET,
                             algorithms=[settings.JWT_ALGORITHM])

        expire_time = payload.get('expires', 0)
        current_time = datetime.now(timezone.utc).timestamp()
        if current_time > expire_time:
            raise jwt.ExpiredSignatureError

        payload['id'] = UUID(payload['id'])
        return payload
    except jwt.ExpiredSignatureError:
        raise UnauthorizedException("Token has expired")
    except jwt.InvalidSignatureError:
        raise UnauthorizedException("Invalid token")
    except Exception:
        raise UnauthorizedException("Could not validate")


def get_hashed_password(password: str) -> str:
    pwd_bytes = password.encode('utf-8')
    return bcrypt.hashpw(pwd_bytes, bcrypt.gensalt()).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        password=plain_password.encode('utf-8'),
        hashed_password=hashed_password.encode('utf-8')
    )


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar()
    if not user:
        raise NotFoundException("User not found")
    elif not verify_password(password, user.password):
        raise UnauthorizedException("Incorrect email or password")

    return user


def valid_access_token(token: str = Depends(oauth_scheme)):
    data = verify_token(token)
    if data.get('type') == 'access':
        return data
    raise UnauthorizedException("Invalid token")


def valid_admin_token(token: dict = Depends(valid_access_token)):
    if token.get('role') == Role.admin.value:
        return token
    raise UnauthorizedException("Unauthorized access")


async def current_user(db: Session, token: dict = Depends(valid_access_token)) -> User:
    if token.get('id'):
        user = await db.scalar(select(User).where(User.id == token.get('id')))
        if user:
            return user
    raise UnauthorizedException("User not found")


async def current_admin(db: Session, token: dict = Depends(valid_admin_token)) -> User:
    if token.get('id'):
        user = await db.scalar(select(User).where(User.id == token.get('id')))
        if user:
            return user
    raise UnauthorizedException("User not found")


AccessToken = Annotated[Token, Depends(valid_access_token)]
AdminAccessToken = Annotated[Token, Depends(valid_admin_token)]
CurrentUser = Annotated[User, Depends(current_user)]
CurrentAdmin = Annotated[User, Depends(current_admin)]
