from fastapi import APIRouter, Depends, status, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.config.database import get_db
import app.controller.address as address_service
import app.pydantic_schema.address as address_schema

router = APIRouter()


# Permission: Customer
@router.get('/address/id/{id}', response_model=address_schema.AddressOut)
async def get_address_by_id(id: UUID, db: AsyncSession = Depends(get_db)):
    address = await address_service.get_address_by_id(id, db)
    return address_schema.AddressOut.model_validate(address)


# Permission: Customer
@router.get('/addresss/{user_id}', response_model=list[address_schema.AddressOut])
async def get_all_addresss(*, user_id:UUID, page: int = Query(1, ge=1),
                           per_page: int = Query(10, ge=1, le=100),
                           db: AsyncSession = Depends(get_db),  response: Response):
    addresss = await address_service.get_all_addresss(user_id, page, per_page, db)
    total_addresss = await address_service.count_address(db)

    response.headers['X-Total-Count'] = str(total_addresss)
    response.headers['X-Total-Pages'] = str(-(-total_addresss // per_page))
    response.headers['X-Current-Page'] = str(page)
    response.headers['X-Per-Page'] = str(per_page)

    return [address_schema.AddressOut.model_validate(address) for address in addresss]


# Permission: Admin
@router.post('/address/{user_id}', response_model=address_schema.AddressOut, status_code=status.HTTP_201_CREATED)
async def create_address(user_id: UUID, payload: address_schema.CreateAddress, db: AsyncSession = Depends(get_db)):
    address = await address_service.create_address(user_id, payload.model_dump(), db)
    return address_schema.AddressOut.model_validate(address)


# Permission: Admin
@router.patch('/address/{id}', response_model=address_schema.AddressOut)
async def update_address(id: UUID, payload: address_schema.UpdateAddress, db: AsyncSession = Depends(get_db)):
    address = await address_service.update_address(id, payload.model_dump(exclude_unset=True), db)
    return address_schema.AddressOut.model_validate(address)


# Permission: Admin
@router.delete('/address/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_address(id: UUID, db: AsyncSession = Depends(get_db)):
    await address_service.delete_address(id, db)
