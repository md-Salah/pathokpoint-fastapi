import logging
from fastapi_mail import FastMail, MessageSchema, MessageType
from pydantic import EmailStr

from app.models import Order
from app.config.email import conf, templates, logo_url

logger = logging.getLogger(__name__)


async def send_invoice_email(order: Order):
    template = templates.get_template('order_invoice_email.html')
    body = template.render(order=order, logo_url=logo_url)
    
    message = MessageSchema(
        subject='Invoice #{}'.format(order.invoice),
        recipients=[order.customer.email],
        body=body,
        subtype=MessageType.html
    )
    
    fm = FastMail(conf)
    await fm.send_message(message)

    return {"message": "Invoice has been sent to your email."}
  

async def send_signup_otp(email: EmailStr, otp: str, expiry_min: int):
    template = templates.get_template('signup_otp.html')
    body = template.render(email=email, otp=otp, expiry_min=expiry_min, logo_url=logo_url)
    
    message = MessageSchema(
        subject='{} is your Pathok Point code'.format(otp),
        recipients=[email],
        body=body,
        subtype=MessageType.html
    )
    
    fm = FastMail(conf)
    await fm.send_message(message)
    
    logger.info("OTP has been sent to email: %s", email)
    
async def send_reset_password_otp(email: EmailStr, otp: str, expiry_min: int):
    template = templates.get_template('reset_password_otp.html')
    body = template.render(email=email, otp=otp, expiry_min=expiry_min, logo_url=logo_url)
    
    message = MessageSchema(
        subject='{} is your reset password code'.format(otp),
        recipients=[email],
        body=body,
        subtype=MessageType.html
    )
    
    fm = FastMail(conf)
    await fm.send_message(message)
    
    logger.info("Reset password OTP has been sent to email: %s", email)
    
