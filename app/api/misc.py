from fastapi import APIRouter, BackgroundTasks

import app.controller.misc as service
import app.pydantic_schema.misc as schema

# This is miscellanous API router
router = APIRouter(prefix='/misc')


@router.post('/contact-us')
async def contact_us(payload: schema.ContactUs, bg_task: BackgroundTasks) -> dict:
    bg_task.add_task(service.contact_us, payload.model_dump())
    return {'message': 'Your message has been sent successfully'}
