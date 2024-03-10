from pydantic import BaseModel
from enum import Enum

class Country(Enum):
    BD = 'Bangladesh'
    IN = 'India'
    
    
class Desh(BaseModel):
    country: Country
    
d = Desh(country=Country.BD)

print(d.country)