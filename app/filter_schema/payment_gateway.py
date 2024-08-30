from fastapi_filter.contrib.sqlalchemy import Filter

from app.models.payment_gateway import PaymentGateway


class PaymentGatewayFilter(Filter):
    is_disabled: bool | None = None
    is_admin_only: bool | None = None

    class Constants(Filter.Constants):
        model = PaymentGateway
