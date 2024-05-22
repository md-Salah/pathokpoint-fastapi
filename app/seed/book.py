import httpx
import random
import time
from faker import Faker

from app.config.settings import settings
from app.constant import Condition

fake = Faker()


async def get_related_data():
    authors = []
    categories = []
    publishers = []
    tags = []
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.BASE_URL}/author/all")
        if response.status_code == 200:
            [authors.append(author['id']) for author in response.json()]
        else:
            print(response.json())

        response = await client.get(f"{settings.BASE_URL}/category/all")
        if response.status_code == 200:
            [categories.append(category['id']) for category in response.json()]
        else:
            print(response.json())

        response = await client.get(f"{settings.BASE_URL}/publisher/all")
        if response.status_code == 200:
            [publishers.append(publisher['id'])
             for publisher in response.json()]
        else:
            print(response.json())

        response = await client.get(f"{settings.BASE_URL}/tag/all")
        if response.status_code == 200:
            [tags.append(tag['id']) for tag in response.json()]
        else:
            print(response.json())

    return authors, categories, publishers, tags


def generate_book(authors, categories, publishers, tags):
    payload = {
        'name': fake.sentence(nb_words=4).strip('.'),
        'slug': fake.slug(),
        'sku': f'sk-{fake.random_int(min=100000, max=999999)}',
        'regular_price': random.randint(1000, 5000),
        'sale_price': random.randint(50, 900),
        'manage_stock': random.choice([True, False]),
        'quantity': random.randint(1, 20),
        'condition': random.choice([cond.value for cond in Condition]),
        'authors': [random.choice(authors)],
        'categories': list(set([random.choice(categories), random.choice(categories)])),
        'publisher': random.choice(publishers),
        'tags': [random.choice(tags)]
    }
    payload['is_used'] = payload['condition'] != Condition.new.value
    return payload


async def seed_book(n: int, headers: dict):
    authors, categories, publishers, tags = await get_related_data()

    st = time.time()
    counter = 0
    for _ in range(n):
        payload = generate_book(authors, categories, publishers, tags)

        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(f"{settings.BASE_URL}/book", json=payload, headers=headers)
            if response.status_code != 201:
                print(response.json())
            else:
                counter += 1
    print(f"{counter}/{n} books seeded successfully, Average time taken: {
          ((time.time() - st) / n):.2f} sec")


async def seed_book_bulk(n: int, headers: dict):
    authors, categories, publishers, tags = await get_related_data()

    st = time.time()
    counter = 0

    payload = [generate_book(authors, categories, publishers, tags)
               for _ in range(n)]
    async with httpx.AsyncClient(timeout= 10 * 60) as client:
        response = await client.post(f"{settings.BASE_URL}/book/bulk", json=payload, headers=headers)
        if response.status_code != 201:
            print(response.json())
        else:
            counter = len(response.json())
    print(f"{counter}/{n} books seeded successfully, Average time taken: {
          ((time.time() - st) / n):.6f} sec")
    print(f"Required time: {(time.time() - st):.2f} sec")
