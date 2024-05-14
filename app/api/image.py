from fastapi import APIRouter, status, Query, Response, File, UploadFile, Form
from uuid import UUID

from app.config.database import Session
import app.controller.image as image_service
import app.pydantic_schema.image as image_schema
from app.constant.image_folder import ImageFolder
from app.controller.auth import AdminAccessToken

router = APIRouter(prefix='/image')


@router.get('/id/{id}', response_model=image_schema.ImageOut)
async def get_image_by_id(id: UUID, db: Session):
    return await image_service.get_image_by_id(id, db)


@router.get('/all', response_model=list[image_schema.ImageOut])
async def get_all_images(*, page: int = Query(1, ge=1),
                         per_page: int = Query(10, ge=1, le=100),
                         _: AdminAccessToken,
                         db: Session,  response: Response):
    images = await image_service.get_all_images(page, per_page, db)
    total_images = await image_service.count_image(db)

    response.headers['X-Total-Count'] = str(total_images)
    response.headers['X-Total-Pages'] = str(-(-total_images // per_page))
    response.headers['X-Current-Page'] = str(page)
    response.headers['X-Per-Page'] = str(per_page)

    return images


@router.post('', response_model=image_schema.ImageOut, status_code=status.HTTP_201_CREATED)
async def upload_image_by_admin(*, file: UploadFile = File(...), filename: str = Form(None), alt: str = Form(""), folder: ImageFolder = Form(ImageFolder.dummy), _: AdminAccessToken, db: Session):
    return await image_service.create_image(file, filename, alt, folder, db)


@router.put('/{id}', response_model=image_schema.ImageOut)
async def update_image(*, id: UUID, file: UploadFile = File(...), filename: str = Form(None), alt: str = Form(""), _: AdminAccessToken, db: Session):
    return await image_service.update_image(id, file, filename, alt, db)


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_image(id: UUID, _: AdminAccessToken, db: Session):
    await image_service.delete_image(id, db)
