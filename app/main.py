from fastapi import FastAPI
from contextlib import asynccontextmanager
# from app.api.user import router as user_route
from app.api.book import router as book_route
# from app.models.db_setup import create_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    # create_tables()
    yield
    # shutdown
    

app = FastAPI(
    title = 'PATHOK POINT',
    description = 'Ecommerce backend for the bookshop PATHOK POINT',
    version = '1.0.0',
    contact={
        'name': 'Md Salah',
        'email': 'mdsalah.connect@gmail.com',
    },
    license_info={
        'name': 'MIT'
    },
    lifespan=lifespan
)


@app.get('/')
def say_hello():
    return {'msg': 'Hello! Welcome to PATHOK POINT!'}


# app.include_router(user_route, tags=['USER'])
app.include_router(book_route, tags=['BOOK'])

