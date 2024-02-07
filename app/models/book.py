import enum
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

from .mixins import TimestampMixin

class Cover(enum.Enum):
    paperback = 'paperback'
    hardcover = 'hardcover'

class Language(enum.Enum):
    english = 'english'
    bangla = 'bangla'

class Condition(enum.Enum):
    new = 'new'
    old = 'old'
    old_like_new = 'old like new'


# class Genre(Base):
#     __tablename__ = 'genres'

#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String(50), unique=True, nullable=False)
#     banglish_name = Column(String(50))
#     description = Column(String)
#     image_url = Column(String)
    
#     books = relationship('Book', back_populates='genre')



# Models
class BookBase(SQLModel):
    sku: str = Field(unique=True)
    name: str
    regular_price: int
    condition: Condition
    slug: str = Field(unique=True, max_length=100)
    image_url: str | None = None
    qty: int = Field(default=1, ge=0, le=10000)
    banglish_name: str | None = None
    sale_price: int | None = None
    manage_stock: bool = True
    publisher: str | None = None
    edition: str | None = None
    cost: int | None = None
    notes: str | None = None
    cover: Cover | None = None
    description: str | None = None
    language: Language | None = None
    ISBN: int | None = None
    no_of_pages: int | None = None

# SQLModel
# Table name: book
class Book(BookBase, table=True):
    id: int | None = Field(primary_key=True)
    author_id: int = Field(foreign_key="author.id")
    translator_id: int = Field(foreign_key="author.id")
    genre_id: int = Field(foreign_key="genre.id")

    author: List["Author"] = Relationship(back_populates="books")
    translator: List["Author"] = Relationship(back_populates="translated")
    # images: List["BookImage"] = Relationship(back_populates="books")
    genre: List["Genre"] = Relationship(back_populates="books")


class AuthorBase(SQLModel):
    name: str
    banglish_name: str | None = None
    bio: str | None = None
    image_url: str | None = None
    birth_date: str | None = None
    death_date: str | None = None
    slug: str | None = None

class Author(AuthorBase, TimestampMixin, table=True):
    id: Optional[int] = Field(primary_key=True)
    books: List[Book] = Relationship(back_populates="author")
    translated: List[Book] = Relationship(back_populates="translator")

class GenreBase(SQLModel):
    name: str
    banglish_name: str | None = None
    description: str | None = None
    image_url: str | None = None
    slug: str | None = None

class Genre(GenreBase, TimestampMixin, table=True):
    id: int = Field(default=None, primary_key=True)
    books: List[Book] = Relationship(back_populates="genre")

class BookImageBase(SQLModel):
    url: str

class BookImage(BookImageBase, table=True):
    id: int = Field(default=None, primary_key=True)
    book_id: int = Field(default=None, foreign_key="book.id")
    
    
# Pydantic models
class BookCreate(BookBase):
    pass