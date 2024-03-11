from fastapi import APIRouter, Depends, status, Query, Response, File, UploadFile, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.config.database import get_db
import app.controller.image as image_service
import app.pydantic_schema.image as image_schema

router = APIRouter()


# Permission: Public
@router.get('/image/id/{id}', response_model=image_schema.ImageOut)
async def get_image_by_id(id: UUID, db: AsyncSession = Depends(get_db)):
    image = await image_service.get_image_by_id(id, db)
    return image_schema.ImageOut.model_validate(image)


# Permission: Public
@router.get('/images', response_model=list[image_schema.ImageOut])
async def get_all_images(*, page: int = Query(1, ge=1),
                         per_page: int = Query(10, ge=1, le=100),
                         db: AsyncSession = Depends(get_db),  response: Response):
    images = await image_service.get_all_images(page, per_page, db)
    total_images = await image_service.count_image(db)

    response.headers['X-Total-Count'] = str(total_images)
    response.headers['X-Total-Pages'] = str(-(-total_images // per_page))
    response.headers['X-Current-Page'] = str(page)
    response.headers['X-Per-Page'] = str(per_page)

    return [image_schema.ImageOut.model_validate(image) for image in images]


# Permission: Admin
@router.post('/image', status_code=status.HTTP_201_CREATED)
async def upload_image(*, file: UploadFile = File(...), alt: str = Form(...), db: AsyncSession = Depends(get_db)):
    mx_bytes = 1 * 1024 * 1024  # 1 MB
    if file.content_type not in ['image/jpeg', 'image/png']:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Only JPEG and PNG files are allowed')
    elif file.size is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='File size information not available')
    elif file.size > mx_bytes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='File size should be less than 1 MB')
    
    if file.filename:
        file.filename = file.filename.replace(' ', '-').lower()
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='File name not available')
    image = await image_service.create_image(file, alt, db)
    return image_schema.ImageOut.model_validate(image)


# Permission: Admin
# @router.patch('/image/{id}', response_model=image_schema.ImageOut)
# async def update_image(id: UUID, payload: image_schema.UpdateImage, db: AsyncSession = Depends(get_db)):
#     image = await image_service.update_image(id, payload.model_dump(exclude_unset=True), db)
#     return image_schema.ImageOut.model_validate(image)


# Permission: Admin
@router.delete('/image/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_image(id: UUID, db: AsyncSession = Depends(get_db)):
    await image_service.delete_image(id, db)
