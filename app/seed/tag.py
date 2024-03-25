import httpx

from app.config.settings import settings

async def seed_tag():
    data = [
        {
            'name': 'General bangla',
            'slug': 'general-bangla',
            'private': True,
        },
        {
            'name': 'General english',
            'slug': 'general-english',
            'private': True,
        },
        {
            'name': 'Indian bangla',
            'slug': 'indian-bangla',
            'private': True,
        },
        {
            'name': 'Islamic old',
            'slug': 'islamic-old',
            'private': True,
        },
        {
            'name': 'Islamic new',
            'slug': 'islamic-new',
            'private': True,
        },
        {
            'name': 'English classic',
            'slug': 'english-classic',
            'private': True,
        }
    ]

    counter = 0
    for payload in data:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{settings.BASE_URL}/tag", json=payload)
            if response.status_code != 201:
                print(response.json())
            else:
                counter += 1
    print(f"{counter} tags seeded successfully")
