# class SortBy(BaseModel):
#     price_low_to_high: bool = False
#     price_high_to_low: bool = False
#     recently_added: bool = False
#     best_selling: bool = False

# class FilterBy(BaseModel):
#     max_sale_price: float | None = Field(None, ge=0, le=_10_lakh)
#     min_sale_price: float | None = Field(None, ge=0, le=_10_lakh)
#     in_stock: bool | None = None
#     pre_order: bool | None = None
#     cover: Cover | None = None
#     language: Language | None = None
#     is_used: bool | None = None
#     condition: Condition | None = None
#     country: Country | None = None
#     is_featured: bool | None = None
#     is_must_read: bool | None = None
#     is_vintage: bool | None = None
#     is_islamic: bool | None = None
#     is_translated: bool | None = None
#     is_recommended: bool | None = None
#     is_big_sale: bool | None = None
#     is_popular: bool | None = None
#     authors: List[UUID4] = []
#     translators: List[UUID4] = []
#     categories: List[UUID4] = []
#     publishers: List[UUID4] = []
#     tags: List[UUID4] = []