from fastapi_mail import FastMail, MessageSchema, MessageType
from pydantic import EmailStr

from app.models import Order
from app.config.email import conf, templates, logo_url

async def send_reset_password_email(name: str, email: EmailStr, reset_url: str):
    template = templates.get_template('reset_password_email.html')
    body = template.render(name=name, reset_url=reset_url, logo_url=logo_url)
    
    message = MessageSchema(
        subject='Password reset request',
        recipients=[email],
        body=body,
        subtype=MessageType.html
    )
    
    fm = FastMail(conf)
    await fm.send_message(message)
    
    return {"message": "Reset password link has been sent to your email."}

async def send_verification_email(name: str, email: EmailStr, confirmation_url: str):
    template = templates.get_template('email_verification.html')
    body = template.render(name=name, reset_url=confirmation_url, logo_url=logo_url)
    
    message = MessageSchema(
        subject='Email verification request',
        recipients=[email],
        body=body,
        subtype=MessageType.html
    )
    
    fm = FastMail(conf)
    await fm.send_message(message)
    
    return {"message": "Verification link has been sent to your email."}


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
  
