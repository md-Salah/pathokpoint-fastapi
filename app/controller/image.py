from fastapi import HTTPException, status, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Sequence
from uuid import UUID
from ftplib import FTP

from app.models.image import Image
from app.config.settings import settings

async def get_image_by_id(id: UUID, db: AsyncSession) -> Image:
    image = await db.get(Image, id)
    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Image with id ({id}) not found')
    return image


async def get_all_images(page: int, per_page: int, db: AsyncSession) -> Sequence[Image]:
    offset = (page - 1) * per_page
    result = await db.execute(select(Image).offset(offset).limit(per_page))
    return result.scalars().all()


async def create_image(file: UploadFile, alt: str, db: AsyncSession) -> Image:
    src = upload_file_via_ftp(file)
    if not src:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail='Image upload failed')
    
    image = Image(name= file.filename, src=src, alt=alt)
    db.add(image)
    await db.commit()
    return image

# async def update_image(id: UUID, payload: dict, db: AsyncSession) -> Image:
#     image = await get_image_by_id(id, db)
#     [setattr(image, key, value)
#      for key, value in payload.items()]
#     await db.commit()
#     return image


async def delete_image(id: UUID, db: AsyncSession) -> None:
    image = await get_image_by_id(id, db)
    await db.delete(image)
    await db.commit()


async def count_image(db: AsyncSession) -> int:
    result = await db.execute(select(func.count()).select_from(Image))
    return result.scalar_one()



def upload_file_via_ftp(file: UploadFile, remote_directory='fastapi-img'):

    try:
        remote_file_path = '/{}/{}'.format(remote_directory, file.filename)

        with FTP(settings.ftp_host) as ftp:
            ftp.login(user=settings.ftp_user, passwd=settings.ftp_pass)
            ftp.storbinary('STOR ' + remote_file_path, file.file)

        src = 'http://mdsalah.customerserver003003.eurhosting.net/fastapi-img/{}'.format(file.filename)
        return src
    
    except Exception as err:
        print(err)
    
    return None

