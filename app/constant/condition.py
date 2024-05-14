from enum import Enum

class Condition(str, Enum):
    new = 'new'
    old_like_new = 'old-like-new'
    old_good_enough = 'old-good-enough'
    old_readable = 'old-readable'
    
    