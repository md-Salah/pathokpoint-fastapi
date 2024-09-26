from fastapi import APIRouter, status, Query, Response, File, UploadFile, BackgroundTasks
from uuid import UUID

from app.config.database import Session
import app.controller.image as image_service
import app.library.s3 as s3
import app.pydantic_schema.image as image_schema
from app.controller.auth import AdminAccessToken, AccessToken

router = APIRouter(prefix='/image')


@router.get('/id/{id}', response_model=image_schema.ImageOut)
async def get_image_by_id(id: UUID, _: AdminAccessToken, db: Session):
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


@router.post('/admin', response_model=list[image_schema.ImageOut], status_code=status.HTTP_201_CREATED)
async def inventory_img_uploader(*, files: list[UploadFile] = File(...),
                                 book_id: UUID | None = None,
                                 author_id: UUID | None = None,
                                 category_id: UUID | None = None,
                                 publisher_id: UUID | None = None,
                                 payment_gateway_id: UUID | None = None,
                                 is_banner: bool = Query(
                                     False, description="Banner of author/publisher/category"),
                                 is_append: bool = Query(
                                     False, description="Appending image to book"),
                                 optimizer: bool = Query(
                                     False, description="Optimize image"),
                                 _: AdminAccessToken,
                                 db: Session):
    return await image_service.inventory_img_uploader(
        files, db,
        book_id=book_id,
        author_id=author_id,
        category_id=category_id,
        publisher_id=publisher_id,
        payment_gateway_id=payment_gateway_id,
        is_banner=is_banner,
        is_append=is_append,
        optimizer=optimizer,
    )


@router.post('/user', response_model=list[image_schema.ImageOut], status_code=status.HTTP_201_CREATED)
async def customer_img_uploader(*, files: list[UploadFile] = File(...),
                                is_profile_pic: bool = False,
                                review_id: UUID | None = None,
                                token: AccessToken,
                                db: Session):
    return await image_service.customer_img_uploader(
        files, token['id'], db,
        is_profile_pic=is_profile_pic,
        review_id=review_id,
    )


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_image(id: UUID, _: AdminAccessToken, db: Session):
    await image_service.delete_image(id, db)


@router.get('/attach-books')
async def attach_s3_images_with_books(*, page: int = Query(0, ge=0), _: AdminAccessToken, bg_task: BackgroundTasks, db: Session):
    bg_task.add_task(s3.attach_s3_imgs_with_books, page, db)
    return {
        'message': 'Images are being attached with books'
    }
