import httpx

from app.config.settings import settings


async def seed_book():
    author_data = [
        {
            "name": "হুমায়ূন আহমেদ",
            "slug": "humayun-ahmed",
            "description": "বাংলাদেশের প্রখ্যাত লেখক",
            "birth_date": "1948-11-13",
            "death_date": "2012-07-19",
            "book_published": 200,
            "city": "dhaka",
            "country": "BD",
            "is_popular": True,
        },
        {
            "name": "Rabindranath Tagore",
            "slug": "rabindranath-tagore",
            "description": "Nobel laureate Indian poet and musician",
            "birth_date": "1861-05-07",
            "death_date": "1941-08-07",
            "book_published": 150,
            "city": "Kolkata",
            "country": "IN",
            "is_popular": True,
        },
    ]

    authors = []
    for payload in author_data:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{settings.BASE_URL}/author", json=payload)
            if response.status_code == 201:
                authors.append(response.json()['id'])

    data = [
        {'name': 'সোনার তরী 1', 'slug': 'sonar-tori-1', 'sku': '123657', 'regular_price': 340, 'sale_price': 215,
            'manage_stock': True, 'quantity': 12, 'is_used': True, 'condition': 'old like new', 'authors': [authors[0]]},
        {'name': 'স্বপ্নের দেশ 2', 'slug': 'shopner-desh-2', 'sku': '123658', 'regular_price': 250, 'sale_price': 240,
            'manage_stock': True, 'quantity': 13, 'is_used': True, 'condition': 'old readable', 'authors': [authors[1]]},
        {'name': 'গহীন বন 3', 'slug': 'gohin-bon-3', 'sku': '123659', 'regular_price': 600, 'sale_price': 250,
            'manage_stock': True, 'quantity': 13, 'is_used': True, 'condition': 'old like new', 'authors': [authors[0]]},
        {'name': 'মায়াবী এক রাত 4', 'slug': 'mayabi-ek-raat-4', 'sku': '123660', 'regular_price': 300, 'sale_price': 240,
            'manage_stock': True, 'quantity': 15, 'is_used': True, 'condition': 'old good enough', 'authors': [authors[1]]},
        {'name': 'স্বপ্নের দেশ 5', 'slug': 'shopner-desh-5', 'sku': '123661', 'regular_price': 300, 'sale_price': 215,
            'manage_stock': True, 'quantity': 13, 'is_used': True, 'condition': 'old good enough', 'authors': [*authors]},
        {'name': 'স্বপ্নের দেশ 6', 'slug': 'shopner-desh-6', 'sku': '123662', 'regular_price': 490, 'sale_price': 210,
            'manage_stock': True, 'quantity': 12, 'is_used': True, 'condition': 'old good enough', 'authors': [authors[0]]},
        {'name': 'নীল দরিয়া 7', 'slug': 'neel-doriya-7', 'sku': '123663', 'regular_price': 610, 'sale_price': 310,
            'manage_stock': True, 'quantity': 12, 'is_used': True, 'condition': 'old like new', 'authors': [*authors]},
        {'name': 'মায়াবী এক রাত 8', 'slug': 'mayabi-ek-raat-8', 'sku': '123664', 'regular_price': 600, 'sale_price': 600,
            'manage_stock': False, 'quantity': 12, 'is_used': False, 'condition': 'new', 'authors': []},
        {'name': 'মায়াবী এক রাত 9', 'slug': 'mayabi-ek-raat-9', 'sku': '123665', 'regular_price': 680, 'sale_price': 360,
            'manage_stock': False, 'quantity': 15, 'is_used': False, 'condition': 'new', 'authors': [authors[0]]},
        {'name': 'স্বপ্নের দেশ 10', 'slug': 'shopner-desh-10', 'sku': '123666', 'regular_price': 480, 'sale_price': 155,
            'manage_stock': False, 'quantity': 15, 'is_used': False, 'condition': 'new', 'authors': [authors[1]]}
    ]

    counter = 0
    for payload in data:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{settings.BASE_URL}/book", json=payload)
            if response.status_code != 201:
                print(response.json())
            else:
                counter += 1
    print(f"{counter}/{len(data)} books seeded successfully")
