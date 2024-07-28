import datetime

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import DeclarativeBase



class Base(DeclarativeBase):
    pass
class Contacts(Base):
    __tablename__ = "contacts"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    surname: Mapped[str] = mapped_column(String(50))
    phone: Mapped[str] = mapped_column(String(15))
    email: Mapped[str] = mapped_column(String(50))
    birthday: Mapped[datetime] = mapped_column(DateTime)
    extra: Mapped[str] = mapped_column(String(255))
