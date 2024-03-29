from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.api.root import router as root_route
from app.api.auth import router as auth_route
from app.api.user import router as user_route
from app.api.book import router as book_route
from app.api.image import router as image_route
from app.api.tag import router as tag_route
from app.api.author import router as author_route
from app.api.publisher import router as publisher_route
from app.api.category import router as category_route
from app.api.order import router as order_route
from app.api.courier import router as courier_route
from app.api.address import router as address_route
from app.api.coupon import router as coupon_route
from app.api.payment_gateway import router as payment_gateway_route
from app.api.transaction import router as transaction_route


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
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION,
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
app.include_router(user_route, tags=['User'])
app.include_router(book_route, tags=['Book'])
app.include_router(image_route, tags=['Image'])
app.include_router(tag_route, tags=['Tag'])
app.include_router(author_route, tags=['Author'])
app.include_router(publisher_route, tags=['Publisher'])
app.include_router(category_route, tags=['Category'])
app.include_router(order_route, tags=['Order'])
app.include_router(courier_route, tags=['Courier'])
app.include_router(address_route, tags=['Address'])
app.include_router(coupon_route, tags=['Coupon'])
app.include_router(payment_gateway_route, tags=['PaymentGateway'])
app.include_router(transaction_route, tags=['Transaction'])
