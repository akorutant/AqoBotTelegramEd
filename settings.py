from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, \
    InlineKeyboardButton
from aiogram.utils.markdown import hlink, italic, bold, hbold, hitalic
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram import Bot, types
from db_new import DataBase

# Токен.
TOKEN = '1923482161:AAE0htBy-eGqVY_KRhyjKSp7o3YlXcUPZr0'
db = DataBase('work.sqlite')
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


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


# Размут пользователя.
un_mute_button = InlineKeyboardMarkup(row_width=1)
button_un_mute = InlineKeyboardButton(text='Размутить', callback_data='button_un_mute')
un_mute_button.add(button_un_mute)


# Отправка поручений.
async def send_tasks(message):
    text = ""
    if message.chat.id != message.from_user.id:
        if db.get_tasks(message['from']['id'], message.chat['id']):
            for i in range(len(db.get_tasks(message['from']['id'], message.chat['id']))):
                text += f"├ {i + 1}. {hbold(db.get_tasks(message['from']['id'], message.chat['id'])[i][1])}\n"
            await message.reply(text='Поручения отправлены вам в личные сообщения.')
            await bot.send_message(text=f"│ Ваши поручения:\n{text}\n"
                                        f"---------------------\n"
                                        f"Нажмите на кнопку, чтобы удалить поручение.", parse_mode='HTML',
                                   chat_id=message.from_user.id)
        else:
            await message.reply("У вас нет поручений.")

    elif message.chat.id == message.from_user.id:
        text = ""
        chat = db.get_chat_id_by_user_id(message.from_user.id)[0]
        if db.get_tasks(message['from']['id'], chat):
            for i in range(len(db.get_tasks(message['from']['id'], chat))):
                text += f"├ {i + 1}. {hbold(db.get_tasks(message['from']['id'], chat)[i][1])}\n"
            await message.reply(text=f"│ Ваши поручения:\n{text}", parse_mode='HTML')
        else:
            await message.reply("У вас нет поручений.")

if __name__ == '__main__':
    executor.start_polling(dp)
