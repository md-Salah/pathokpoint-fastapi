from pydantic import ConfigDict, NonNegativeFloat, NonNegativeInt

from app.pydantic_schema.base import BaseModel

example_order_analysis = {
    "total_order": 100,
    "order_value": 1000.0,
    "order_value_new_book": 500.0,
    "order_value_old_book": 500.0,
    "cog_new_book": 250.0,
    "cog_old_book": 250.0,
    "profit": 250.0,
    "shipping_charge": 50.0,
    "weight_charge": 50.0
}


class OrderAnalysis(BaseModel):
    total_order: int
    order_value: NonNegativeFloat
    order_value_new_book: NonNegativeFloat
    order_value_old_book: NonNegativeFloat
    cog_new_book: NonNegativeFloat
    cog_old_book: NonNegativeFloat
    profit: NonNegativeFloat
    shipping_charge: NonNegativeFloat
    weight_charge: NonNegativeFloat

    model_config = ConfigDict(
        json_schema_extra={"example": example_order_analysis})


class ProductGroup(BaseModel):
    tag: str
    unique_product: NonNegativeInt
    in_stock: NonNegativeInt
    out_of_stock: NonNegativeInt
    quantity: NonNegativeInt
    cost: NonNegativeInt
    regular_price: NonNegativeInt
    sale_price: NonNegativeInt
