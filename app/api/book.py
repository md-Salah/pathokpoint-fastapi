from fastapi import APIRouter, status, Depends, HTTPException
# from app.models.book import BookCreate, Book
# from app.models.db_setup import get_db
# from sqlmodel import Session
import pandas as pd
import random
import slugify
from datetime import datetime

router = APIRouter()


def slug(name):
    return slugify.slugify(name).replace('aa', 'a').replace('ii', 'i')


def create_author(author):
    return {
        'id': random.randint(1, 1000),
        'name': author,
        'description': None,
        'banglish_name': None,
        'slug': slug(author),

        'birth_date': None,
        'death_date': None,
        'book_published': None,
        'image': None,
        'banner': None,

        'created_at': datetime.now(),
        'updated_at': datetime.now(),
    }


def create_publisher(publisher):
    return {
        'id': random.randint(1, 1000),
        'name': publisher,
        'description': None,
        'banglish_name': None,
        'slug': slug(publisher),

        'country': None,
        'book_published': None,
        'image': None,
        'banner': None,

        'created_at': datetime.now(),
        'updated_at': datetime.now(),
    }


def create_category(category):
    return {
        'id': random.randint(1, 1000),
        'name': category,
        'description': None,
        'banglish_name': None,
        'slug': slug(category),

        'image': None,
        'banner': None,

        'created_at': datetime.now(),
        'updated_at': datetime.now(),
    }


def reorder_columns(df):
    columns = [
        "id",
        "sku",
        "name",
        "banglish_name",
        "short_description",
        "authors",
        "translators",
        "regular_price",
        "sale_price",
        "quantity",
        "in_stock",
        "shipping_required",
        "publisher",
        "edition",
        "notes",
        "cover",
        "description",
        "images",
        "categories",
        "variations",
        "tags",
        "language",
        "condition",
        "isbn",
        "page",
        "slug",
        "draft",
        "featured",
        "must_read",
        "stock_location",
        "shelf",
        "row_col",
        "bar_code",
        "weight",
        "selector",
        "cost",
        "created_at",
        "updated_at"
    ]

    return df[columns]


def get_books():
    df = pd.read_csv('dummy/seba_clean.csv', dtype={'edition': 'str'})
    df.dropna(subset=['regular_price'], inplace=True)
    df.regular_price.astype(int)
    df = df.fillna('')

    df['sale_price'] = 0
    df['edition'] = df['edition'].apply(lambda x: x.split('.')[0])

    # Type casting Regular Price
    df['regular_price'] = df['regular_price'].astype(int)

    # Images
    df['images'] = df['images'].apply(lambda x: x.split(','))

    # Create Author
    df['authors'] = df['author'].apply(
        lambda x: [create_author(name) for name in x.split('/')])
    df.drop(columns=['author'], inplace=True)

    # Create Publisher
    df['publisher'] = df['publisher'].apply(lambda x: create_publisher(x))

    # Create Category
    df['category'] = 'তিন গোয়েন্দা, মাসুদ রানা'
    df['categories'] = df['category'].apply(
        lambda x: [create_category(cat.strip()) for cat in x.split(',')])
    df.drop(columns=['category'], inplace=True)

    # Language
    df['language'] = df['language'].apply(
        lambda x: x.replace('Bn', 'বাংলা').replace('En', 'English'))
    
    # Notes
    df['notes'] = df['notes'].apply(lambda x: x.strip() if x else None)

    # Additional Info
    df['id'] = df.index
    df['translators'] = [[] for _ in range(len(df))]
    df['short_description'] = None
    df['banglish_name'] = None
    df['in_stock'] = df['quantity'].apply(lambda x: True if x > 0 else False)
    df['shipping_required'] = True
    df['description'] = None
    df['variations'] = [[] for _ in range(len(df))]
    df['tags'] = [[] for _ in range(len(df))]
    df['isbn'] = None
    df['page'] = None
    df['slug'] = df['name'].apply(lambda x: slug(x))
    df['draft'] = False
    
    df['featured'] = False
    df['must_read'] = False

    # Stock
    df['stock_location'] = 'mirpur-11'
    df['shelf'] = None
    df['row_col'] = None
    df['bar_code'] = None
    df['weight'] = None
    df['selector'] = None
    df['cost'] = None

    # Timestamp
    df['created_at'] = datetime.now()
    df['updated_at'] = datetime.now()

    df = reorder_columns(df)

    return df.to_dict(orient='records')


books: list[dict] = get_books()


@router.get('/book/{id}')
async def get_book_by_id(id: int):
    return books[id]


@router.get('/books')
async def get_all_books():
    print(len(books))
    return books

# CREATE - Admin, Editor
# @router.post('/book', status_code=status.HTTP_201_CREATED)
# async def create_book(book: BookCreate, db: Session = Depends(get_db)):
#     # check sku exits
#     if db.get(Book, book.sku):
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=f"SKU {book.sku} already exists"
#         )

#     new_book = Book(**book.dict())
#     db.add(new_book)
#     db.commit()
#     db.refresh(new_book)

#     return new_book


# @router.patch('/book')
# async def update_book(book: dict):
#     return books.append(book)

# @router.delete('/book/{id}')
# async def delete_book(id: int):
#     return books.pop(id)
