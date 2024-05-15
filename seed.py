import asyncio
import uuid

from app.seed.user import seed_user
from app.seed.category import seed_category
from app.seed.author import seed_author
from app.seed.publisher import seed_publisher
from app.seed.tag import seed_tag
from app.seed.book import seed_book, seed_book_bulk

from app.controller.auth import create_jwt_token
from app.constant.role import Role


headers = {
    "Authorization": f"Bearer {create_jwt_token(uuid.uuid4(), Role.admin, 'access')}",
}


async def seed():
    n = 1000
    # await seed_user(n, headers)
    # await seed_category(n, headers)
    # await seed_author(n, headers)
    # await seed_publisher(n, headers)
    # await seed_tag(n, headers)
    # await seed_book(n, headers)
    await seed_book_bulk(n, headers)

if __name__ == "__main__":
    asyncio.run(seed())
