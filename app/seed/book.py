import httpx
import random
import time

from app.config.settings import settings
from app.constant import Condition

async def seed_book():
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

    data = [
        {'name': 'সোনার তরী 1', 'slug': 'sonar-tori-1', 'sku': '123657', 'regular_price': 340, 'sale_price': 215,
            'manage_stock': True, 'quantity': 12, 'is_used': True, 'condition': Condition.old_like_new.value},
        {'name': 'স্বপ্নের দেশ 2', 'slug': 'shopner-desh-2', 'sku': '123658', 'regular_price': 250, 'sale_price': 240,
            'manage_stock': True, 'quantity': 13, 'is_used': True, 'condition': Condition.old_readable.value},
        {'name': 'গহীন বন 3', 'slug': 'gohin-bon-3', 'sku': '123659', 'regular_price': 600, 'sale_price': 250,
            'manage_stock': True, 'quantity': 13, 'is_used': True, 'condition': Condition.old_like_new.value},
        {'name': 'মায়াবী এক রাত 4', 'slug': 'mayabi-ek-raat-4', 'sku': '123660', 'regular_price': 300, 'sale_price': 240,
            'manage_stock': True, 'quantity': 15, 'is_used': True, 'condition': Condition.old_good_enough.value},
        {'name': 'স্বপ্নের দেশ 5', 'slug': 'shopner-desh-5', 'sku': '123661', 'regular_price': 300, 'sale_price': 215,
            'manage_stock': True, 'quantity': 13, 'is_used': True, 'condition': Condition.old_good_enough.value, },
        {'name': 'স্বপ্নের দেশ 6', 'slug': 'shopner-desh-6', 'sku': '123662', 'regular_price': 490, 'sale_price': 210,
            'manage_stock': True, 'quantity': 12, 'is_used': True, 'condition': Condition.old_good_enough.value},
        {'name': 'নীল দরিয়া 7', 'slug': 'neel-doriya-7', 'sku': '123663', 'regular_price': 610, 'sale_price': 310,
            'manage_stock': True, 'quantity': 12, 'is_used': True, 'condition': Condition.old_like_new.value},
        {'name': 'মায়াবী এক রাত 8', 'slug': 'mayabi-ek-raat-8', 'sku': '123664', 'regular_price': 600, 'sale_price': 600,
            'manage_stock': False, 'quantity': 12, 'is_used': False, 'condition': Condition.new.value},
        {'name': 'মায়াবী এক রাত 9', 'slug': 'mayabi-ek-raat-9', 'sku': '123665', 'regular_price': 680, 'sale_price': 360,
            'manage_stock': False, 'quantity': 15, 'is_used': False, 'condition': Condition.new.value},
        {'name': 'স্বপ্নের দেশ 10', 'slug': 'shopner-desh-10', 'sku': '123666', 'regular_price': 480, 'sale_price': 155,
            'manage_stock': False, 'quantity': 15, 'is_used': False, 'condition': Condition.new.value}
    ]

    counter = 0
    st = time.time()
    for payload in data:
        payload['authors'] = [authors[random.randint(0, len(authors) - 1)]]
        payload['categories'] = [categories[random.randint(0, len(categories) - 1)]]
        payload['publisher'] = publishers[random.randint(0, len(publishers) - 1)]
        payload['tags'] = [tags[random.randint(0, len(tags) - 1)]]
        
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(f"{settings.BASE_URL}/book", json=payload)
            if response.status_code != 201:
                print(response.json())
            else:
                counter += 1
    print(f"{counter}/{len(data)} books seeded successfully")
    if counter:
        print('Average time taken {} sec'.format(round((time.time() - st)/counter, 2)))
