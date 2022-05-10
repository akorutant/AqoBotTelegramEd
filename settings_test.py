from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, \
    InlineKeyboardButton
from aiogram.utils.markdown import hbold
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram import Bot
from db_new import DataBase

# Токен.
TOKEN = '1923482161:AAE0htBy-eGqVY_KRhyjKSp7o3YlXcUPZr0'
db = DataBase('work.sqlite')
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

admin_chat_dict = {}
muted_user = {}
user_for_weather = {}

# Кнопки.
show_task = KeyboardButton('📒Поручения')
weather = KeyboardButton('☁Погода', request_location=True)
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


# Отправка поручений.
async def send_tasks(message):
    text = ""
    if message.chat.id != message.from_user.id:
        if db.get_tasks(message['from']['id'], message.chat['id']):
            btn_list = []
            buttons_delete_tasks = InlineKeyboardMarkup(row_width=5)
            for i in range(len(db.get_tasks(message['from']['id'], message.chat['id']))):
                text += f"├ {i + 1}. " \
                        f"{hbold(db.get_tasks(message['from']['id'], message.chat['id'])[i][1])}\n"
            buttons_delete_tasks.row(*btn_list)
            await message.reply(text='Поручения отправлены вам в личные сообщения.')
            await bot.send_message(text=f"│ Ваши поручения:\n{text}\n"
                                        f"---------------------\n"
                                        f"Нажмите на кнопку, чтобы удалить поручение.",
                                   parse_mode='HTML',
                                   chat_id=message.from_user.id,
                                   reply_markup=buttons_delete_tasks)
        else:
            await message.reply("У вас нет поручений.")

    elif message.chat.id == message.from_user.id:
        text = ""
        chat = db.get_chat_id_by_user_id(message.from_user.id)
        if chat:
            chat = chat[0]
            if db.get_tasks(message['from']['id'], chat):
                btn_list = []
                buttons_delete_tasks = InlineKeyboardMarkup(row_width=5)
                for i in range(len(db.get_tasks(message['from']['id'], chat))):
                    btn_list.append(
                        InlineKeyboardButton(text=f"{i + 1} ✖️", callback_data=f'{i + 1}'))
                    text += f"├ {i + 1}. {hbold(db.get_tasks(message['from']['id'], chat)[i][1])}\n"
                buttons_delete_tasks.row(*btn_list)
                await message.reply(text=f"│ Ваши поручения:\n{text}"
                                         f"---------------------\n"
                                         f"Нажмите на кнопку, чтобы удалить поручение.",
                                    parse_mode='HTML',
                                    reply_markup=buttons_delete_tasks)

            else:
                await message.reply("У вас нет поручений.")


async def send_tasks_callback(callback_query):
    text = ""
    chat_id = db.get_chat_id_by_user_id(callback_query.from_user.id)[0]
    user_id = callback_query.from_user.id
    if db.get_tasks(user_id, chat_id):
        btn_list = []
        buttons_delete_tasks = InlineKeyboardMarkup(row_width=5)
        for i in range(
                len(db.get_tasks(user_id, chat_id))):
            text += f"├ {i + 1}. " \
                    f"{hbold(db.get_tasks(user_id, chat_id)[i][1])}\n"
        buttons_delete_tasks.row(*btn_list)
        await bot.answer_callback_query(callback_query.id)
        await callback_query.bot.edit_message_text(text=f"│ Ваши поручения:\n{text}\n"
                                                        f"---------------------\n"
                                                        f"Нажмите на кнопку, чтобы удалить поручение.",
                                                   parse_mode='HTML',
                                                   chat_id=chat_id,
                                                   message_id=callback_query.message.message_id,
                                                   reply_markup=buttons_delete_tasks)


if __name__ == '__main__':
    executor.start_polling(dp)
