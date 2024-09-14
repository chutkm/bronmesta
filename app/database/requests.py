from sqlalchemy.orm import joinedload
from .models import async_session, User, Reservation, Table
from sqlalchemy import select, update,delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from datetime import datetime
import logging

async def find_user(tg_id):
    async with async_session() as session:
        return await session.scalar(select(User).where(User.tg_id == tg_id))


async def set_user(tg_id, username=None):
    async with async_session() as session:
        try:
            # Проверяем, существует ли уже пользователь с таким tg_id
            user = await session.scalar(select(User).where(User.tg_id == tg_id))
            if not user:
                # Создаем нового пользователя
                new_user = User(tg_id=tg_id, username=username)
                session.add(new_user)
                await session.commit()
        except Exception as e:
            await session.rollback()
            raise e

async def create_reservation(user_tg_id, number_of_guests, reservation_time,reservation_name):
    async with async_session() as session:
        try:
            # Проверяем, существует ли пользователь с таким tg_id
            user = await session.scalar(select(User).where(User.tg_id == user_tg_id))
            if not user:
                raise ValueError("User does not exist")

            # Находим подходящие столы по количеству мест
            available_table_query = (
                select(Table)
                .options(joinedload(Table.reservations))
                .where(
                    Table.seats >= number_of_guests,

                )
                .order_by(Table.seats.asc())  # Сортируем по количеству мест, чтобы выбрать наиболее подходящий стол
            )

            tables = await session.scalars(available_table_query)

            # Фильтруем столы, чтобы исключить те, которые уже заняты на указанное время
            suitable_table = None
            for table in tables:
                reservations = table.reservations if table.reservations is not None else []

                # Убедимся, что reservations является коллекцией
                if not isinstance(reservations, list):
                    reservations = [reservations]  # Преобразуем в список, если это одиночный объект

                if all(reservation.reservation_time != reservation_time for reservation in reservations):
                    suitable_table = table
                    break

            if not suitable_table:
                raise ValueError("No available tables for the specified time and guest count")

            # Создаем бронирование
            new_reservation = Reservation(
                user_id=user.id,
                table_id=suitable_table.id,
                reservation_time=reservation_time,
                reservation_name=reservation_name,
                number_of_guests = number_of_guests
            )
            session.add(new_reservation)

            # Сохраняем изменения в базе данных
            await session.commit()

        except Exception as e:
            await session.rollback()
            raise e


async def find_suitable_table(number_of_guests, reservation_time):
    async with async_session() as session:
        try:
            # Найти все столики с достаточным количеством мест
            available_table_query = (
                select(Table)
                .where(Table.seats >= number_of_guests)
                .order_by(Table.seats.asc())
            )
            result = await session.execute(available_table_query)
            tables = result.scalars().all()

            suitable_table = None
            for table in tables:
                # Проверка на пересечения бронирований
                reservation_query = (
                    select(Reservation)
                    .where(
                        Reservation.table_id == table.id,
                        Reservation.reservation_time == reservation_time
                    )
                )
                reservation_result = await session.execute(reservation_query)
                existing_reservation = reservation_result.scalars().first()

                if not existing_reservation:
                    suitable_table = table
                    break

            return suitable_table

        except Exception as e:
            raise


async def cancel_reservation(user_tg_id, number_of_guests, reservation_time, reservation_name):
    async with async_session() as session:
        try:
            # Проверка существования пользователя
            user = await session.scalar(select(User).where(User.tg_id == user_tg_id))
            if not user:
                raise ValueError("User does not exist")

            # Формируем запрос на удаление записи
            stmt = (
                delete(Reservation)
                    .where(
                    Reservation.user_id == user.id,
                    Reservation.number_of_guests == number_of_guests,
                    Reservation.reservation_time == reservation_time,
                    Reservation.reservation_name == reservation_name
                )
            )

            # Выполняем запрос
            result = await session.execute(stmt)
            await session.commit()

            # Проверяем количество удаленных строк
            if result.rowcount == 0:
                raise ValueError("Бронирования не найдено")

            return True

        except Exception as e:
            await session.rollback()
            raise e

async def get_all_reservations() -> list[Reservation]:
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(Reservation))
            reservations = result.scalars().all()
    return reservations

async def get_reservation_by_id(reservation_id: int) -> Reservation:
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(Reservation).where(Reservation.id == reservation_id))
            reservation = result.scalars().first()
    return reservation

async def delete_reservation_by_id(reservation_id: int) -> None:
    async with async_session() as session:
        async with session.begin():
            await session.execute(
                delete(Reservation).where(Reservation.id == reservation_id)
            )

# async def add_reservation(id,user_id,):
#     async with async_session() as session:
#         async with session.begin():
#             # Создаем новый объект Reservation
#             new_reservation = Reservation(
#                 name=name,
#                 date=date,
#                 time=time,
#                 guests=guests
#             )
#             # Вставляем объект в базу данных
#             session.add(new_reservation)
#             await session.commit()