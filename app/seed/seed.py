import asyncio

from app.seed.user import seed_user
from app.seed.category import seed_category
from app.seed.author import seed_author
from app.seed.publisher import seed_publisher
from app.seed.tag import seed_tag
from app.seed.book import seed_book

async def seed():
    await seed_user()
    await seed_category()
    await seed_author()
    await seed_publisher()
    await seed_tag()
    await seed_book()
    
asyncio.run(seed())

