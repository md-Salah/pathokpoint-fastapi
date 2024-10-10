import uuid
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.constant.gender import Gender
from app.constant.role import Role
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models import Address, Author, Image, Order, Review


class User(TimestampMixin):
    __tablename__ = 'users'

    id: Mapped[uuid.UUID] = mapped_column(UUID(
        as_uuid=True), primary_key=True, default=uuid.uuid4)

    first_name: Mapped[str | None] = mapped_column(String(20))
    last_name: Mapped[str | None] = mapped_column(String(20))
    username: Mapped[str] = mapped_column(String(25), unique=True)
    email: Mapped[str] = mapped_column(String, index=True, unique=True)
    password: Mapped[str]
    phone_number: Mapped[str | None]
    date_of_birth: Mapped[date | None]
    gender: Mapped[Gender | None]
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.customer)

    image_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey('images.id'))
    image: Mapped['Image'] = relationship(foreign_keys=[
                                          image_id], cascade='all, delete-orphan', lazy='selectin', single_parent=True)

    orders: Mapped[list["Order"]] = relationship(back_populates='customer')
    addresses: Mapped[list["Address"]] = relationship(
        back_populates='user', cascade='all, delete-orphan')
    reviews: Mapped[list["Review"]] = relationship(back_populates='user')

    following_authors: Mapped[list["Author"]] = relationship(
        secondary='author_follower_link', back_populates='followers')

    def __repr__(self):
        return f'<User (username={self.username}, role={self.role})>'
