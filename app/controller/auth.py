from datetime import datetime, timedelta, timezone
import jwt
import bcrypt
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.config.settings import settings
from app.models.user import User


def create_jwt_token(id: UUID, role: str) -> str:
    payload = {
        "id": str(id),
        'role': role,
        "expires": (datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp()
    }
    token = jwt.encode(payload, settings.JWT_SECRET,
                       algorithm=settings.JWT_ALGORITHM)
    return token

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        
        expire_time = payload.get('expires', 0)
        current_time = datetime.now(timezone.utc).timestamp()
        if current_time > expire_time:
            raise jwt.ExpiredSignatureError
        
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token signature verification failed",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

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
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return user
