import httpx
import time
from faker import Faker

from app.config.settings import settings

fake = Faker()


async def seed_publisher(n: int, headers: dict):
    st = time.time()
    counter = 0
    for _ in range(n):
        payload = {
        'name': fake.company(),
        'slug': fake.slug(),
        'description': fake.text(),
        'is_islamic': fake.boolean(),
        'is_english': fake.boolean(),
        'is_popular': fake.boolean(),
        'is_big_sale': fake.boolean(),
        'country': fake.country_code(representation="alpha-2"),
        'book_published': fake.random_int(min=1, max=100),
    }
            
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{settings.BASE_URL}/publisher", json=payload, headers=headers)
            if response.status_code != 201:
                print(response.json())
            else:
                counter += 1
    print(f"{counter}/{n} publishers seeded successfully, Average time taken: {((time.time() - st) / n):.2f} sec")
    
