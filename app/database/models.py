from sqlalchemy import Column, Integer, String, DateTime, ForeignKey,BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import aiomysql
from sqlalchemy import Boolean
# Создание асинхронного движка и сессии
# DATABASE_URL = 'mysql+aiomysql://root:sqlritach@127.0.0.1/base_b'
from config import DATABASE_URL
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

import asyncio

# Определение базового класса для асинхронных операций
class Base(DeclarativeBase):
    pass

# Определение модели User
class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(20), nullable=True)
    reservations: Mapped['Reservation'] = relationship('Reservation', back_populates='user')

# Определение модели Table
class Table(Base):
    __tablename__ = 'tables'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    number: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    seats: Mapped[int] = mapped_column(Integer, nullable=False)

    reservations: Mapped['Reservation'] = relationship('Reservation', back_populates='table')


# Определение модели Reservation
class Reservation(Base):
    __tablename__ = 'reservations'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    table_id: Mapped[int] = mapped_column(Integer, ForeignKey('tables.id'), nullable=False)
    reservation_time: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    reservation_name: Mapped[str] = mapped_column(String(100), nullable=False)
    number_of_guests:Mapped[int]= mapped_column(Integer,nullable=False)
    user: Mapped['User'] = relationship('User', back_populates='reservations')
    table: Mapped['Table'] = relationship('Table', back_populates='reservations')

async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
