import httpx
import time
from faker import Faker
from app.config.settings import settings

fake = Faker()


async def seed_tag(n: int, headers: dict):
    st = time.time()
    counter = 0
    for _ in range(n):
        payload = {
            'name': fake.text(20),
            'slug': fake.slug(),
            'private': fake.boolean(),
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(f"{settings.BASE_URL}/tag", json=payload, headers=headers)
            if response.status_code != 201:
                print(response.json())
            else:
                counter += 1
    print(f"{counter}/{n} tags seeded successfully, Average time taken: {((time.time() - st) / n):.2f} sec")
