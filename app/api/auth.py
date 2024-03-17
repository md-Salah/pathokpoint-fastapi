from fastapi import Depends, HTTPException, APIRouter, status
from fastapi.security import (OAuth2PasswordBearer, OAuth2PasswordRequestForm)

from app.config.database import get_db, AsyncSession
import app.pydantic_schema.user as user_schema
import app.pydantic_schema.auth as auth_schema
import app.controller.user as user_service
import app.controller.auth as auth_service
import app.controller.email as email_service


router = APIRouter()
oauth_scheme = OAuth2PasswordBearer(tokenUrl="token")


def valid_token(token: str = Depends(oauth_scheme)):
    return auth_service.verify_token(token)


@router.post("/token", response_model=auth_schema.TokenResponse)
async def login_for_access_token(req: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    # we are using email as username
    user = await auth_service.authenticate_user(db, req.username, req.password)
    token = auth_service.create_jwt_token(user.id, user.role, 'access')
    return {"access_token": token, "token_type": "bearer"}


@router.post('/signup', response_model=auth_schema.UserOutWithToken, status_code=status.HTTP_201_CREATED)
async def user_signup(user: user_schema.CreateUser, db: AsyncSession = Depends(get_db)):
    if await user_service.is_user_exist(user.email, db):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Email is already registered, Try login or forget password.")

    new_user = await user_service.create_user(user.model_dump(), db)
    token = auth_service.create_jwt_token(new_user.id, new_user.role, 'access')

    return {
        'user': new_user,
        'token': {
            'access_token': token,
            'token_type': 'bearer'
        }
    }


@router.post('/reset-password')
async def reset_password(payload: auth_schema.ResetPassword, db: AsyncSession = Depends(get_db)):
    user = await user_service.get_user_by_email(payload.email, db)

    reset_token = auth_service.create_jwt_token(
        user.id, user.role, 'reset_password', 10)
    reset_url = 'http://localhost:8000/reset-password?token={}'.format(
        reset_token)

    return await email_service.send_reset_password_email(user.first_name or user.username, user.email, reset_url)


@router.post('/set-new-password')
async def set_new_password(payload: auth_schema.SetNewPassword, db: AsyncSession = Depends(get_db)):
    decoded_token = auth_service.verify_token(payload.token)
    if decoded_token['type'] != 'reset_password':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")

    await user_service.update_user(decoded_token['id'], {'password': payload.new_password}, db)
    return {"message": "Password has been updated successfully."}


@router.post('/request-email-verification')
async def request_email_verification(decoded_token: dict = Depends(valid_token), db: AsyncSession = Depends(get_db)):
    user = await user_service.get_user_by_id(decoded_token['id'], db)
    if user.is_verified:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Email is already verified.")

    confirmation_token = auth_service.create_jwt_token(
        user.id, user.role, 'verification', 10)
    confirmation_url = 'http://localhost:8000/confirm-email?token={}'.format(
        confirmation_token)

    return await email_service.send_verification_email(user.first_name or user.username, user.email, confirmation_url)


@router.get('/verify-email/{token}')
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    decoded_token = auth_service.verify_token(token)
    if decoded_token['type'] != 'verification':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")
    await user_service.update_user(decoded_token['id'], {'is_verified': True}, db)
    return {"message": "Email has been verified successfully."}


@router.get('/get-private-data')
def test_get_private_data(token: dict = Depends(valid_token)):
    return {"message": "You are accessing private data because you have the access token."}
