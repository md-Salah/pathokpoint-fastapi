from fastapi_filter.contrib.sqlalchemy import Filter

from app.models.courier import Courier
from app.constant import Country, City


class CourierFilter(Filter):
    allow_cash_on_delivery: bool | None = None
    # country: Country | None = None
    city: City | None = None

    class Constants(Filter.Constants):
        model = Courier
