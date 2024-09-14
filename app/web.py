# from quart import Quart, render_template, redirect, url_for
# from app.database.requests import get_all_reservations, delete_reservation_by_id
# import locale
# import cryptography
#
#
# locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
#
# app = Quart(__name__,template_folder='templates')
#
# @app.route('/')
# async def index():
#     try:
#         reservations = await get_all_reservations()
#         return await render_template('index.html', reservations=reservations)
#     except Exception as e:
#         return str(e)
#
# @app.route('/delete/<int:reservation_id>')
# async def delete_reservation(reservation_id):
#     await delete_reservation_by_id(reservation_id)
#     return redirect(url_for('index'))
#
#
# if __name__ == '__main__':
#     app.run(debug=True)

# from quart impo
# rt Quart, render_template, redirect, url_for
# from app.database.requests import get_all_reservations, delete_reservation_by_id
# import locale
# import cryptography
#
#
# locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
#
# app = Quart(__name__,template_folder='templates')
#
# @app.route('/')
# async def index():
#     try:
#         reservations = await get_all_reservations()
#         return await render_template('index.html', reservations=reservations)
#     except Exception as e:
#         return str(e)
#
# @app.route('/delete/<int:reservation_id>')
# async def delete_reservation(reservation_id):
#     await delete_reservation_by_id(reservation_id)
#     return redirect(url_for('index'))
#
#
# if __name__ == '__main__':
#     app.run(debug=True)
import asyncio
from aiogram import Bot, Dispatcher
from quart import Quart, render_template, redirect, url_for
import locale
from app.handlers import router
from app.database.models import async_main
from app.database.requests import get_all_reservations, delete_reservation_by_id
import logging
locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')

app = Quart(__name__, template_folder='templates')
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
async def index():
    try:
        reservations = await get_all_reservations()
        return await render_template('index.html', reservations=reservations)
    except Exception as e:
        return str(e)


@app.route('/delete/<int:reservation_id>')
async def delete_reservation(reservation_id):
    await delete_reservation_by_id(reservation_id)
    return redirect(url_for('index'))


# @app.route('/add', methods=['GET', 'POST'])
# async def add_reservation():
#     if request.method == 'POST':
#         name = request.form['name']
#         date = request.form['date']
#         time = request.form['time']
#         guests = request.form['guests']
#         # Здесь добавьте код для сохранения новой записи в базе данных
#         await add_reservation_to_db(name, date, time, guests)
#         return redirect(url_for('index'))
#
#     return await render_template('add_reservation.html')
