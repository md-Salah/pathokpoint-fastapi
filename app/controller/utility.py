import slugify as slg

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Any

def slugify(text):
    """_summary_
    Args:
        text (str): any text (e.g. 'Hello World', 'আমার সোনার বাংলা')
    Returns:
        str: Lower case english slug (e.g. 'hello-world', 'amar-sonar-bangla')
    """    
    return slg.slugify(text).replace('aa', 'a').replace('ii', 'i').replace('ea', 'o')


async def unique_slug(base_slug: str, cls: Any, db: AsyncSession) -> str:
    slug = slugify(base_slug)
    counter = 1
    while True:
        result = await db.execute(select(cls).filter_by(slug=slug))
        if not result.scalars().first():
            break
        slug = f"{base_slug}-{counter}"
        counter += 1
    return slug
