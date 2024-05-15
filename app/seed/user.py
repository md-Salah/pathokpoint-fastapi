import httpx
import time
from faker import Faker

from app.config.settings import settings

fake = Faker()


async def seed_user(n: int, headers: dict):
    st = time.time()
    counter = 0
    for _ in range(n):

        payload = {
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "email": fake.email(),
            "password": fake.password(),
            "phone_number": "+8801" + str(fake.random_int(min=100000000, max=999999999)),
            "role": "customer",
            "is_verified": fake.boolean()
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(f"{settings.BASE_URL}/user", json=payload, headers=headers)
            if response.status_code != 201:
                print(response.json())
            else:
                counter += 1
    print(f"{counter}/{n} users seeded successfully, Average time taken: {((time.time() - st) / n):.2f} sec")
