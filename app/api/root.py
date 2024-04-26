from pydantic import BaseModel
from fastapi import APIRouter
from fastapi import Request

router = APIRouter()

class SayHello(BaseModel):
    msg: str

@router.get('/', response_model=SayHello)
def say_hello():
    return {'msg': 'Hello! Welcome to PATHOK POINT!'}


# @router.post('/set-to-redis')
# async def set_to_redis(msg: str, request: Request):
#     await request.app.state.redis.set('msg', msg)

# @router.get('/get-from-redis')
# async def get_from_redis(request: Request):
#     return await request.app.state.redis.get('msg')

