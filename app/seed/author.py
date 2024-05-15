import httpx
from datetime import datetime, timedelta
import random
import time
from faker import Faker

from app.config.settings import settings

fake = Faker()

def random_date():
    start = datetime(1800, 1, 1)
    end = datetime.now()
    return (start + timedelta(days=random.randint(0, (end - start).days))).strftime("%Y-%m-%d")

async def seed_author(n: int, headers: dict):
    st = time.time()
    counter = 0
    for _ in range(n):
        payload = {
            "name": fake.name(),
            "slug": fake.slug(),
            "description": fake.text(),
            "birth_date": fake.date_of_birth().strftime("%Y-%m-%d"),
            "death_date": fake.date_of_birth().strftime("%Y-%m-%d"),
            "book_published": fake.random_int(min=1, max=100),
            "city": fake.city(),
            "country": fake.country_code(representation="alpha-2"),
            "is_popular": fake.boolean(),
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{settings.BASE_URL}/author", json=payload, headers=headers)
            if response.status_code != 201:
                print(response.json())
            else:
                counter += 1
    print(f"{counter}/{n} authors seeded successfully, Average time taken: {((time.time() - st) / n):.2f} sec")