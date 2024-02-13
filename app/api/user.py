from typing import Union, List
from app.auth.jwt_handler import create_jwt_token, decode_jwt_token, verify_password, get_hashed_password
from fastapi import Depends, HTTPException, APIRouter, status

from app.config.database import get_db, Session
from app.models.user import UserCreate, User, UserReadWithToken, UserRead
from fastapi.security import (OAuth2PasswordBearer, OAuth2PasswordRequestForm)
from pydantic import BaseModel


router = APIRouter()

oauth_scheme = OAuth2PasswordBearer(tokenUrl="token")

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class LoginSchema(BaseModel):
    email: str
    password: str

@router.post("/token", response_model=TokenResponse)
async def generate_token(req: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, req.username, req.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_jwt_token(user.id, user.email, user.role.value)
    return {"access_token": token, "token_type": "bearer"}

def is_user_exist(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def authenticate_user(db: Session, email: str, password: str):
    user = is_user_exist(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"}
        )
    elif not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incorrect password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return user

async def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth_scheme)) -> Union[User, None]:
    return await very_token(db, token)

async def very_token(db: Session, token: str) -> Union[User, None]:
    '''verify token from login'''
    try:
        payload = decode_jwt_token(token)
        if payload:
            user = db.get(User, payload.get('id'))
            return user
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Token",
                headers={"WWW-Authenticate": "Bearer"}                
            )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token",
            headers={"WWW-Authenticate": "Bearer"}
        )

@router.post('/signup', status_code=status.HTTP_201_CREATED, response_model=UserReadWithToken)
async def user_signup(*, db: Session = Depends(get_db), user: UserCreate):
   
    if is_user_exist(db, user.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is already registered")
    
    # Hash the password
    new_user = User(**user.dict(exclude_unset=True))
    new_user.password = get_hashed_password(new_user.password)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Generate JWT token
    assert new_user.id is not None
    token = create_jwt_token(new_user.id, new_user.email, new_user.role.value)

    return {**new_user.dict(), 'token': token}

    
@router.get('/users', response_model=List[UserRead])
def get_all_users(db: Session = Depends(get_db), user = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not an authorized user")
    elif user.role.value != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not an authorized admin")
    
    users = db.query(User).all()
    return users
