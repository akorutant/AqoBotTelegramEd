from db import DataBase
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.dispatcher.filters import BoundFilter
from aiogram.utils.markdown import hlink, italic, bold, hbold, hitalic
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, \
    InlineKeyboardButton
from aiogram.utils.helper import Helper, HelperMode, ListItem
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from datetime import datetime, timedelta
import settings
import random

bot = Bot(token=settings.TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())
db = DataBase('work.sqlite')


class FilterWords(Helper):
    mode = HelperMode.snake_case
    STATEWORD = ListItem()
    UPDATESTATEWORD = ListItem()


def send_tasks(message):
    text = ""
    if db.get_tasks(message['from']['id'], message.chat['id']):
        for i in range(len(db.get_tasks(message['from']['id'], message.chat['id']))):
            text += f"├ {i + 1}. {hbold(db.get_tasks(message['from']['id'], message.chat['id'])[i][2])}\n"
        await message.reply(text='Поручения отправлены вам в личные сообщения.')
        await bot.send_message(text=f"│ Ваши поручения:\n{text}", parse_mode='HTML',
                               chat_id=message.from_user.id)
    elif message.chat.id == message.from_user.id:
        text = ""
        if db.get_tasks(message['from']['id'], message.chat['id']):
            for i in range(len(db.get_tasks(message['from']['id'], message.chat['id']))):
                text += f"├ {i + 1}. {hbold(db.get_tasks(message['from']['id'], message.chat['id'])[i][2])}\n"
            await bot.send_message(text=f"│ Ваши поручения:\n{text}", parse_mode='HTML',
                                   chat_id=message.from_user.id)
    else:
        await message.reply("У вас нет поручений.")


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    if member.is_chat_admin():
        if message.chat.id != message.from_user.id:
            db.add_admins(message.chat.id, message.from_user.id)
            await message.reply("Привет! Я AqoBot из Discord для Telegram!\n"
                                "Для корректной работы мне нужны права администратора.")

    else:
        if message.chat.id == message.from_user.id:
            await message.reply(text='Клавиаутра включена.', reply_markup=settings.keyboard)


@dp.message_handler(commands=['ban'])
async def kick(message: types.Message):
    member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    if message.chat.id != message.from_user.id:
        arguments = message.get_args()
        if member.is_chat_admin():
            try:
                if 'last_name' in message['from']:
                    user_name = f"{message['from']['first_name']} {message['from']['last_name']}"
                    user = hlink(user_name, "tg://user?id=" + str(message['from']['id']))
                else:
                    user_name = f"{message['from']['first_name']} "
                    user = hlink(user_name, "tg://user?id=" + str(message['from']['id']))

                if not arguments:
                    await message.bot.kick_chat_member(chat_id=message.chat.id,
                                                       user_id=message.reply_to_message.from_user.id)
                    await message.reply_to_message.reply(
                        "Этот участник получает бан.\nБан выдан администратором: {0}".format(user),
                        parse_mode="HTML")
                else:
                    await message.bot.kick_chat_member(chat_id=message.chat.id,
                                                       user_id=message.reply_to_message.from_user.id)
                    await message.reply_to_message.reply(
                        "Этот участник получает бан.\nПричина: " + arguments + "\n"
                        + "Бан выдан администратором: {0}".format(user), parse_mode="HTML")
            except:
                await message.reply("Нужно ответить на сообщение для бана.")

        else:
            await message.reply("У вас нет прав администратора.")


@dp.message_handler(content_types=["new_chat_members"])
async def handler_new_member(message):
    if 'last_name' in message['from']:
        user_name = f"{message['from']['first_name']} {message['from']['last_name']}"
        user = hlink(user_name, "tg://user?id=" + str(message['from']['id']))
    else:
        user_name = f"{message['from']['first_name']} "
        user = hlink(user_name, "tg://user?id=" + str(message['from']['id']))
    await bot.send_message(message.chat.id, "Добро пожаловать в чат, {0}! "
                                            "Перейдите в ЛС с ботом и нажмите старт: "
                                            "@AqoTgBot".format(user), parse_mode="HTML")


@dp.message_handler(commands=['tasks'])
async def get_member(message: types.Message):
    member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    if message.chat.id != message.from_user.id:
        if member.is_chat_admin():
            arguments = message.get_args()
            admin_id = message['from']['id']
            chat_id = message.chat['id']
            if not arguments:
                await message.reply("Вы не назначили поручение.")
                return

            elif len(arguments) < 6:
                await message.reply("Слишком коротко. Выдайте поручение длиннее пяти символов.")
                return
            if not message.reply_to_message:
                users = db.get_users_by_chat_id(message.chat.id)
                if users:
                    random_user = random.choice(users)
                    db.add_task(random_user, arguments, admin_id, chat_id)
                    if 'last_name' in message['from']:
                        user_name = f"{message['from']['first_name']} {message['from']['last_name']}"
                        user = hlink(user_name, "tg://user?id=" + str(message['from']['id']))
                    else:
                        user_name = f"{message['from']['first_name']} "
                        user = hlink(user_name, "tg://user?id=" + str(message['from']['id']))
                    await message.reply(
                        "Поручение выдано для {0}".format(user) + ": " + "\n" + hbold(arguments),
                        parse_mode="HTML")
                else:
                    await message.reply('Нет участников, соотвествующих требованиям.')

            else:
                if 'last_name' in message['from']:
                    user_name = f"{message['from']['first_name']} {message['from']['last_name']}"
                    user = hlink(user_name, "tg://user?id=" + str(message['from']['id']))
                else:
                    user_name = f"{message['from']['first_name']} "
                    user = hlink(user_name, "tg://user?id=" + str(message['from']['id']))
                task_user = message.reply_to_message['from']['id']
                task_admin = await bot.get_chat_member(message.chat.id,
                                                       message.reply_to_message['from']['id'])

                if db.check_tasks(task_user, message.chat.id):
                    await message.reply("Можно выдать не более пяти поручений.")
                else:
                    if task_admin.is_chat_admin():
                        await message.reply("Нельзя выдать поручение администратору.")

                    elif not arguments:
                        await message.reply("Вы не назаначили поручение.")

                    elif len(arguments) < 6:
                        await message.reply(
                            "Слишком коротко. Выдайте поручение длинее пяти символов.")

                    elif task_user == admin_id:
                        await message.reply("Нельзя выдать поручение самому себе.")

                    else:
                        db.add_task(task_user, arguments, admin_id, chat_id)
                        await message.reply(
                            "Поручение выдано для {0}".format(user) + ": " + "\n" + hbold(arguments),
                            parse_mode="HTML")

        else:
            send_tasks(message)


@dp.message_handler(commands="tagsdel")
async def del_task(message: types.Message):
    member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    if message.chat.id != message.from_user.id:
        if member.is_chat_admin():
            arguments = message.get_args()
            from_id = message.reply_to_message['from']['id']
            chat_id = message.chat['id']
            if not arguments:
                await message.reply("Вы не указали номер поручения.")
                return
            if not message.reply_to_message:
                await message.reply("Нужно ответить на сообщение от пользователя.")

            else:
                tasks = db.get_tasks(from_id, chat_id)
                if int(arguments) > len(tasks) + 1:
                    await message.reply("Вы указали неверный номер поручения.")
                    return
                task = tasks[int(arguments) - 1]
                db.task_delete(task[0])
                await message.reply(f"Было удалено поручение: {task[2]}")
        else:
            await message.reply("У вас недостаточно прав.")


@dp.message_handler(commands=['filter'])
async def filter_chat(message: types.Message):
    member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    if message.chat.id != message.from_user.id:
        if member.is_chat_admin():
            db.change_filter(message.chat.id)
            state = dp.current_state(user=message.from_user.id)
            await message.answer("Хотите ли вы включить фильтрацию чата?",
                                 reply_markup=settings.button)
            if db.check_filter(chat_id=message.chat.id):
                await state.reset_state(FilterWords.all()[0])
        else:
            await message.reply('У вас нет прав администратора для выполнения команды.', )


@dp.callback_query_handler(lambda c: c.data, state='*')
async def process_callback_button1(callback_query: types.CallbackQuery):
    member = await bot.get_chat_member(callback_query.message.chat.id,
                                       callback_query.from_user.id)
    state = dp.current_state(user=callback_query.from_user.id)
    chat_id = callback_query.message.chat.id
    if member.is_chat_admin():
        if callback_query.data == 'button_on':
            if db.check_filter(chat_id=chat_id):
                await bot.answer_callback_query(callback_query.id)
                await callback_query.bot.edit_message_text(text='Фильтрация чата уже включена.',
                                                           chat_id=callback_query.message.chat.id,
                                                           message_id=callback_query.message.message_id)
            elif db.get_words_by_chat(chat_id=chat_id):
                await state.reset_state(FilterWords.all()[0])
                await bot.answer_callback_query(callback_query.id)
                await callback_query.bot.edit_message_text(text='Фильтрация чата включена.',
                                                           chat_id=callback_query.message.chat.id,
                                                           message_id=callback_query.message.message_id)
                db.change_filter(chat_id=callback_query.message.chat.id)

            elif db.check_filter(chat_id=chat_id):
                await bot.answer_callback_query(callback_query.id)
                await callback_query.bot.edit_message_text(text='Фильтрация чата уже включена.',
                                                           chat_id=callback_query.message.chat.id,
                                                           message_id=callback_query.message.message_id)
            else:
                await state.set_state(FilterWords.all()[0])
                await bot.answer_callback_query(callback_query.id)
                await callback_query.bot.edit_message_text(text='Укажите слово',
                                                           chat_id=callback_query.message.chat.id,
                                                           message_id=callback_query.message.message_id)
        elif callback_query.data == 'button_off':
            if not db.check_filter(chat_id):
                await bot.answer_callback_query(callback_query.id)
                await callback_query.bot.edit_message_text(text='Фильтрация чата уже отключена.',
                                                           chat_id=callback_query.message.chat.id,
                                                           message_id=callback_query.message.message_id)
            else:
                db.change_filter(chat_id)
                await bot.answer_callback_query(callback_query.id)
                await callback_query.bot.edit_message_text(text='Фильтрация чата отключена.',
                                                           chat_id=callback_query.message.chat.id,
                                                           message_id=callback_query.message.message_id)
        elif callback_query.data == 'button_filter':
            if db.check_filter(chat_id=chat_id):
                await bot.answer_callback_query(callback_query.id)
                await callback_query.bot.edit_message_text(
                    text='Укажите слово',
                    chat_id=chat_id,
                    message_id=callback_query.message.message_id)
                await state.set_state(FilterWords.all()[1])
            else:
                await callback_query.bot.edit_message_text(
                    text='Фильтрация в чате отключена. Включите её, чтобы дополнить '
                         'список слов.',
                    chat_id=chat_id,
                    message_id=callback_query.message.message_id)
        elif callback_query.data == 'button_delete':
            if db.check_filter(chat_id=chat_id):
                db.delete_words(chat_id=chat_id)
                await bot.answer_callback_query(callback_query.id)
                await callback_query.bot.edit_message_text(text='Список слов был очищен.',
                                                           chat_id=chat_id,
                                                           message_id=callback_query.message.message_id)


@dp.message_handler(state=FilterWords.STATEWORD)
async def bad_words(message: types.Message):
    argument = message.text
    if '/' in argument:
        await message.reply('Нельзя добавить команду в список.')
    else:
        state = dp.current_state(user=message.from_user.id)
        db.add_words(chat_id=message.chat.id, words=argument)
        await message.reply('Фильтрация чата включена и слово добавлено в список запрещенных.')
        await state.reset_state(FilterWords.all()[0])
        db.change_filter(chat_id=message.chat.id)


@dp.message_handler(state=FilterWords.UPDATESTATEWORD)
async def bad_words_update(message: types.Message):
    argument = message.text
    if '/' in argument:
        await message.reply('Нельзя добавить команду в список.')
    else:
        state = dp.current_state(user=message.from_user.id)
        db.add_words(chat_id=message.chat.id, words=argument)
        await message.reply('Фильтрация чата включена и слово добавлено в список запрещенных.')
        await state.reset_state(FilterWords.all()[1])
        db.change_filter(chat_id=message.chat.id)


@dp.message_handler(commands=['keyboard'])
async def keyboard_buttons(message: types.Message):
    await message.reply(text='Клавиаутра включена.', reply_markup=settings.keyboard)


@dp.message_handler()
async def catch_messages(message: types.Message):
    db.add_users(message['from']['id'], message.chat['id'])
    member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    if 'last_name' in message['from']:
        user_name = f"{message['from']['first_name']} {message['from']['last_name']}"
        user = hlink(user_name, "tg://user?id=" + str(message['from']['id']))
    else:
        user_name = f"{message['from']['first_name']} "
        user = hlink(user_name, "tg://user?id=" + str(message['from']['id']))

    if not member.is_chat_admin():
        if db.filter_chat(message.chat.id):
            for i in db.filter_chat(message.chat.id):
                if i.lower() in message['text'].lower():
                    await bot.send_message(text='{0}, получает ограничение прав в чате на один час'
                                                ', за использование запрещённых слов.'.format(user),
                                           chat_id=message.chat.id,
                                           parse_mode='HTML')
                    await bot.restrict_chat_member(chat_id=message.chat.id,
                                                   user_id=message.from_user.id,
                                                   until_date=datetime.now() + timedelta(minutes=60))
                    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    if not member.is_chat_admin():
        if message.text == 'Поручения':
            send_tasks(message)
    if message.text == 'Погода':
        await message.reply('+248 градусов в Сыктывкаре')


if __name__ == '__main__':
    executor.start_polling(dp)
