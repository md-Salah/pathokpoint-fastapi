import logging
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_mail import FastMail, MessageSchema, MessageType
from pydantic import EmailStr

from app.models import Order
from app.config.email import conf, templates, logo_url
from app.controller.utility import bangladesh_time
from app.controller.order import get_order_by_invoice

logger = logging.getLogger(__name__)


async def send_invoice_email(order: Order, test_email: str | None = None):
    template = templates.get_template('invoice.html')
    body = template.render(order=order, logo_url=logo_url,
                           timestamp=bangladesh_time(order.created_at))

    if test_email:
        email = test_email
    elif order.address and order.address.email:
        email = order.address.email
    else:
        return {"message": "Email address not found."}

    message = MessageSchema(
        subject='Invoice #{}'.format(order.invoice),
        recipients=[email],
        body=body,
        subtype=MessageType.html,
    )

    fm = FastMail(conf)
    await fm.send_message(message)

    return {"message": "Invoice has been sent to your email."}


async def send_signup_otp(email: EmailStr, otp: str, expiry_min: int):
    template = templates.get_template('signup_otp.html')
    body = template.render(email=email, otp=otp,
                           expiry_min=expiry_min, logo_url=logo_url)

    message = MessageSchema(
        subject='{} is your Pathok Point code'.format(otp),
        recipients=[email],
        body=body,
        subtype=MessageType.html
    )

    fm = FastMail(conf)
    await fm.send_message(message)

    logger.info("OTP has been sent to email")


async def send_reset_password_otp(email: EmailStr, otp: str, expiry_min: int):
    template = templates.get_template('reset_password_otp.html')
    body = template.render(email=email, otp=otp,
                           expiry_min=expiry_min, logo_url=logo_url)

    message = MessageSchema(
        subject='{} is your reset password code'.format(otp),
        recipients=[email],
        body=body,
        subtype=MessageType.html
    )

    fm = FastMail(conf)
    await fm.send_message(message)

    logger.info("Reset password OTP has been sent to email")


async def send_email(message: MessageSchema):
    fm = FastMail(conf)
    await fm.send_message(message)

    logger.info("Email has been sent successfully.")


async def payment_recieved_email(order: Order):
    body = '''
    Dear {},\n
    We have received your payment for order #{}.\n
    Amount: {}\n
    Thank you for shopping with us.\n
    '''.format(order.address.name, order.invoice, order.paid)
    
    if order.address and order.address.email:
        message = MessageSchema(
            subject='Payment Received for Order #{}'.format(order.invoice),
            recipients=[order.address.email],
            body=body,
            subtype=MessageType.plain
        )

        fm = FastMail(conf)
        await fm.send_message(message)

        logger.info("Payment received email has been sent.")



# Test email sending
async def test_send_invoice_email(email: str, db: AsyncSession):
    order = await get_order_by_invoice(1, db)
    if order:
        await send_invoice_email(order, test_email=email)
