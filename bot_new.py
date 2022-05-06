from db_new import DataBase
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.utils.markdown import hlink, hbold
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, \
    InlineKeyboardButton
from aiogram.utils.helper import Helper, HelperMode, ListItem
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from datetime import datetime, timedelta
import settings
import random
import asyncio

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
            if message.chat.type == 'supergroup':
                db.add_chat_info(message.chat.id, message.chat.title)
                await message.reply(
                    "Привет! Я AqoBot!\nДля корректной работы мне нужны права администратора.\n\n"
                    "Если вы старый пользователь чата, напишите /reg для добавления в базу данных.")
            else:
                await message.reply("Привет! Я AqoBot!\nВаш чат не является супергруппой, "
                                    "я не смогу корректно работать.\n\n"
                                    "Чтобы сделать этот чат супергруппой, "
                                    "то измените просмотр истории группы для всех.")

    else:
        if message.chat.id == message.from_user.id:
            await message.reply(text='Привет! Я AqoBot!\nДобавь меня в чат '
                                     'и начни со мной работать!',
                                reply_markup=settings.keyboard)


@dp.message_handler(commands=['ban'])
async def ban(message: types.Message):
    member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    if message.chat.id != message.from_user.id:
        arguments = message.get_args()
        if member.is_chat_admin():
            try:
                if 'last_name' in message['reply_to_message']:
                    user_name = f"{message['reply_to_message']['first_name']} " \
                                f"{message['reply_to_message']['last_name']}"
                    user = hlink(user_name,
                                 "tg://user?id=" + str(message['reply_to_message']['id']))
                else:
                    user_name = f"{message['reply_to_message']['first_name']} "
                    user = hlink(user_name,
                                 "tg://user?id=" + str(message['reply_to_message']['id']))

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
        db.add_user(message.chat.id, message['from']['id'])
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
                            user_ping = hlink(user_name, "tg://user?id=" + str(
                                message['reply_to_message']['id']))
                        else:
                            user_name = f"{user['first_name']} "
                            user_ping = hlink(user_name, "tg://user?id=" + str(random_user))
                        await message.reply(
                            "Поручение выдано для {0}".format(user_ping) + ": " + "\n" + hbold(
                                arguments),
                            parse_mode="HTML")
                    else:
                        await message.reply('Нет участников, соотвествующих требованиям.')

            else:
                if 'last_name' in message.reply_to_message['from']:
                    user_name = f"{message.reply_to_message['from']['first_name']} " \
                                f"{message.reply_to_message['from']['last_name']}"
                    user = hlink(user_name,
                                 "tg://user?id=" + str(message.reply_to_message['from']['id']))
                else:
                    user_name = f"{message.reply_to_message['from']['first_name']} "
                    user = hlink(user_name,
                                 "tg://user?id=" + str(message.reply_to_message['from']['id']))
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
                        db.add_task(task_user, chat_id, message.chat.title, arguments, admin_id)
                        await message.reply(
                            "Поручение выдано для {0}".format(user) + ": " + "\n" + hbold(
                                arguments),
                            parse_mode="HTML")


@dp.message_handler(commands=['tasks'])
async def get_tasks(message: types.Message):
    if message.chat.id != message.from_user.id:
        try:
            await settings.send_tasks(message)
        except:
            await message.reply('Похоже, вы не написали в лс @AqoTgBot /start.')
    else:
        await settings.send_tasks(message)


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
                print(arguments)
                task = tasks[int(arguments) - 1]
                db.task_delete(task[0])
                await message.reply(f"Было удалено поручение: {task[1]}")
        else:
            await message.reply("У вас недостаточно прав.")


@dp.message_handler(commands=['filter'])
async def filter_chat(message: types.Message):
    user = message.from_user.id
    if db.get_admin_id(user):
        chat_titles = db.get_chat_titles_by_admin_id(user)
        for chat_title in chat_titles:
            settings.keyboard_chat_titles.add(chat_title)
        state = dp.current_state(user=message.from_user.id)
        await bot.send_message(text="Выберите чат для работы с фильтром.",
                               reply_markup=settings.keyboard_chat_titles,
                               chat_id=message.from_user.id)
        if message.chat.id != message.from_user.id:
            if message.chat.type == 'group':
                await message.reply(
                    'Этот чат является группой. Фильтрация невозможна в чате, данного типа.\n\n'
                    'Чтобы сделать этот чат супергруппой, '
                    'то измените просмотр истории группы для всех.')
            await message.reply('Бот отправил вам инструкции в ЛС.')

        if db.check_filter(chat_id=message.chat.id):
            await state.reset_state(FilterWords.all()[0])
    else:
        await message.reply('У вас нет прав администратора для выполнения команды.', )


@dp.callback_query_handler(lambda c: c.data == 'button_un_mute')
async def process_callback_button_un_mute(callback_query: types.CallbackQuery):
    member = await bot.get_chat_member(callback_query.message.chat.id,
                                       callback_query.from_user.id)
    if member.is_chat_admin():
        await bot.restrict_chat_member(chat_id=callback_query.message.chat.id,
                                       user_id=settings.muted_user[
                                           callback_query.message.chat.id],
                                       can_send_messages=True,
                                       can_send_media_messages=True,
                                       can_send_other_messages=True,
                                       can_add_web_page_previews=True)

        await bot.answer_callback_query(callback_query_id=callback_query.id,
                                        text='Пользователь был размучен.',
                                        show_alert=False)
    else:
        await bot.answer_callback_query(callback_query_id=callback_query.id,
                                        text='У вас нет прав для размута.',
                                        show_alert=False)


@dp.callback_query_handler(lambda c: c.data == 'button_on', state='*')
async def process_callback_button_on(callback_query: types.CallbackQuery):
    state = dp.current_state(user=callback_query.from_user.id)
    user = callback_query.from_user.id
    if db.get_admin_id(user):
        chat_id = settings.admin_chat_dict[callback_query.message.chat.id][0]
        chat_title = settings.admin_chat_dict[callback_query.message.chat.id][1]
        if db.check_filter(chat_id=chat_id):
            await bot.answer_callback_query(callback_query.id)
            await callback_query.bot.edit_message_text(text='Фильтрация чата уже включена.',
                                                       chat_id=user,
                                                       message_id=callback_query.message.message_id,
                                                       reply_markup=settings.button)
        elif db.get_words_by_chat(chat_id=chat_id):
            await state.reset_state(FilterWords.all()[0])
            await bot.answer_callback_query(callback_query.id)
            await callback_query.bot.edit_message_text(text='Фильтрация чата включена.',
                                                       chat_id=user,
                                                       message_id=callback_query.message.message_id,
                                                       reply_markup=settings.button)
            db.change_filter(chat_id=chat_id, chat_title=chat_title)

        elif db.check_filter(chat_id=chat_id):
            await bot.answer_callback_query(callback_query.id)
            await callback_query.bot.edit_message_text(text='Фильтрация чата уже включена.',
                                                       chat_id=user,
                                                       message_id=callback_query.message.message_id,
                                                       reply_markup=settings.button)
        else:
            await state.set_state(FilterWords.all()[0])
            await bot.answer_callback_query(callback_query.id)
            await callback_query.bot.edit_message_text(text='Укажите слово',
                                                       chat_id=user,
                                                       message_id=callback_query.message.message_id)


@dp.message_handler(state=FilterWords.STATEWORD)
async def bad_words(message: types.Message):
    argument = message.text
    user = message.from_user.id
    chat_id = settings.admin_chat_dict[message.from_user.id][0]
    chat_title = settings.admin_chat_dict[message.from_user.id][1]
    if db.get_admin_id(user):
        if '/' in argument:
            await message.reply('Нельзя добавить команду в список.')
        else:
            state = dp.current_state(user=message.from_user.id)
            if db.add_words(chat_id=chat_id, word=argument.lower()):
                await message.reply('Это слово уже есть в списке, укажите другое.')
            else:
                db.add_words(chat_id=chat_id, word=argument.lower())
                await message.answer(
                    'Фильтрация чата включена и слово добавлено в список запрещенных.',
                    reply_markup=settings.button)
                await state.reset_state(FilterWords.all()[0])
                db.change_filter(chat_id=chat_id, chat_title=chat_title)


@dp.callback_query_handler(lambda c: c.data == 'button_off')
async def process_callback_button_off(callback_query: types.CallbackQuery):
    user = callback_query.from_user.id
    if db.get_admin_id(user):
        chat_id = settings.admin_chat_dict[callback_query.message.chat.id][0]
        chat_title = settings.admin_chat_dict[callback_query.message.chat.id][1]
        if not db.check_filter(chat_id):
            await bot.answer_callback_query(callback_query.id)
            await callback_query.bot.edit_message_text(text='Фильтрация чата уже отключена.',
                                                       chat_id=user,
                                                       message_id=callback_query.message.message_id,
                                                       reply_markup=settings.button)
        else:
            db.change_filter(chat_id, chat_title=chat_title)
            await bot.answer_callback_query(callback_query.id)
            await callback_query.bot.edit_message_text(text='Фильтрация чата отключена.',
                                                       chat_id=user,
                                                       message_id=callback_query.message.message_id,
                                                       reply_markup=settings.button)


@dp.callback_query_handler(lambda c: c.data == 'button_update', state='*')
async def process_callback_button_update(callback_query: types.CallbackQuery):
    state = dp.current_state(user=callback_query.from_user.id)
    user = callback_query.from_user.id
    if db.get_admin_id(user):
        chat_id = settings.admin_chat_dict[callback_query.message.chat.id][0]
        if db.check_filter(chat_id=chat_id):
            await bot.answer_callback_query(callback_query.id)
            await callback_query.bot.edit_message_text(
                text='Укажите слово',
                chat_id=user,
                message_id=callback_query.message.message_id)
            await state.set_state(FilterWords.all()[1])
        else:
            await callback_query.bot.edit_message_text(
                text='Фильтрация в чате отключена. Включите её, чтобы дополнить '
                     'список слов.',
                chat_id=user,
                message_id=callback_query.message.message_id,
                reply_markup=settings.button)


@dp.message_handler(state=FilterWords.UPDATESTATEWORD)
async def bad_words_update(message: types.Message):
    argument = message.text
    user = message.from_user.id
    if db.get_admin_id(user):
        admin_id = db.get_admin_id(user)[0]
        chat_id = settings.admin_chat_dict[message.from_user.id][0]
        if '/' in argument:
            await message.reply('Нельзя добавить команду в список.')
        else:
            state = dp.current_state(user=admin_id)
            if db.add_words(chat_id=chat_id, word=argument.lower()):
                await message.reply('Это слово уже есть в списке, укажите другое.')
            else:
                db.add_words(chat_id=chat_id, word=argument.lower())
                await message.answer('Слово добавлено в список запрещенных.',
                                     reply_markup=settings.button)
                await state.reset_state(FilterWords.all()[1])


@dp.callback_query_handler(lambda c: c.data == 'button_delete')
async def process_callback_button_filter(callback_query: types.CallbackQuery):
    user = callback_query.from_user.id
    if db.get_admin_id(user):
        chat_id = settings.admin_chat_dict[callback_query.message.chat.id][0]
        db.delete_words(chat_id=chat_id)
        await bot.answer_callback_query(callback_query.id)
        await bot.edit_message_text(text='Список слов был очищен.',
                                    chat_id=user,
                                    message_id=callback_query.message.message_id,
                                    reply_markup=settings.button)


@dp.callback_query_handler(lambda c: c.data == '1')
async def process_callback_button_delete_task_one(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    chat_id = db.get_chat_id_by_user_id(user_id)[0]
    if db.get_user(user_id):
        if db.get_tasks(user_id, chat_id):
            task = db.get_tasks(user_id, chat_id)[0]
            db.task_delete(task[0])
            text = ""
            btn_list = []
            buttons_delete_tasks = InlineKeyboardMarkup(row_width=5)
            for i in range(
                    len(db.get_tasks(user_id, chat_id))):
                text += f"├ {i + 1}. " \
                        f"{hbold(db.get_tasks(user_id, chat_id)[i][1])}\n"
            buttons_delete_tasks.row(*btn_list)
            await bot.answer_callback_query(callback_query.id)
            await bot.edit_message_text(text=f"│ Ваши поручения:\n{text}\n"
                                             f"---------------------\n"
                                             f"Было удалено поручение: {task[1]}\n"
                                             f"---------------------"
                                             f"Если вы выполнили поручение, то нажмите на кнопку, "
                                             f"чтобы удалить.",
                                        parse_mode='HTML',
                                        chat_id=user_id,
                                        message_id=callback_query.message.message_id,
                                        reply_markup=buttons_delete_tasks)


@dp.callback_query_handler(lambda c: c.data == '2')
async def process_callback_button_delete_task_one(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    chat_id = db.get_chat_id_by_user_id(user_id)[0]
    if db.get_user(user_id):
        if db.get_tasks(user_id, chat_id):
            task = db.get_tasks(user_id, chat_id)[0]
            db.task_delete(task[0])


@dp.message_handler(commands=['keyboard'])
async def keyboard_buttons(message: types.Message):
    await message.reply(text='Клавиаутра включена.', reply_markup=settings.keyboard)


@dp.message_handler(commands=['reg'])
async def reg(message: types.Message):
    db.add_user(message.chat.id, message.from_user.id)
    mess = await message.reply('Вы добавлены в базу данных.')
    await asyncio.sleep(5)
    await mess.delete()


@dp.message_handler()
async def catch_messages(message: types.Message):
    member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    if message.chat.id != message.from_user.id:
        if message.chat.type == 'supergroup':
            db.add_chat_info(message.chat.id, message.chat.title)
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
                if message.chat.type == 'supergroup':
                    if db.check_filter(message.chat.id):
                        for i in db.get_words_by_chat(message.chat.id):
                            if i in message['text'].lower():
                                await bot.send_message(
                                    text='{0}, получает ограничение прав в чате на один час'
                                         ' за использование запрещённых слов.\n'
                                         '------------------------------'
                                         'Кнопка действительна до следующего мута.'.format(user),
                                    chat_id=message.chat.id,
                                    parse_mode='HTML',
                                    reply_markup=settings.un_mute_button)
                                settings.muted_user[message.chat.id] = message.from_user.id
                                await bot.restrict_chat_member(chat_id=message.chat.id,
                                                               user_id=settings.muted_user[
                                                                   message.chat.id],
                                                               until_date=datetime.now() + timedelta(
                                                                   minutes=60))
                                await bot.delete_message(chat_id=message.chat.id,
                                                         message_id=message.message_id)
        if not member.is_chat_admin():
            if message.text == 'Поручения':
                await settings.send_tasks(message)
        if message.text == 'Погода':
            await message.reply('+248 градусов в Сыктывкаре')
    else:
        if message.text == 'Поручения':
            await settings.send_tasks(message)
        if db.get_chat_titles_by_admin_id(message.chat.id):
            for chat_title in db.get_chat_titles_by_admin_id(message.chat.id):
                if message.text == chat_title:
                    settings.admin_chat_dict[message.from_user.id] = (
                        db.get_chat_id_by_chat_title(chat_title)[0], chat_title)
                    await bot.send_message(text=f'Выберите действие для чата {chat_title}',
                                           reply_markup=settings.button,
                                           chat_id=message.chat.id)


if __name__ == '__main__':
    executor.start_polling(dp)
