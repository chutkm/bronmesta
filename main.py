# import asyncio
# from aiogram import Bot, Dispatcher, F
#
# from app.handlers import router
# from app.database.models import async_main

#python main.py
#python app\web.py
#python -m app.web
#
# async def main():
#     # print("Запуск создания таблиц...")
#     await async_main()
#     # print("Таблицы созданы.")
#
#     bot = Bot(token='7101129783:AAH8nZtOvPUyfCAg7008QxjR13Fb5b63ShA')
#     dp = Dispatcher()
#     dp.include_router(router)
#     await dp.start_polling(bot)
#
# if __name__ == "__main__":
#     try:
#         asyncio.run(main())
#     except KeyboardInterrupt:
#         print("Бот выключен")

import asyncio
from aiogram import Bot, Dispatcher
from quart import Quart, render_template, redirect, url_for
from app.handlers import router
from app.database.models import async_main
from app.database.requests import get_all_reservations, delete_reservation_by_id

# Создание экземпляра веб-приложения
app = Quart(__name__, template_folder='templates')


@app.route('/')
async def index():
    reservations = await get_all_reservations()
    return await render_template('index.html', reservations=reservations)


@app.route('/delete/<int:reservation_id>')
async def delete_reservation(reservation_id):
    await delete_reservation_by_id(reservation_id)
    return redirect(url_for('index'))


# Функция для запуска бота
async def start_bot():
    await async_main()  # Инициализация базы данных
    bot = Bot(token='7101129783:AAH8nZtOvPUyfCAg7008QxjR13Fb5b63ShA')
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


async def start_web():
    await app.run_task(debug=True)


async def main():

    bot_task = asyncio.create_task(start_bot())
    web_task = asyncio.create_task(start_web())

    try:
        await asyncio.gather(bot_task, web_task)
    except KeyboardInterrupt:
        print("Приложение остановлено")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
            print("Бот выключен")
