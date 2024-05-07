from fastapi import Depends, APIRouter, status, Request, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
import logging
import json

import app.pydantic_schema.user as user_schema
import app.pydantic_schema.auth as auth_schema
import app.controller.user as user_service
import app.controller.auth as auth_service
import app.controller.email as email_service
from app.config.database import Session
from app.controller.auth import AccessToken, CurrentUser
from app.controller.redis import get_redis, set_redis
from app.controller.exception import BadRequestException
from app.controller.otp import generate_otp

logger = logging.getLogger(__name__)

router = APIRouter(prefix='/auth')


@router.post("/token", response_model=auth_schema.TokenResponse)
async def login_for_access_token(db: Session, req: OAuth2PasswordRequestForm = Depends()):
    # we are using email as username
    user = await auth_service.authenticate_user(db, req.username, req.password)
    token = auth_service.create_jwt_token(user.id, user.role, 'access')
    logger.info(f'{user.username} logged in successfully')
    return {"access_token": token, "token_type": "bearer"}


@router.post('/signup')
async def user_signup(user: user_schema.CreateUser, request: Request, background_tasks: BackgroundTasks, db: Session):
    if await user_service.is_user_exist(user.email, db):
        raise BadRequestException(
            "Email is already registered, Try login or forget password.")

    payload = user.model_dump()
    payload['password'] = auth_service.get_hashed_password(
        payload['password'].get_secret_value())

    otp = generate_otp()
    expiry_min = 10
    expiry_sec = 60 * expiry_min

    background_tasks.add_task(
        set_redis, request, user.email, json.dumps({
            'payload': payload,
            'otp': otp
        }), expiry_sec)

    background_tasks.add_task(
        email_service.send_signup_otp, user.email, otp, expiry_min)

    return {"detail": {"message": "OTP has been sent to your email. Please verify within {} minutes.".format(expiry_min)
                       }}


@router.post('/verify-otp', response_model=user_schema.UserOut, status_code=status.HTTP_201_CREATED)
async def verify_otp(payload: auth_schema.VerifyOTP, request: Request, db: Session):
    data = await get_redis(request, payload.email)
    if not data:
        raise BadRequestException("OTP expired, SignUp again.")

    data = json.loads(data)
    if data['otp'] == payload.otp:
        return await user_service.create_user(data['payload'], db)
    else:
        raise BadRequestException("Invalid OTP, Try again.")


@router.post('/reset-password')
async def reset_password(payload: auth_schema.ResetPassword, request: Request, background_tasks: BackgroundTasks, db: Session):
    user = await user_service.get_user_by_email(payload.email, db)

    otp = generate_otp()
    expiry_min = 10

    background_tasks.add_task(
        set_redis, request, payload.email, otp, expiry_min * 60)
    background_tasks.add_task(
        email_service.send_reset_password_otp, user.email, otp, expiry_min)

    return {"detail": {"message": "OTP has been sent to your email. Please reset your password within {} minutes.".format(expiry_min)}}


@router.post('/set-new-password')
async def set_new_password(payload: auth_schema.SetNewPassword, request: Request, db: Session):
    user = await user_service.get_user_by_email(payload.email, db)
    otp = await get_redis(request, payload.email)
    if not otp:
        raise BadRequestException("OTP expired, Try again.")

    if otp != payload.otp:
        raise BadRequestException("Invalid OTP, Try again.")

    await user_service.update_user(user.id, {'password': payload.new_password}, db)

    return {"message": "Password has been updated successfully."}


@router.post('/change-password')
async def change_password(payload: auth_schema.ChangePassword, user: CurrentUser, db: Session):
    if not auth_service.verify_password(payload.current_password.get_secret_value(), user.password):
        raise BadRequestException("Password is incorrect.")

    await user_service.update_user(user.id, {'password': payload.new_password}, db)
    return {"message": "Password has been updated successfully."}


@router.get('/get-private-data')
def test_get_private_data(_: AccessToken):
    return {"message": "You are accessing private data because you have the access token."}
