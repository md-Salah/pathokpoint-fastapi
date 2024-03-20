import httpx

from app.config.settings import settings


async def seed_user():
    data = [
        {
            "first_name": "John",
            "last_name": "Doe",
            "username": "johndoe",
            "email": "jhondoe@gmail.com",
            "password": "password123",
            "phone_number": "+8801786357098",
            "role": "admin",
            "is_verified": True
        },
        {
            "first_name": "Jane",
            "last_name": "Smith",
            "username": "janesmith",
            "email": "janesmith@gmail.com",
            "password": "securePassword1",
            "phone_number": "+8801687316402",
            "role": "customer",
            "is_verified": False
        },
        {
            "first_name": "Emily",
            "last_name": "Johnson",
            "username": "emilyj",
            "email": "emilyjohnson@gmail.com",
            "password": "myPassword456",
            "phone_number": "+8801623456789",
            "role": "customer",
            "is_verified": True
        },
        {
            "first_name": "Michael",
            "last_name": "Brown",
            "username": "michaelb",
            "email": "michaelbrown@gmail.com",
            "password": "password789",
            "phone_number": "+8801723456798",
            "role": "customer",
            "is_verified": False
        },
        {
            "first_name": "Sarah",
            "last_name": "Davis",
            "username": "sarahd",
            "email": "sarahdavis@gmail.com",
            "password": "sarahsPassword123",
            "phone_number": "+8801776543210",
            "role": "customer",
            "is_verified": True
        },
        {
            "first_name": "William",
            "last_name": "Wilson",
            "username": "williamw",
            "email": "williamwilson@gmail.com",
            "password": "williamsPass456",
            "phone_number": "+8801887654321",
            "role": "customer",
            "is_verified": False
        }

    ]
    
    counter = 0
    for payload in data:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{settings.BASE_URL}/user", json=payload)
            if response.status_code != 201:
                print(response.json())
            else:
                counter += 1
    print(f"{counter} users seeded successfully")
    