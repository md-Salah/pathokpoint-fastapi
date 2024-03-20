import asyncio
import httpx

async def create_data(payload):
    async with httpx.AsyncClient() as client:
        response = await client.post("http://localhost:8000/courier", json=payload)
        print('Done')
        return response.json()

async def seed():
    data = [
        {
            'method_name': 'Inside Dhaka Home Delivery',
            'company_name': 'Delivery Tiger',
            'base_charge': 60,
            'weight_charge_per_kg': 20,
            'include_city': ['dhaka'],
        },
        {
            'method_name': 'Outside Dhaka Home Delivery',
            'company_name': 'Delivery Tiger',
            'base_charge': 100,
            'weight_charge_per_kg': 20,
            'exclude_city': ['dhaka'],
        },
        {
            'method_name': 'Outside Dhaka Sundarban Courier',
            'company_name': 'Sundarban Courier',
            'base_charge': 60,
            'weight_charge_per_kg': 20,
            'allow_cash_on_delivery': False,
            'exclude_city': ['dhaka'],
        }
    ]
    for payload in data:
        await create_data(payload)

# Run the seed function
asyncio.run(seed())
