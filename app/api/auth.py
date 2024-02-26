from fastapi import Depends, HTTPException, APIRouter, status
from fastapi.security import (OAuth2PasswordBearer, OAuth2PasswordRequestForm)

from app.config.database import get_db, AsyncSession
import app.pydantic_schema.user as user_schema
import app.pydantic_schema.auth as auth_schema
import app.controller.user as user_service
import app.controller.auth as auth_service


router = APIRouter()
oauth_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_token(token: str = Depends(oauth_scheme)):
    return auth_service.verify_token(token)

@router.post("/token", response_model=auth_schema.TokenResponse)
async def login_for_access_token(req: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await auth_service.authenticate_user(db, req.username, req.password) # we are using email as username
    token = auth_service.create_jwt_token(user.id, user.role)
    return {"access_token": token, "token_type": "bearer"}


@router.post('/signup', response_model=user_schema.ReadUserWithToken, status_code=status.HTTP_201_CREATED)
async def user_signup(user: user_schema.CreateUser, db: AsyncSession = Depends(get_db)):
    _user = await user_service.is_user_exist(db, user.email)
    if _user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Email is already registered, Try login or forget password.")

    user.password = auth_service.get_hashed_password(user.password)
    new_user = await user_service.create_user(db, user)
    token = auth_service.create_jwt_token(new_user.id, new_user.role)

    return {
        'user': new_user,
        'token': {
            'access_token': token,
            'token_type': 'bearer'
        }
    }


@router.get('/get-private-data')
def test_get_private_data(payload: dict = Depends(verify_token)):
    return {"message": "You are accessing private data because you have the access token."}
