import uuid

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.constant.city import City
from app.constant.country import Country
from app.models.mixins import TimestampMixin
from app.models.user import User


class Address(TimestampMixin):
    __tablename__ = 'addresses'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String)
    email: Mapped[str | None] = mapped_column(String)
    phone_number: Mapped[str] = mapped_column(String)
    alternative_phone_number: Mapped[str | None] = mapped_column(String)
    address: Mapped[str] = mapped_column(String)
    thana: Mapped[str] = mapped_column(String)
    city: Mapped[City] = mapped_column(Enum(City))
    country: Mapped[Country] = mapped_column(Enum(Country), default=Country.BD)

    user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey('users.id'))
    user: Mapped['User'] = relationship(back_populates='addresses')

    def __repr__(self):
        return f'<Address (address={self.address}, user_id={self.user_id})>'
