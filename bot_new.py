from db_new import DataBase
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.utils.markdown import hlink, italic, bold, hbold, hitalic
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


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    if member.is_chat_admin():
        if message.chat.id != message.from_user.id:
            await message.reply("Привет! Я AqoBot!\n Для корректной работы мне нужны права администратора.")

    else:
        if message.chat.id == message.from_user.id:
            await message.reply(text='Клавиаутра включена.', reply_markup=settings.keyboard)


@dp.message_handler(commands=['ban'])
async def ban(message: types.Message):
    member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    if message.chat.id != message.from_user.id:
        arguments = message.get_args()
        if member.is_chat_admin():
            try:
                if 'last_name' in message['reply_to_message']:
                    user_name = f"{message['reply_to_message']['first_name']} {message['reply_to_message']['last_name']}"
                    user = hlink(user_name, "tg://user?id=" + str(message['reply_to_message']['id']))
                else:
                    user_name = f"{message['reply_to_message']['first_name']} "
                    user = hlink(user_name, "tg://user?id=" + str(message['reply_to_message']['id']))

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


@dp.message_handler(commands=['task'])
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
                    if db.check_tasks(random_user, message.chat.id) is False:
                        db.add_task(random_user, chat_id, message.chat.title, arguments, admin_id)
                        user = await bot.get_chat_member(chat_id, random_user)
                        user = user['user']

                        if 'last_name' in user:
                            user_name = f"{user['first_name']} {user['last_name']}"
                            user_ping = hlink(user_name, "tg://user?id=" + str(message['reply_to_message']['id']))
                        else:
                            user_name = f"{user['first_name']} "
                            user_ping = hlink(user_name, "tg://user?id=" + str(random_user))
                        await message.reply(
                            "Поручение выдано для {0}".format(user_ping) + ": " + "\n" + hbold(arguments),
                            parse_mode="HTML")
                    else:
                        await message.reply('Нет участников, соотвествующих требованиям.')

            else:
                if 'last_name' in message.reply_to_message['from']:
                    user_name = f"{message.reply_to_message['from']['first_name']} " \
                                f"{message.reply_to_message['from']['last_name']}"
                    user = hlink(user_name, "tg://user?id=" + str(message.reply_to_message['from']['id']))
                else:
                    user_name = f"{message.reply_to_message['from']['first_name']} "
                    user = hlink(user_name, "tg://user?id=" + str(message.reply_to_message['from']['id']))
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
                        print(message)
                        db.add_task(task_user, chat_id, message.chat.title, arguments, admin_id)
                        await message.reply(
                            "Поручение выдано для {0}".format(user) + ": " + "\n" + hbold(arguments),
                            parse_mode="HTML")


@dp.message_handler(commands=['tasks'])
async def get_tasks(message: types.Message):
    member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    if message.chat.id != message.from_user.id:
        try:
            await settings.send_tasks(message)
        except:
            await message.reply('Похоже, вы не написали в лс @AqoTgBot /start.')


@dp.message_handler(commands="taskdel")
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
                await message.reply(f"Было удалено поручение: {task[1]}")
        else:
            await message.reply("У вас недостаточно прав.")


@dp.message_handler(commands=['filter'])
async def filter_chat(message: types.Message):
    member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    if message.chat.id != message.from_user.id:
        if member.is_chat_admin():
            db.change_filter(message.chat.id)
            state = dp.current_state(user=message.from_user.id)
            await bot.send_message(text="Выберите действие для работы с фильтром.",
                                   reply_markup=settings.button,
                                   chat_id=message.from_user.id)

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
    if message.chat.id != message.from_user.id:
        await message.reply(text='Клавиаутра включена.', reply_markup=settings.keyboard)


@dp.message_handler()
async def catch_messages(message: types.Message):
    member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    if 'last_name' in message['from']:
        user_name = f"{message['from']['first_name']} {message['from']['last_name']}"
        user = hlink(user_name, "tg://user?id=" + str(message['from']['id']))
    else:
        user_name = f"{message['from']['first_name']} "
        user = hlink(user_name, "tg://user?id=" + str(message['from']['id']))

    admins = await bot.get_chat_administrators(message.chat.id)
    for admin in admins:
        if admin['user']['is_bot'] is False:
            db.add_admins(message.chat.id, admin['user']['id'], message.chat.title)
    if not member.is_chat_admin():
        db.add_user(message.chat.id, message.from_user.id)
        if db.check_filter(message.chat.id):
            for i in db.get_words_by_chat(message.chat.id):
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
            await settings.send_tasks(message)
    if message.text == 'Погода':
        await message.reply('+248 градусов в Сыктывкаре')


if __name__ == '__main__':
    executor.start_polling(dp)
