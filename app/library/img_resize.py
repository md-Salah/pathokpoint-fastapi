from PIL import Image
import io
import logging
import aiofiles

logger = logging.getLogger(__name__)

async def img_resize(file_path: str, dimension: tuple, max_kb: int) -> None:
    try:
        logger.debug(f"Resizing image: {file_path}")
        with Image.open(file_path) as image: 
            if 'A' in image.getbands():
                image = image.convert('RGB')
            
            img_buffer = io.BytesIO()
            image.save(img_buffer, format='JPEG')
            initial_size = f"{img_buffer.tell() / 1024:,.1f}KB"
            

            image.thumbnail(dimension, Image.Resampling.LANCZOS)
            quality = 100
            counter = 0
            while img_buffer.tell() > max_kb * 1024:
                quality -= 5
                img_buffer = io.BytesIO()
                image.save(img_buffer, format='JPEG', optimize=True, quality=quality)
                counter += 1
                if quality <= 15:
                    break
                
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(img_buffer.getvalue())
                
            final_size = f"{img_buffer.tell() / 1024:,.1f}KB"
            logger.info(f"Image size reduced from {initial_size} to {final_size} in {counter} iterations")
            
    except Exception as err:
        logger.error(f'Error while resizing image: {err}')
        
