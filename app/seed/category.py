import httpx

from app.config.settings import settings

async def seed_category():
    data = [
        {
            'name': 'Fiction',
            'slug': 'fiction',
            'description': 'Fiction is the form of any narrative or informative work that deals, in part or in whole, with information or events that are not real but rather, imaginary and theoretical—that is, invented by the author.',
            'is_islamic': False,
            'is_english_featured': True,
            'is_bangla_featured': False,
            'is_job_featured': False,
            'is_comics': False,
            'is_popular': True,
            'is_big_sale': False            
        },
        {
            'name': 'Non-Fiction',
            'slug': 'non-fiction',
            'description': 'Non-fiction is a form of any narrative, account, or other communicative work whose assertions and descriptions are understood to be fact.',
            'is_islamic': False,
            'is_english_featured': True,
            'is_bangla_featured': False,
            'is_job_featured': False,
            'is_comics': False,
            'is_popular': True,
            'is_big_sale': False
        },
        {
            'name': 'Science Fiction',
            'slug': 'science-fiction',
            'description': 'Science fiction is a genre of speculative fiction that typically deals with imaginative and futuristic concepts such as advanced science and technology, space exploration, time travel, parallel universes, and extraterrestrial life.',
            'is_islamic': False,
            'is_english_featured': True,
            'is_bangla_featured': False,
            'is_job_featured': False,
            'is_comics': False,
            'is_popular': True,
            'is_big_sale': False
        },
        {
            'name': 'Islamic',
            'slug': 'islamic',
            'description': 'Islamic literature is literature written with an Islamic perspective, in any language.',
            'is_islamic': True,
            'is_english_featured': False,
            'is_bangla_featured': True,
            'is_job_featured': False,
            'is_comics': False,
            'is_popular': True,
            'is_big_sale': False
        },
        {
            'name': 'Comics',
            'slug': 'comics',
            'description': 'Comics is a medium used to express ideas with images, often combined with text or other visual information.',
            'is_islamic': False,
            'is_english_featured': False,
            'is_bangla_featured': True,
            'is_job_featured': False,
            'is_comics': True,
            'is_popular': True,
            'is_big_sale': False
        },
        {
            'name': 'Job Preparation',
            'slug': 'job-preparation',
            'description': 'Job Preparation is the process of preparing for a job interview or job search.',
            'is_islamic': False,
            'is_english_featured': False,
            'is_bangla_featured': True,
            'is_job_featured': True,
            'is_comics': False,
            'is_popular': True,
            'is_big_sale': False
        },
        {
            'name': 'HSC',
            'slug': 'hsc',
            'description': 'Higher Secondary Certificate (HSC) is a public examination taken by students in Bangladesh, Pakistan and in the states of Gujarat, Kerala, Tamil Nadu, Andhra Pradesh, Punjab, Maharashtra, West Bengal and Goa in India.',
            'is_islamic': False,
            'is_english_featured': False,
            'is_bangla_featured': True,
            'is_job_featured': False,
            'is_comics': False,
            'is_popular': True,
            'is_big_sale': False
        },
        {
            'name': 'নামাজ শিক্ষা',
            'slug': 'namaz-shikha',
            'description': 'নামাজ শিক্ষা বা নামাজ পড়ার নিয়ম হলো নামাজ পড়ার সঠিক উপায় শিখানোর জন্য একটি বই।',
            'is_islamic': True,
            'is_english_featured': False,
            'is_bangla_featured': True,
            'is_job_featured': False,
            'is_comics': False,
            'is_popular': True,
            'is_big_sale': False
        },
        {
            'name': 'হাদিস শিক্ষা',
            'slug': 'hadis-shikha',
            'description': None,
            'is_islamic': True,
        },
        {
            'name': 'কোরআন শিক্ষা',
            'slug': 'quran-shikha',
            'description': None,
            'is_islamic': True,
        },
        {
            'name': 'BCS Preparation',
            'slug': 'bcs-preparation',
            'description': 'BCS Preparation is the process of preparing for a BCS examination.',
            'is_islamic': False,
            'is_english_featured': False,
            'is_bangla_featured': True,
            'is_job_featured': True,
            'is_comics': False,
            'is_popular': True,
        }
    ]

    counter = 0
    for payload in data:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{settings.BASE_URL}/category", json=payload)
            if response.status_code != 201:
                print(response.json())
            else:
                counter += 1
    print(f"{counter} categories seeded successfully")
