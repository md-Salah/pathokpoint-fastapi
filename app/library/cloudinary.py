import cloudinary
import cloudinary.uploader

from app.config.settings import settings

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET
)


def upload_file_to_cloudinary(file, filename, public_id):
    try:
        response = cloudinary.uploader.upload(file, public_id=public_id, filename=filename)
        print(response)
        return response['secure_url']
    except Exception as e:
        print(e)
        return None