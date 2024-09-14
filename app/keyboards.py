from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import datetime, timedelta
# import locale
# locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
# Создаем функцию для генерации callback данных
def make_callback_data(action, value):
    return f"{action}:{value}"


main = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Бронь')],
        [KeyboardButton(text='Отмена брони')],
        [KeyboardButton(text='Контакты'), KeyboardButton(text='О нас')]
    ],
    resize_keyboard=True,
    input_field_placeholder='Выберите пункт который вас интересует'
)
main_without_bron = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Контакты'), KeyboardButton(text='О нас')]
    ],
    resize_keyboard=True,
    input_field_placeholder='Введите информацию'
)

back_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Вернуться в главное меню', callback_data='back')]
])


get_number = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Отправить номер', request_contact=True)],
        [KeyboardButton(text='Ввести номер вручную')]
    ],
    resize_keyboard=True
)


def generate_date_buttons():
    today = datetime.now().date()
    buttons = []

    # Добавляем кнопки для выбора дат
    for i in range(7):  # Предлагаем выбор из 7 дней
        date = today + timedelta(days=i)
        buttons.append(
            InlineKeyboardButton(
                text=date.strftime('%a, %d.%m'),
                callback_data=make_callback_data("date", i)
            )
        )

    # Добавляем кнопку "Назад" в отдельной строке
    back_button = InlineKeyboardButton(text="Назад в меню", callback_data="back")

    # Формируем клавиатуру
    inline_keyboard = [
        buttons[:4],  # Первая строка: 4 дня
        buttons[4:7], # Вторая строка: 3 дня
        [back_button] # Третья строка: кнопка "Назад"
    ]

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)




def generate_time_buttons():
    builder = InlineKeyboardBuilder()
    for hour in range(10, 22):  # Например, время с 10 до 22
        builder.add(
            InlineKeyboardButton(
                text=f'{hour:02d}:00',
                callback_data=make_callback_data("time", hour)
            )
        )

    builder.row(InlineKeyboardButton(text="Назад в меню", callback_data="back"))
    return builder.as_markup()


#клава при утверждении инфы о брони - верная ли она или нет
def confirmation_buttons():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Да", callback_data="confirm:yes")],
        [InlineKeyboardButton(text="Нет", callback_data="confirm:no")],
        [InlineKeyboardButton(text="Назад в меню", callback_data="back")]
    ])

def correction_buttons():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Дата", callback_data="correct:date")],
        [InlineKeyboardButton(text="Время", callback_data="correct:time")],
        [InlineKeyboardButton(text="Количество гостей", callback_data="correct:guests")],
        [InlineKeyboardButton(text="Имя", callback_data="correct:name")],
        [InlineKeyboardButton(text="Номер телефона", callback_data="correct:number")],
        [InlineKeyboardButton(text="Назад", callback_data="back")]
    ])

#отмена брони
def cancel_buttons():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Да", callback_data="cancel:yes")],
        [InlineKeyboardButton(text="Нет", callback_data="cancel:no")],
        [InlineKeyboardButton(text="Назад в меню", callback_data="back")]
    ])
