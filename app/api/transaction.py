from fastapi import APIRouter, status, Query, Response
from uuid import UUID
from fastapi_filter import FilterDepends

from app.filter_schema.transaction import TransactionFilter
from app.config.database import Session
import app.controller.transaction as service
import app.pydantic_schema.transaction as schema
from app.controller.auth import AdminAccessToken, AccessToken

router = APIRouter(prefix='/transaction')


@router.get('/id/{id}', response_model=schema.TransactionOut)
async def get_transaction_by_id(id: UUID, token: AccessToken, db: Session):
    return await service.get_transaction_by_id(id, token['id'], token['role'], db)


@router.get('/all', response_model=list[schema.TransactionOut])
async def get_all_transactions(*, page: int = Query(1, ge=1),
                               per_page: int = Query(10, ge=1, le=100),
                               filter: TransactionFilter = FilterDepends(
                                   TransactionFilter),
                               _: AdminAccessToken,
                               db: Session,  response: Response):
    transactions = await service.get_all_transactions(filter, page, per_page, db)
    total_transactions = await service.count_transaction(filter, db)

    response.headers['X-Total-Count'] = str(total_transactions)
    response.headers['X-Total-Pages'] = str(-(-total_transactions // per_page))
    response.headers['X-Current-Page'] = str(page)
    response.headers['X-Per-Page'] = str(per_page)

    return transactions


@router.post('/refund', response_model=schema.TransactionOut, status_code=status.HTTP_201_CREATED)
async def create_refund(payload: schema.CreateRefundTransaction, token: AdminAccessToken, db: Session):
    return await service.refund({
        **payload.model_dump(),
        'refunded_by_id': token['id']
    }, db)


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(id: UUID, _: AdminAccessToken, db: Session):
    await service.delete_transaction(id, db)
