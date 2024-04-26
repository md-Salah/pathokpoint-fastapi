from datetime import datetime, timedelta, timezone
import jwt
import bcrypt
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from typing import Literal, Annotated

from app.config.database import get_db
from app.constant.role import Role
from app.config.settings import settings
from app.models.user import User

oauth_scheme = OAuth2PasswordBearer(tokenUrl="token")


def unauthorized_exception(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={
            "message": detail,
        },
        headers={"WWW-Authenticate": "Bearer"},
    )


def create_jwt_token(id: UUID, role: Role, type: Literal['access', 'refresh', 'reset_password', 'verification'], minutes: int | None = None) -> str:
    minutes = minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES
    payload = {
        "id": str(id),
        'role': str(role),
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

        return payload
    except jwt.ExpiredSignatureError:
        raise unauthorized_exception("Token has expired")
    except jwt.InvalidSignatureError:
        raise unauthorized_exception("Invalid token")
    except Exception:
        raise unauthorized_exception("Could not validate")


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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"}
        )
    elif not verify_password(password, user.password):
        raise unauthorized_exception("Incorrect email or password")

    return user


def valid_access_token(token: str = Depends(oauth_scheme)):
    data = verify_token(token)
    if data.get('type') == 'access':
        return data
    raise unauthorized_exception("Invalid token")

def valid_admin_token(token: dict = Depends(valid_access_token)):
    if token.get('role') == Role.admin.value:
        return token
    raise unauthorized_exception("Unauthorized access")

async def current_user(token: dict = Depends(valid_access_token), db: AsyncSession = Depends(get_db)) -> User:
    if token.get('id'):
        user = await db.scalar(select(User).where(User.id == token.get('id')))
        if user:
            return user
    raise unauthorized_exception("User not found")

async def current_admin(token: dict = Depends(valid_admin_token), db: AsyncSession = Depends(get_db)) -> User:
    if token.get('id'):
        user = await db.scalar(select(User).where(User.id == token.get('id')))
        if user:
            return user
    raise unauthorized_exception("User not found")

CurrentUser = Annotated[User, Depends(current_user)]
CurrentAdmin = Annotated[User, Depends(current_admin)]
AccessToken = Annotated[dict, Depends(valid_access_token)]
ValidAdminToken = Annotated[dict, Depends(valid_admin_token)]

