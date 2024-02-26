from pydantic import BaseModel
from fastapi import APIRouter

router = APIRouter()

class SayHello(BaseModel):
    msg: str

@router.get('/', response_model=SayHello)
def say_hello():
    return {'msg': 'Hello! Welcome to PATHOK POINT!'}