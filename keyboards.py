from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
)

main = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Переглянути каталог"),
            KeyboardButton(text="Змінити каталог")
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder="Виберіть дію з меню",
)

add_pizza = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Додати назву"),
            KeyboardButton(text="Додати тип"),
        ],
        [
            KeyboardButton(text="Додати розмір"),
            KeyboardButton(text="Додати ціну"),
        ],
        [
            KeyboardButton(text="Додати картинку"),
        ],
        [
            KeyboardButton(text="✔ Готово"),
            KeyboardButton(text="❌ Скасувати"),
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

change_pizza = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Змінити назву"),
            KeyboardButton(text="Змінити тип"),
        ],
        [
            KeyboardButton(text="Змінити розмір"),
            KeyboardButton(text="Змінити ціну"),
        ],
        [
            KeyboardButton(text="Змінити картинку"),
        ],
        [
            KeyboardButton(text="❌ Видалити піцу"),
        ],
        [
            KeyboardButton(text="✔ Готово"),
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)
