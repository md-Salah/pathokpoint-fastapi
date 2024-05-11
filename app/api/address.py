from fastapi import APIRouter, status, Query, Response
from uuid import UUID

from app.config.database import Session
import app.controller.address as address_service
import app.pydantic_schema.address as address_schema
from app.controller.auth import AccessToken, Role
from app.controller.exception import ForbiddenException

router = APIRouter(prefix='/address')


@router.get('/id/{id}', response_model=address_schema.AddressOut)
async def get_address_by_id(id: UUID, token: AccessToken, db: Session):
    return await address_service.get_address_by_id(id, token['id'], token['role'], db)


@router.get('/user/{user_id}/all', response_model=list[address_schema.AddressOut])
async def get_all_addresses(*, page: int = Query(1, ge=1),
                            per_page: int = Query(10, ge=1, le=100),
                            user_id: UUID,
                            token: AccessToken,
                            db: Session,  response: Response):

    if token['id'] == user_id or token['role'] == Role.admin.value:
        addresss = await address_service.get_all_addresss(user_id, page, per_page, db)
        total_addresss = await address_service.count_address(user_id, db)

        response.headers['X-Total-Count'] = str(total_addresss)
        response.headers['X-Total-Pages'] = str(-(-total_addresss // per_page))
        response.headers['X-Current-Page'] = str(page)
        response.headers['X-Per-Page'] = str(per_page)

        return addresss

    raise ForbiddenException('You are not allowed to access this address')


@router.post('', response_model=address_schema.AddressOut, status_code=status.HTTP_201_CREATED)
async def create_my_address(payload: address_schema.CreateAddress, token: AccessToken, db: Session):
    return await address_service.create_address(token['id'], payload.model_dump(), db)


@router.patch('/{id}', response_model=address_schema.AddressOut)
async def update_my_address(id: UUID, payload: address_schema.UpdateAddress, token: AccessToken, db: Session):
    return await address_service.update_address(id, token['id'], payload.model_dump(exclude_unset=True), db)


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_address(id: UUID, token: AccessToken, db: Session):
    await address_service.delete_address(id, token['id'], token['role'], db)
