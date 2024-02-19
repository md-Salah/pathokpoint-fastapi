from fastapi import FastAPI
from pydantic import BaseModel
from contextlib import asynccontextmanager

from app.api.auth import router as auth_route
from app.api.book import router as book_route
# from app.api.order import router as order_route
from app.config.database import create_tables
from app.config.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    create_tables()
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


class SayHello(BaseModel):
    msg: str

@app.get('/', response_model=SayHello, tags=['Root'])
def say_hello():
    return {'msg': 'Hello! Welcome to PATHOK POINT!'}


app.include_router(auth_route, tags=['Auth'])
app.include_router(book_route, tags=['Book'])
# app.include_router(order_route, tags=['Order'])
# app.include_router(test_route, tags=['Test'])

