from fastapi import APIRouter, Depends, status, Query, Response, File, UploadFile, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
import tempfile
import aiofiles

from app.config.database import get_db
import app.controller.image as image_service
import app.pydantic_schema.image as image_schema

router = APIRouter()


@router.get('/image/id/{id}', response_model=image_schema.ImageOut)
async def get_image_by_id(id: UUID, db: AsyncSession = Depends(get_db)):
    image = await image_service.get_image_by_id(id, db)
    return image_schema.ImageOut.model_validate(image)


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


@router.post('/image', response_model=image_schema.ImageOut, status_code=status.HTTP_201_CREATED)
async def upload_image(file: UploadFile = File(...), alt: str = Form(...), db: AsyncSession = Depends(get_db)):
    CHUNK_SIZE = 1 * 1024 * 1024
    dir = 'dummy/tmp'
    
    if file.size is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='File size is unknown')
    elif file.size > 10 * CHUNK_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='File size should not exceed 10MB')

    if file.filename is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='File name is unknown')
    else:
        file.filename = file.filename.replace(' ', '-').lower().strip()

    try:
        with tempfile.NamedTemporaryFile(dir=dir, delete=False) as temp_file:
            tmp_file = temp_file.name
            async with aiofiles.open(tmp_file, 'wb') as f:
                while chunk := await file.read(CHUNK_SIZE):
                    await f.write(chunk)

        image = await image_service.create_image(tmp_file, file.filename, alt, db)

    except Exception as err:
        print(err)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Error while uploading image')

    return image_schema.ImageOut.model_validate(image)


@router.delete('/image/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_image(id: UUID, db: AsyncSession = Depends(get_db)):
    await image_service.delete_image(id, db)
