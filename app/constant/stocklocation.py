from enum import Enum


class StockLocation(str, Enum):
    mirpur_11 = 'mirpur-11'
    backorder = 'backorder'
    on_demand = 'on-demand'
    
