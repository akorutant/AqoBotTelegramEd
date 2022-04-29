from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, \
    InlineKeyboardButton

# Токен.
TOKEN = '1923482161:AAE0htBy-eGqVY_KRhyjKSp7o3YlXcUPZr0'

# Кнопки.
show_task = KeyboardButton('Поручения')
weather = KeyboardButton('Погода')
keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(show_task, weather)

# Инлайн-кнопки.
button = InlineKeyboardMarkup(row_width=2)
button_on = InlineKeyboardButton(text='Включить', callback_data='button_on')
button_off = InlineKeyboardButton(text='Отключить', callback_data='button_off')
button_filter = InlineKeyboardButton(text='Дополнить список', callback_data='button_filter')
button_delete = InlineKeyboardButton(text='Очистить список', callback_data='button_delete')
button.add(button_on, button_off, button_filter, button_delete)
