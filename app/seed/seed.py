import asyncio
import httpx

# Function to create a book through the /book endpoint
async def create_book(payload):
    async with httpx.AsyncClient() as client:
        response = await client.post("http://localhost:8000/book", json=payload)
        return response.json()
    
async def create_author(payload):
    async with httpx.AsyncClient() as client:
        response = await client.post("http://localhost:8000/author", json=payload)
        return response.json()

# Dummy book data
dummy_books = [
    {'name': 'Book 1', 'regular_price': 100, 'slug': 'book-1'},
    {'name': 'Book 2', 'regular_price': 200, 'slug': 'book-2', 'tags': ['fiction', 'mystery']},
    {'name': 'Book 3', 'regular_price': 300, 'slug': 'book-3', 'tags': ['non-fiction', 'biography']},
    {'name': 'Book 4', 'regular_price': 400, 'slug': 'book-4', 'tags': ['non-fiction', 'history']},
    {'name': 'Book 5', 'regular_price': 500, 'slug': 'book-5', 'tags': ['fiction', 'science-fiction']},
    {'name': 'Book 6', 'regular_price': 600, 'slug': 'book-6', 'tags': ['non-fiction', 'self-help']},
    {'name': 'Book 7', 'regular_price': 700, 'slug': 'book-7', 'tags': ['fiction', 'romance']},
    {'name': 'Book 8', 'regular_price': 800, 'slug': 'book-8', 'tags': ['fiction', 'thriller']},
    {'name': 'Book 9', 'regular_price': 900, 'slug': 'book-9', 'tags': ['non-fiction', 'science']},
    {'name': 'Book 10', 'regular_price': 1000, 'slug': 'book-10', 'tags': ['fiction', 'horror']},
]

dummy_authors = [
    {'name': 'Author 1', 'slug': 'author-1'},
    {'name': 'Author 2', 'slug': 'author-2'},
    {'name': 'Author 3', 'slug': 'author-3'},
    {'name': 'Author 4', 'slug': 'author-4'},
    {'name': 'Author 5', 'slug': 'author-5'},
    {'name': 'Author 6', 'slug': 'author-6'},
    {'name': 'Author 7', 'slug': 'author-7'},
    {'name': 'Author 8', 'slug': 'author-8'},
    {'name': 'Author 9', 'slug': 'author-9'},
    {'name': 'Author 10', 'slug': 'author-10'},
]

# Seed function to create 10 dummy books
async def seed():
    for book_data in dummy_books:
        await create_book(book_data)
    for author in dummy_authors:
        await create_author(author)

# Run the seed function
asyncio.run(seed())
