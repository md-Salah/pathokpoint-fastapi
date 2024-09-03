from fastapi import APIRouter

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
from app.api.review import router as review_route
from app.api.courier import router as courier_route
from app.api.address import router as address_route
from app.api.coupon import router as coupon_route
from app.api.payment_gateway import router as payment_gateway_route
from app.api.transaction import router as transaction_route
from app.api.payment import router as payment_route
from app.api.cart import router as cart_route
from app.api.checkout import router as checkout_route
from app.api.email import router as email_route

router = APIRouter()

router.include_router(root_route, tags=['Root'])
router.include_router(auth_route, tags=['Auth'])
router.include_router(user_route, tags=['User'])
router.include_router(book_route, tags=['Book'])
router.include_router(author_route, tags=['Author'])
router.include_router(publisher_route, tags=['Publisher'])
router.include_router(category_route, tags=['Category'])
router.include_router(image_route, tags=['Image'])
router.include_router(tag_route, tags=['Tag'])
router.include_router(coupon_route, tags=['Coupon'])
router.include_router(cart_route, tags=['Cart'])
router.include_router(checkout_route, tags=['Checkout'])
router.include_router(order_route, tags=['Order'])
router.include_router(review_route, tags=['Review'])
router.include_router(courier_route, tags=['Courier'])
router.include_router(address_route, tags=['Address'])
router.include_router(payment_gateway_route, tags=['PaymentGateway'])
router.include_router(payment_route, tags=['Payment'])
router.include_router(transaction_route, tags=['Transaction'])
router.include_router(email_route, tags=['Email'])
