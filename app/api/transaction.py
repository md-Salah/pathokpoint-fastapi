from fastapi import APIRouter, Depends, status, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.config.database import get_db
import app.controller.transaction as transaction_service
import app.pydantic_schema.transaction as transaction_schema

router = APIRouter()


@router.get('/transaction/id/{id}', response_model=transaction_schema.TransactionOut)
async def get_transaction_by_id(id: UUID, db: AsyncSession = Depends(get_db)):
    transaction = await transaction_service.get_transaction_by_id(id, db)
    return transaction


@router.get('/transactions', response_model=list[transaction_schema.TransactionOut])
async def get_all_transactions(*, page: int = Query(1, ge=1),
                               per_page: int = Query(10, ge=1, le=100),
                               db: AsyncSession = Depends(get_db),  response: Response):
    transactions = await transaction_service.get_all_transactions(page, per_page, db)
    total_transactions = await transaction_service.count_transaction(db)

    response.headers['X-Total-Count'] = str(total_transactions)
    response.headers['X-Total-Pages'] = str(-(-total_transactions // per_page))
    response.headers['X-Current-Page'] = str(page)
    response.headers['X-Per-Page'] = str(per_page)

    return transactions


@router.post('/transaction', response_model=transaction_schema.TransactionOut, status_code=status.HTTP_201_CREATED)
async def create_transaction(payload: transaction_schema.CreateTransaction, db: AsyncSession = Depends(get_db)):
    transaction = await transaction_service.create_transaction(payload.model_dump(), db)
    return transaction


@router.post('/refund', response_model=transaction_schema.TransactionOut, status_code=status.HTTP_201_CREATED)
async def create_refund(payload: transaction_schema.CreateRefundTransaction, db: AsyncSession = Depends(get_db)):
    transaction = await transaction_service.create_transaction(payload.model_dump(), db)
    return transaction


@router.delete('/transaction/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(id: UUID, db: AsyncSession = Depends(get_db)):
    await transaction_service.delete_transaction(id, db)
