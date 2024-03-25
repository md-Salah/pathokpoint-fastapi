import httpx

from app.config.settings import settings
from app.constant import Country

async def seed_publisher():
    data = [
        {
            'name': 'Penguin Random House',
            'slug': 'penguin-random-house',
            'description': 'Penguin Random House is an American multinational conglomerate publishing company formed in 2013 from the merger of Penguin Group and Random House.',
            'is_islamic': False,
            'is_english': True,
            'is_popular': True,
            'is_big_sale': False,
            'country': Country.US.value,
            'book_published': 1000
        },
        {
            'name': 'অনন্যা প্রকাশনী',
            'slug': 'ananya-prokashoni',
            'description': 'বাংলাদেশী প্রখ্যাত প্রকাশনী',
            'is_islamic': False,
            'is_english': False,
            'is_popular': True,
            'is_big_sale': False,
            'country': Country.BD.value,
            'book_published': 500
        },
        {
            'name': 'HarperCollins',
            'slug': 'harper-collins',
            'description': 'HarperCollins Publishers LLC is one of the world\'s largest publishing companies and is one of the Big Five English-language publishing companies.',
            'is_islamic': False,
            'is_english': True,
            'is_popular': True,
            'is_big_sale': True,
            'country': Country.US.value,
            'book_published': 800
        },
        {
            'name': 'আনন্দ পাবলিশার্স',
            'slug': 'ananda-publishers',
            'description': None,
            'is_islamic': False,
            'is_english': False,
            'is_popular': True,
            'is_big_sale': False,
            'country': Country.IN.value,
            'book_published': 300
        },
        {
            'name': 'প্রথমা প্রকাশন',
            'slug': 'prothoma-prokashon',
            'description': None,
            'is_islamic': False,
            'is_english': False,
            'is_popular': False,
            'is_big_sale': False,
            'country': Country.BD.value,
            'book_published': 200
        }, 
        {
            'name': 'Rupa Publications',
            'slug': 'rupa-publications',
            'description': 'Rupa Publications India is a publishing company based in Kolkata.',
            'is_islamic': False,
            'is_english': True,
            'is_popular': True,
            'is_big_sale': False,
            'country': Country.IN.value,
            'book_published': 250
        },
        {
            'name': 'উপালকথা',
            'slug': 'upalokkho',
            'description': None,
            'is_islamic': False,
            'is_english': False,
            'is_popular': False,
            'is_big_sale': False,
            'country': Country.BD.value,
            'book_published': 150
        }, 
        {
            'name': 'প্রথম আলো',
            'slug': 'prothom-alo',
            'description': None,
            'is_islamic': False,
            'is_english': False,
            'is_popular': False,
            'is_big_sale': True,
            'country': Country.BD.value,
            'book_published': 100
        },
        {
            'name': 'দারুল ইসলাম',
            'slug': 'darul-islam',
            'description': 'বাংলাদেশের প্রখ্যাত ইসলামিক প্রকাশনী',
            'is_islamic': True,
            'is_english': False,
            'is_popular': True,
            'is_big_sale': False,
            'country': Country.BD.value,
            'book_published': 200
        },
        {
            'name': 'আল হিজরা',
            'slug': 'al-hijra',
            'description': 'বাংলাদেশের প্রখ্যাত ইসলামিক প্রকাশনী',
            'is_islamic': True,
            'is_english': False,
            'is_popular': True,
            'is_big_sale': False,
            'country': Country.BD.value,
            'book_published': 150
        }
    ]

    counter = 0
    for payload in data:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{settings.BASE_URL}/publisher", json=payload)
            if response.status_code != 201:
                print(response.json())
            else:
                counter += 1
    print(f"{counter} publishers seeded successfully")
