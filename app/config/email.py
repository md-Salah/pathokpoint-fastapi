from fastapi_mail import ConnectionConfig
from fastapi.templating import Jinja2Templates

from app.config.settings import settings

conf = ConnectionConfig(
    MAIL_SERVER=settings.SMTP_SERVER,
    MAIL_PORT=settings.SMTP_PORT,
    MAIL_USERNAME=settings.SMTP_USERNAME,
    MAIL_PASSWORD=settings.SMTP_PASSWORD,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    MAIL_FROM=settings.SMTP_USERNAME,
    MAIL_FROM_NAME='Pathok Point'
    )

templates = Jinja2Templates(directory="app/templates")
logo_url = settings.LOGO_URL
