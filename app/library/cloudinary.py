from starlette.concurrency import run_in_threadpool
import logging
import cloudinary
import cloudinary.uploader
from io import BufferedReader

from app.config.settings import settings

logger = logging.getLogger(__name__)


cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET
)


async def upload_file_to_cloudinary(file: BufferedReader | str, filename: str | None = None, folder: str | None = None) -> dict[str, str] | None:
    try:
        response = await run_in_threadpool(
            cloudinary.uploader.upload, file, filename=filename, use_filename=True, folder=folder
        )
        logger.debug(response)
        return {
            'filename': response['original_filename'] + '.' + response['format'],
            'public_id': response['public_id'],
            'secure_url': response['secure_url'],
        }
    except Exception as err:
        logger.error(err)
        return None


async def update_file(file: BufferedReader | str, public_id: str, filename: str | None = None) -> dict[str, str] | None:
    try:
        response = await run_in_threadpool(
            cloudinary.uploader.upload,
            file, public_id=public_id, filename=filename
        )
        logger.debug(response)
        return {
            'public_id': response['public_id'],
            'secure_url': response['secure_url'],
        }
    except Exception as err:
        logger.error(err)
        return None


def url(public_id: str) -> str:
    return cloudinary.utils.cloudinary_url(public_id)[0]


async def delete_file_from_cloudinary(public_id: str) -> bool:
    try:
        response = await run_in_threadpool(
            cloudinary.uploader.destroy, public_id
        )
        logger.debug(response)
        return response['result'] == 'ok' or response['result'] == 'not found'
    except Exception as err:
        logger.error(err)
        return False
