import httpx

from app.config.settings import settings
from app.constant import Country

async def seed_author():
    data = [
        {
            "name": "হুমায়ূন আহমেদ",
            "slug": "humayun-ahmed",
            "description": "বাংলাদেশের প্রখ্যাত লেখক",
            "birth_date": "1948-11-13",
            "death_date": "2012-07-19",
            "book_published": 200,
            "city": "dhaka",
            "country": Country.BD.value,
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
            "country": Country.IN.value,
            "is_popular": True,
        },
        {
            "name": "Sarat Chandra Chattopadhyay",
            "slug": "sarat-chandra-chattopadhyay",
            "description": "Legendary Indian novelist and short story writer",
            "birth_date": "1876-09-15",
            "death_date": "1938-01-16",
            "book_published": 20,
            "city": "Debanandapur",
            "country": Country.IN.value,
            "is_popular": True,
        },
        {
            "name": "Taslima Nasrin",
            "slug": "taslima-nasrin",
            "description": "Bangladeshi-Swedish author and former physician",
            "birth_date": "1962-08-25",
            "death_date": None,
            "book_published": 35,
            "city": "Mymensingh",
            "country": Country.BD.value,
            "is_popular": False,
        },
        {
            "name": "J.K. Rowling",
            "slug": "jk-rowling",
            "description": "British author best known for the Harry Potter series",
            "birth_date": "1965-07-31",
            "death_date": None,
            "book_published": 15,
            "city": "Yate",
            "country": Country.GB.value,
            "is_popular": True,
        },
        {
            "name": "George R.R. Martin",
            "slug": "george-rr-martin",
            "description": "American novelist and short story writer in fantasy",
            "birth_date": "1948-09-20",
            "death_date": None,
            "book_published": 25,
            "city": "Bayonne",
            "country": Country.US.value,
            "is_popular": True,
        },
        {
            "name": "Kazi Nazrul Islam",
            "slug": "kazi-nazrul-islam",
            "description": "National poet of Bangladesh",
            "birth_date": "1899-05-25",
            "death_date": "1976-08-29",
            "book_published": 75,
            "city": "Churulia",
            "country": Country.BD.value,
            "is_popular": True,
        },
        {
            "name": "Jane Austen",
            "slug": "jane-austen",
            "description": "English novelist known for her romantic fiction",
            "birth_date": "1775-12-16",
            "death_date": "1817-07-18",
            "book_published": 7,
            "city": "Steventon",
            "country": Country.GB.value,
            "is_popular": True,
        },
        {
            "name": "Leo Tolstoy",
            "slug": "leo-tolstoy",
            "description": "Russian writer who is regarded as one of the greatest authors",
            "birth_date": "1828-09-09",
            "death_date": "1910-11-20",
            "book_published": 48,
            "city": "Yasnaya Polyana",
            "country": Country.US.value,
            "is_popular": True,
        },
    ]

    counter = 0
    for payload in data:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{settings.BASE_URL}/author", json=payload)
            if response.status_code != 201:
                print(response.json())
            else:
                counter += 1
    print(f"{counter} authors seeded successfully")
