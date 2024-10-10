import logging

import app.controller.email as email_service
from app.config.settings import settings

logger = logging.getLogger(__name__)


async def contact_us(payload: dict) -> None:
    logger.debug('Contact us payload: {}'.format(payload))

    body = '''
    name: {}\n
    email: {}\n
    phone_number: {}\n
    message: {}\n
    '''.format(payload['name'], payload['email'], payload['phone_number'], payload['message'])

    await email_service.send_email(email_service.MessageSchema(
        subject='{} sends a message'.format(payload['name']),
        recipients=settings.ADMIN_EMAILS,
        body=body,
        subtype=email_service.MessageType.plain
    ))

    logger.info('Contact us email sent to admin')
