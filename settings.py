from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, \
    InlineKeyboardButton

TOKEN = '1923482161:AAE0htBy-eGqVY_KRhyjKSp7o3YlXcUPZr0'

admin_chat_dict = {}
muted_user = {}
user_chat_dict = {}

# Кнопки.
show_task = KeyboardButton('📒Поручения')
weather = KeyboardButton('☁Погода', request_location=True)
admin_button = KeyboardButton('Администратор')
user_button = KeyboardButton('Пользователь')
key = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(admin_button, user_button)
keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(show_task, weather)

# Инлайн-кнопки.
button = InlineKeyboardMarkup(row_width=2)

button_on = InlineKeyboardButton(text='✅Включить', callback_data='button_on')
button_off = InlineKeyboardButton(text='❌Отключить', callback_data='button_off')
button_filter = InlineKeyboardButton(text='✅Дополнить список', callback_data='button_update')
button_delete = InlineKeyboardButton(text='❌Очистить список', callback_data='button_delete')
button.add(button_on, button_off, button_filter, button_delete)


# Размут пользователя.
un_mute_button = InlineKeyboardMarkup(row_width=1)
button_un_mute = InlineKeyboardButton(text='✅Размутить', callback_data='button_un_mute')
un_mute_button.add(button_un_mute)

# Кнопки чатов.
keyboard_chat_titles = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

