from enum import Enum

class ImageFolder(str, Enum):
    book = 'book'
    new_book = 'new_book'
    author = 'author'
    category = 'category'
    publisher = 'publisher'
    profile_picture = 'profile_picture'
    review = 'review'
    dummy = 'dummy'
    payment_gateway = 'payment_gateway'
    
