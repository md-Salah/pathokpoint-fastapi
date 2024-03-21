import asyncio

from app.seed.user import seed_user
from app.seed.author import seed_author
from app.seed.book import seed_book

async def seed():
    await asyncio.gather(
        # seed_user(),
        # seed_author(),
        seed_book()
    )
    
asyncio.run(seed())