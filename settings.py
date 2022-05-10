from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, \
    InlineKeyboardButton
from aiogram.utils.markdown import hlink
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
user_chat_dict = {}

# Кнопки.
show_task = KeyboardButton('Поручения')
weather = KeyboardButton('Погода')
keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(show_task, weather)

# Инлайн-кнопки.
button = InlineKeyboardMarkup(row_width=2)

button_on = InlineKeyboardButton(text='Включить', callback_data='button_on')
button_off = InlineKeyboardButton(text='Отключить', callback_data='button_off')
button_filter = InlineKeyboardButton(text='Дополнить список', callback_data='button_update')
button_delete = InlineKeyboardButton(text='Очистить список', callback_data='button_delete')
button.add(button_on, button_off, button_filter, button_delete)

# Размут пользователя.
un_mute_button = InlineKeyboardMarkup(row_width=1)
button_un_mute = InlineKeyboardButton(text='Размутить', callback_data='button_un_mute')
un_mute_button.add(button_un_mute)

# Кнопки чатов.
keyboard_chat_titles = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)


# Отправка поручений.
async def send_tasks(message, chat_title):
    if message.chat.id == message.from_user.id:
        text = ""
        chat = db.get_chat_id_by_chat_title(chat_title)
        chat_title = chat_title
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
                await message.reply(text=f"│ Ваши поручения в чате {chat_title}:\n{text}"
                                         f"---------------------\n"
                                         f"Нажмите на кнопку, чтобы удалить поручение.",
                                    parse_mode='HTML',
                                    reply_markup=buttons_delete_tasks)

            else:
                await message.reply("У вас нет поручений.")


async def send_tasks_callback(callback_query, number):
    user_id = callback_query.from_user.id
    chat_id = user_chat_dict[user_id][0]
    chat_title = user_chat_dict[user_id][1]
    if db.get_user(user_id):
        if db.get_tasks(user_id, chat_id):
            task = db.get_tasks(user_id, chat_id)[number]
            admin_id = db.get_admin_id_from_tasks(task[1])[0]
            db.task_delete(task[0])
            text = ""
            btn_list = []
            buttons_delete_tasks = InlineKeyboardMarkup(row_width=5)
            for i in range(
                    len(db.get_tasks(user_id, chat_id))):
                btn_list.append(
                    InlineKeyboardButton(text=f"{i + 1} ✖️", callback_data=f'{i + 1}'))
                text += f"├ {i + 1}. " \
                        f"{hbold(db.get_tasks(user_id, chat_id)[i][1])}\n"
            buttons_delete_tasks.row(*btn_list)
            user = await bot.get_chat_member(chat_id, user_id)
            user = user['user']
            if 'last_name' in user:
                user_name = f"{user['first_name']} {user['last_name']}"
                user_ping = hlink(user_name, "tg://user?id=" + str(
                    callback_query.message['reply_to_message']['id']))
            else:
                user_name = f"{user['first_name']} "
                user_ping = hlink(user_name, "tg://user?id=" + str(user_id))
            await bot.answer_callback_query(callback_query.id)
            await bot.edit_message_text(text=f"│ Ваши поручения в чате {chat_title}:\n{text}\n"
                                             f"---------------------\n"
                                             f"Было удалено поручение: {task[1]}\n"
                                             f"---------------------\n"
                                             f"Если вы выполнили поручение, то нажмите на кнопку, "
                                             f"чтобы удалить.",
                                        parse_mode='HTML',
                                        chat_id=user_id,
                                        message_id=callback_query.message.message_id,
                                        reply_markup=buttons_delete_tasks)
            await bot.send_message(text=f'{user_ping} выполнил поручение: {task[1]}. Из чата: {chat_title}',
                                   chat_id=admin_id,
                                   parse_mode='HTML')
            if not db.get_tasks(user_id, chat_id):
                await bot.edit_message_text(text=f'Вы выполнили все поручения в чате {chat_title}.',
                                            chat_id=user_id,
                                            message_id=callback_query.message.message_id
                                            )


async def send_question(message):
    if message.chat.id != message.from_user.id:
        try:
            keyboard_chat_titles_from_users = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            if db.get_chat_titles_by_chat_id(db.get_chats_ids_by_user_id(message.from_user.id)[0]):
                if db.get_chats_ids_by_user_id(message.from_user.id):
                    if db.get_chat_titles_by_chat_id(db.get_chats_ids_by_user_id(message.from_user.id)[0]):
                        for chat_id in db.get_chats_ids_by_user_id(message.from_user.id):
                            for chat_title in db.get_chat_titles_by_chat_id(chat_id):
                                keyboard_chat_titles_from_users.add(chat_title)
                await bot.send_message(text='Выберите чат для просмотра задач.',
                                       reply_markup=keyboard_chat_titles_from_users,
                                       chat_id=message.from_user.id)
        except:
            await message.reply('Похоже, вы не написали в лс @AqoTgBot /start.')
    else:
        keyboard_chat_titles_from_users = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        if db.get_chat_titles_by_chat_id(db.get_chats_ids_by_user_id(message.chat.id)[0]):
            if db.get_chats_ids_by_user_id(message.chat.id):
                if db.get_chat_titles_by_chat_id(db.get_chats_ids_by_user_id(message.chat.id)[0]):
                    for chat_id in db.get_chats_ids_by_user_id(message.from_user.id):
                        for chat_title in db.get_chat_titles_by_chat_id(chat_id):
                            keyboard_chat_titles_from_users.add(chat_title)
            await bot.send_message(text='Выберите чат для просмотра задач.',
                                   reply_markup=keyboard_chat_titles_from_users,
                                   chat_id=message.from_user.id)
if __name__ == '__main__':
    executor.start_polling(dp)
