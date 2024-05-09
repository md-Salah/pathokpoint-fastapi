from fastapi import Query
from pydantic import Field, UUID4
from fastapi_filter.contrib.sqlalchemy import Filter

from app.models.transaction import Transaction

class TransactionFilter(Filter):
    q: str | None = Field(Query(None, description='Search by transaction_id, reference, or account number'))
    transaction_id: str | None = None
    reference: str | None = None
    account_number: str | None = None
    is_manual: bool | None = None
    is_refund: bool | None = None
    amount__lte: int | None = None
    amount__gte: int | None = None
    
    gateway_id: UUID4 | None = None
    refunded_by_id: UUID4 | None = None
    user_id: UUID4 | None = None
    order_id: UUID4 | None = None

    class Constants(Filter.Constants):
        model = Transaction
        search_field_name = 'q'
        search_model_fields = ['transaction_id', 'reference', 'account_number']
        
        