from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.api.root import router as root_route
from app.api.auth import router as auth_route
from app.api.book import router as book_route
# from app.api.order import router as order_route

from app.config.database import create_tables, drop_tables
from app.config.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    # await drop_tables()
    await create_tables()
    yield
    # shutdown

app = FastAPI(
    title = settings.PROJECT_NAME,
    description = settings.PROJECT_DESCRIPTION,
    version = settings.PROJECT_VERSION,
    contact={
        'name': 'Md Salah',
        'email': 'mdsalah.connect@gmail.com',
    },
    license_info={
        'name': 'MIT'
    },
    lifespan=lifespan
)


app.include_router(root_route, tags=['Root'])
app.include_router(auth_route, tags=['Auth'])
app.include_router(book_route, tags=['Book'])
# app.include_router(order_route, tags=['Order'])


