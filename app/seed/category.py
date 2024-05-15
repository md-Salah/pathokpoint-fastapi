import httpx
import time
from faker import Faker

from app.config.settings import settings

fake = Faker()

async def seed_category(n: int, headers: dict):
    st = time.time()
    counter = 0
    for _ in range(n):
        payload = {
            'name': fake.name(),
            'slug': fake.slug(),
            'description': fake.text(),
            'is_islamic': fake.boolean(),
            'is_english_featured': fake.boolean(),
            'is_bangla_featured': fake.boolean(),
            'is_job_featured': fake.boolean(),
            'is_comics': fake.boolean(),
            'is_popular': fake.boolean(),
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{settings.BASE_URL}/category", json=payload, headers=headers)
            if response.status_code != 201:
                print(response.json())
            else:
                counter += 1
    print(f"{counter}/{n} categories seeded successfully, Average time taken: {((time.time() - st) / n):.2f} sec")
