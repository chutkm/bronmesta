from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.types import Message, InputFile
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from datetime import datetime, timedelta
import re
import logging
import app.keyboards as kb
import app.database.requests as rq

router = Router()

# Создаем классы состояний для создании брони
class Register(StatesGroup):
    date = State()
    time = State()
    number_of_guests = State()
    name = State()
    number = State()
    confirm = State()
# для отмены
class CancelReservation(StatesGroup):
    name = State()
    date = State()
    time = State()
    number_of_guests = State()
    confirm_cancel = State()
# для изменения при бронировании
class Edit(StatesGroup):
    date = State()
    time = State()
    number_of_guests = State()
    name = State()
    number = State()
    confirm = State()
#------------------------------------------------------------------------MENU--------------------------
@router.message(CommandStart())
async def cmd_start(message: Message):
    await rq.set_user(message.from_user.id, username=message.from_user.username)
    photo = 'https://i.pinimg.com/564x/b9/88/30/b98830c39bce2aa77a507944b488589b.jpg'
    await message.answer_photo(photo)
    await message.answer("Здравствуйте,\n Вас приветствует сервис бронирования столиков  🤩!", reply_markup=kb.main)

@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer("Вы нажали на кнопку помощи")

@router.message(F.text == 'Контакты')
async def process_contacts(message: Message):
    contact_info = (
        "Для получения обратной связи можно также воспользоваться контактными данными:\n"
        "📞 Телефон: +1234567890\n"
        "✉️ Email: example@example.com\n"
        "🌐 Вебсайт: www.example.com"
    )
    await message.answer(contact_info)

@router.message(F.text == 'О нас')
async def process_about(message: Message):
    contact_info = "информация***"
    await message.answer(contact_info)

@router.callback_query(lambda c: c.data == 'back')
async def process_back_button(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await state.clear()
    await callback_query.message.answer(
        'Вы вернулись в главное меню.',
        reply_markup=kb.main
    )







# -----------------------------------------------------------------БРОНИРОВАНИЕЕЕ

@router.message(F.text == "Бронь")
async def register_date(message: Message, state: FSMContext):
    await message.answer("Приступим  :)", reply_markup=kb.main_without_bron)
    await state.set_state(Register.date)
    await message.answer('Выберите дату бронирования:', reply_markup=kb.generate_date_buttons())


@router.callback_query(lambda c: c.data and c.data.startswith("date:"))
async def register_date_callback(callback: CallbackQuery, state: FSMContext):
    if await state.get_state() == Register.date.state or await state.get_state() == Edit.date.state:
        day = int(callback.data.split(":")[1])
        date = (datetime.now().date() + timedelta(days=day)).strftime('%d-%m-%Y')
        await state.update_data(date=date)
        await state.set_state(Register.time)
        await callback.message.answer('Выберите время бронирования:', reply_markup=kb.generate_time_buttons())
        await callback.answer()
    else:
        await confirm_reservation(callback.message, state)  # Вернуться к подтверждению всех данных
        await state.set_state(Edit.confirm)  # Переход к подтверждению
    await callback.answer()


@router.callback_query(Register.time)
async def register_time_callback(callback: CallbackQuery, state: FSMContext):
    if await state.get_state() == Register.time.state or await state.get_state() == Edit.time.state:
        hour = int(callback.data.split(":")[1])
        time = f"{hour:02d}:00"
        await state.update_data(time=time)
        await state.set_state(Register.number_of_guests)
        await callback.message.answer('Введите количество гостей:')
        await callback.answer()
    else:
        await confirm_reservation(callback.message, state)  # Вернуться к подтверждению всех данных
        await state.set_state(Edit.confirm)  # Переход к подтверждению
    await callback.answer()


@router.message(Register.number_of_guests)
async def register_number_of_guests(message: Message, state: FSMContext):
    if message.text.isdigit():
        number_of_guests = int(message.text)
        data = await state.get_data()

        try:
            reservation_time = datetime.strptime(f"{data['time']} {data['date']}", "%H:%M %d-%m-%Y")
            suitable_table = await rq.find_suitable_table(number_of_guests, reservation_time)

            if suitable_table:
                await state.update_data(number_of_guests=number_of_guests)
                await state.set_state(Register.name)
                await message.answer('Введите ваше имя:')
            else:
                await message.answer(
                    "Извините, в данный момент нет свободных столов, подходящих для указанного количества гостей. "
                    "Пожалуйста, обратитесь к менеджеру для получения дополнительной информации."
                )
                await state.finish()
        except Exception as e:
            await message.answer("Произошла ошибка при поиске столов. Пожалуйста, попробуйте еще раз позже.")
            await state.clear()
    else:
        await message.answer('Пожалуйста, введите корректное число.')


@router.message(Register.name)
async def register_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Register.number)
    await message.answer('Отправьте свой номер телефона (он должен начинаться с +7 или 8 и содержать 11 цифр):',
                         reply_markup=kb.get_number)


@router.message(Register.number)
async def register_phone_number(message: Message, state: FSMContext):
    phone_number = message.contact.phone_number if message.contact else message.text

    if re.match(r'^\+7\d{10}$|^8\d{10}$', phone_number):
        await state.update_data(number=phone_number)
        data = await state.get_data()

        reservation_datetime = datetime.strptime(f"{data['time']} {data['date']}", "%H:%M %d-%m-%Y")

        confirmation_text = (
            f'Ваше имя: {data["name"]}\n'
            f'Дата бронирования: {data["date"]}\n'
            f'Время бронирования: {data["time"]}\n'
            f'Количество гостей: {data["number_of_guests"]}\n'
            f'Номер: {data["number"]}\n\n'
            f'Информация верна?'
        )

        await state.set_state(Register.confirm)
        await message.answer(confirmation_text, reply_markup=kb.confirmation_buttons())
    else:
        await message.answer(
            'Неверный формат номера телефона. Пожалуйста, введите номер в формате +7XXXXXXXXXX или 8XXXXXXXXXX.')


@router.callback_query(lambda c: c.data and c.data.startswith("confirm:"))
async def process_confirmation(callback: CallbackQuery, state: FSMContext):
    if callback.data == "confirm:yes":
        data = await state.get_data()

        reservation_datetime = datetime.strptime(f"{data['time']} {data['date']}", "%H:%M %d-%m-%Y")
        await rq.create_reservation(
            user_tg_id=callback.from_user.id,
            number_of_guests=int(data['number_of_guests']),
            reservation_time=reservation_datetime,
            reservation_name=str(data['name'])
        )

        await callback.message.answer("Ваше бронирование успешно сохранено!",reply_markup=kb.main)

        photo_url = 'https://i.pinimg.com/236x/a1/32/25/a132254161a11046bcce670316e6c43d.jpg'
        await callback.message.bot.send_photo(
            chat_id=callback.message.chat.id,  # Передаем chat_id как параметр
            photo=photo_url,
            caption='Спасибо за ваше бронирование! Мы ждем вас в нашем ресторане 😊'
        )

        await state.clear()

    elif callback.data == "confirm:no":
        await callback.message.answer("Что вы хотите исправить?", reply_markup=kb.correction_buttons())
        await callback.answer()


# @router.callback_query(lambda c: c.data and c.data.startswith("correct:"))
# async def process_correction(callback: CallbackQuery, state: FSMContext):
#     correction_type = callback.data.split(":")[1]
#
#     if correction_type == "date":
#         await state.set_state(Register.date)
#         await callback.message.answer('Выберите новую дату бронирования:', reply_markup=kb.generate_date_buttons())
#     elif correction_type == "time":
#         await state.set_state(Register.time)
#         await callback.message.answer('Выберите новое время бронирования:', reply_markup=kb.generate_time_buttons())
#     elif correction_type == "guests":
#         await state.set_state(Register.number_of_guests)
#         await callback.message.answer('Введите новое количество гостей:')
#     elif correction_type == "name":
#         await state.set_state(Register.name)
#         await callback.message.answer('Введите новое имя:')
#     elif correction_type == "number":
#         await state.set_state(Register.number)
#         await callback.message.answer('Отправьте новый номер телефона', reply_markup=kb.get_number)
#
#     await callback.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("correct:"))
async def process_correction(callback: CallbackQuery, state: FSMContext):
    correction_type = callback.data.split(":")[1]
    await state.update_data(correction_type=correction_type)  # Сохраняем тип изменения

    if correction_type == "date":
        await state.set_state(Edit.date)
        await callback.message.answer('Выберите новую дату бронирования:', reply_markup=kb.generate_date_buttons())
    elif correction_type == "time":
        await state.set_state(Edit.time)
        await callback.message.answer('Выберите новое время бронирования:', reply_markup=kb.generate_time_buttons())
    elif correction_type == "guests":
        await state.set_state(Edit.number_of_guests)
        await callback.message.answer('Введите новое количество гостей:')
    elif correction_type == "name":
        await state.set_state(Edit.name)
        await callback.message.answer('Введите новое имя:')
    elif correction_type == "number":
        await state.set_state(Edit.number)
        await callback.message.answer('Отправьте новый номер телефона', reply_markup=kb.get_number)

    await callback.answer()

@router.message(Edit.date)
async def edit_date(message: Message, state: FSMContext):
    if message.text:
        await state.update_data(date=datetime.strptime(message.text, "%d-%m-%Y").date())
        await confirm_reservation(message, state)
        await state.set_state(Edit.confirm)

@router.callback_query(Edit.time)
async def edit_time(callback: CallbackQuery, state: FSMContext):
    if await state.get_state() == Edit.time.state:
        hour = int(callback.data.split(":")[1])
        time = f"{hour:02d}:00"
        await state.update_data(time=time)
        await confirm_reservation(callback.message, state)
        await state.set_state(Edit.confirm)

@router.message(Edit.number_of_guests)
async def edit_number_of_guests(message: Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(number_of_guests=int(message.text))
        await confirm_reservation(message, state)
        await state.set_state(Edit.confirm)
    else:
        await message.answer('Пожалуйста, введите корректное число.')

@router.message(Edit.name)
async def edit_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await confirm_reservation(message, state)
    await state.set_state(Edit.confirm)

@router.message(Edit.number)
async def edit_number(message: Message, state: FSMContext):
    phone_number = message.contact.phone_number if message.contact else message.text

    if re.match(r'^\+7\d{10}$|^8\d{10}$', phone_number):
        await state.update_data(number=phone_number)
        await confirm_reservation(message, state)
        await state.set_state(Edit.confirm)
    else:
        await message.answer('Неверный формат номера телефона. Пожалуйста, введите номер в формате +7XXXXXXXXXX или 8XXXXXXXXXX.')




async def confirm_reservation(message: Message, state: FSMContext):
    data = await state.get_data()
    confirmation_text = (
        f'Ваше имя: {data["name"]}\n'
        f'Дата бронирования: {data["date"]}\n'
        f'Время бронирования: {data["time"]}\n'
        f'Количество гостей: {data["number_of_guests"]}\n'
        f'Номер: {data["number"]}\n\n'
        f'Информация верна?'
    )

    await message.answer(confirmation_text, reply_markup=kb.confirmation_buttons())





#--------------------------------------------------------------------------ОТМЕНА----------------------------------
@router.message(F.text == 'Отмена брони')
async def cancel_reservation_start(message: Message, state: FSMContext):
    await message.answer("Для отмены бронирования, пожалуйста, введите имя, на которое была сделана бронь:",reply_markup=kb.main_without_bron)
    await state.set_state(CancelReservation.name)

# Ввод имени
@router.message(CancelReservation.name)
async def cancel_reservation_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите дату бронирования (формат: дд-мм-гггг):")
    await state.set_state(CancelReservation.date)

# Ввод даты
@router.message(CancelReservation.date)
async def cancel_reservation_date(message: Message, state: FSMContext):
    try:
        reservation_date = datetime.strptime(message.text, "%d-%m-%Y").date()
        await state.update_data(date=reservation_date)
        await message.answer("Введите время бронирования (формат: чч:мм):", reply_markup = kb.generate_time_buttons())
        await state.set_state(CancelReservation.time)
    except ValueError:
        await message.answer("Неверный формат даты. Пожалуйста, введите дату в формате дд-мм-гггг.")

# Ввод времени
@router.callback_query(CancelReservation.time)
async def cancel_reservation_time_callback(callback: CallbackQuery, state: FSMContext):

    try:
        if await state.get_state() == CancelReservation.time.state:
            hour = int(callback.data.split(":")[1])
            time_str = f"{hour:02d}:00"

            # Преобразование строки времени в объект datetime.time
            time_obj = datetime.strptime(time_str, '%H:%M').time()

            # Обновление данных в состоянии
            await state.update_data(time=time_obj)
        await callback.message.answer("Введите количество гостей:")
        await state.set_state(CancelReservation.number_of_guests)

    except ValueError:
        await callback.message.answer("Неверный формат времени. Пожалуйста, введите время в формате чч:мм.")


@router.message(CancelReservation.number_of_guests)
async def cancel_reservation_confirm(message: Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(number_of_guests=int(message.text))
        await state.set_state(CancelReservation.confirm_cancel)

        data = await state.get_data()
        if 'date' not in data or 'time' not in data:
            await message.answer(
                "Не удалось найти данные бронирования для отмены. Возможно, бронирование не было завершено. Пожалуйста, попробуйте снова.")
            await state.clear()
            return

        reservation_datetime = datetime.combine(data['date'], data['time']).strftime("%Y-%m-%d %H:%M:%S")


        confirmation_cancel_text = (
            f'Ваше имя: {data["name"]}\n'
            f'Дата бронирования: {data["date"].strftime("%d-%m-%Y")}\n'
            f'Время бронирования: {data["time"].strftime("%H:%M")}\n'
            f'Количество гостей: {data["number_of_guests"]}\n\n'
            f'Информация верна?'
        )
        await message.answer(confirmation_cancel_text, reply_markup=kb.cancel_buttons())
    else:
        await message.answer('Пожалуйста, введите корректное число.')


@router.callback_query(lambda c: c.data and c.data.startswith("cancel:"))
async def cancel_reservation_callback(callback: CallbackQuery, state: FSMContext):
    if callback.data == "cancel:yes":
        data = await state.get_data()
        reservation_datetime = datetime.combine(data['date'], data['time']).strftime("%Y-%m-%d %H:%M:%S")
        try:
            result = await rq.cancel_reservation(
                user_tg_id=callback.from_user.id,
                reservation_time=reservation_datetime,
                number_of_guests=int(data['number_of_guests']),
                reservation_name=str(data['name'])
            )

            if result:
                await callback.message.answer("Ваше бронирование успешно отменено.")
                await callback.message.answer("Ждем вас в гости :)",reply_markup=kb.main)

            else:
                await callback.message.answer("Не удалось найти соответствующее бронирование. Проверьте введенные данные.")
        except ValueError as e:
            # Отправляем сообщение пользователю, если бронирование не найдено
            await callback.message.answer(f"Ошибка: {str(e)}")
        except Exception as e:
    # Ловим другие возможные ошибки
            await callback.message.answer("Произошла ошибка при отмене бронирования. Пожалуйста, попробуйте снова.")
        await state.clear()
    elif callback.data == "cancel:no":
        await callback.message.answer("Что вы хотите исправить?", reply_markup=kb.correction_buttons())
        await callback.answer()
