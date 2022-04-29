import db
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
import random

TOKEN = "1923482161:AAE0htBy-eGqVY_KRhyjKSp7o3YlXcUPZr0"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())


class FilterWords(Helper):
    mode = HelperMode.snake_case
    STATEWORD = ListItem()
    UPDATESTATEWORD = ListItem()


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    if message.chat.id != message.from_user.id:
        await message.reply(
            "Привет! Я AqoBot из Discord для Telegram!\nДля корректной работы мне нужны права администратора.")
    else:
        await message.reply(
            "Привет! Я AqoBot из Discord для Telegram!\nДобавьте меня в чат для того чтобы я работал")


@dp.message_handler(commands=['ban'])
async def kick(message: types.Message):
    member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    if message.chat.id != message.from_user.id:
        arguments = message.get_args()
        if member.is_chat_admin():
            try:
                user_name = message.reply_to_message['from']['id']
                u2 = message.reply_to_message['from']['first_name']
                u3 = " " + message.reply_to_message["from"]["last_name"] if \
                    message.reply_to_message["from"][
                        "last_name"] else ""
                u4 = (str(u2) + str(u3))
                user = hlink(u4, "tg://user?id=" + str(user_name))

                if not arguments:
                    BannedUserId = message.reply_to_message['from']['id']
                    await message.bot.kick_chat_member(chat_id=message.chat.id,
                                                       user_id=message.reply_to_message.from_user.id)
                    await message.reply_to_message.reply(
                        "Этот участник получает бан.\nБан выдан администратором: {0}".format(user),
                        parse_mode="HTML")
                else:
                    BannedUserId = message.reply_to_message['from']['id']
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
    user_name = message['new_chat_member']['id']
    u2 = message['new_chat_member']['first_name']
    u3 = " " + message["new_chat_member"]["last_name"] if message["new_chat_member"][
        "last_name"] else ""
    u4 = (str(u2) + str(u3))
    user = hlink(u4, "tg://user?id=" + str(user_name))
    await bot.send_message(message.chat.id, "Добро пожаловать в чат, {0}!".format(user),
                           parse_mode="HTML")


@dp.message_handler(commands=['tags'])
async def get_member(message: types.Message):
    member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    if message.chat.id != message.from_user.id:
        if member.is_chat_admin():

            arguments = message.get_args()
            from_id1 = message['from']['id']
            chat_id = message.chat['id']
            if not arguments:
                await message.reply("Вы не назначили поручение.")
                return

            elif len(arguments) < 6:
                await message.reply("Слишком коротко. Выдайте поручение длиннее пяти символов.")
                return
            if not message.reply_to_message:
                users = db.get_users(message.chat['id'])
                admins = await bot.get_chat_administrators(message.chat['id'])
                admins1 = []

                for admin in admins:
                    admins1.append(admin.user['id'])
                users1 = []
                for i in range(len(users)):
                    if not db.check_tasks(users[i], message.chat['id']) and not users[i] in admins1:
                        users1.append(users[i])

                if users1:
                    random_user = random.choice(users1)
                    db.add_tag(random_user, arguments, from_id1, chat_id)
                    user = await bot.get_chat_member(chat_id, random_user)
                    user = user['user']
                    u2 = user['first_name']
                    u3 = " " + user["last_name"] if user["last_name"] else ""
                    ping = hlink((str(u2) + str(u3)), "tg://user?id=" + str(random_user))
                    await message.reply(
                        "Поручение выдано для {0}".format(ping) + ": " + "\n" + hbold(arguments),
                        parse_mode="HTML")
                else:
                    await message.reply("Нет участников, соответствующих требованиям.")


            else:
                user_name = message.reply_to_message['from']['id']
                u2 = message.reply_to_message['from']['first_name']
                u3 = " " + message.reply_to_message["from"]["last_name"] if \
                    message.reply_to_message["from"][
                        "last_name"] else ""
                u4 = (str(u2) + str(u3))
                user = hlink(u4, "tg://user?id=" + str(user_name))
                tag_user1 = message.reply_to_message['from']['id']
                tag_admin = await bot.get_chat_member(message.chat.id,
                                                      message.reply_to_message['from']['id'])

                if db.check_tasks(tag_user1, message.chat['id']):
                    await message.reply("Можно выдать не более пяти поручений.")
                else:
                    if tag_admin.is_chat_admin():
                        await message.reply("Нельзя выдать поручение администратору.")

                    elif not arguments:
                        await message.reply("Вы не назаначили поручение.")

                    elif len(arguments) < 6:
                        await message.reply(
                            "Слишком коротко. Выдайте поручение длинее пяти символов.")

                    elif tag_user1 == from_id1:
                        await message.reply("Нельзя выдать поручение самому себе.")

                    else:
                        db.add_tag(tag_user1, arguments, from_id1, chat_id)
                        await message.reply(
                            "Поручение выдано для {0}".format(user) + ": " + "\n" + hbold(arguments),
                            parse_mode="HTML")

        else:
            text = ""
            if db.get_tasks(message['from']['id'], message.chat['id']):
                for i in range(len(db.get_tasks(message['from']['id'], message.chat['id']))):
                    text += f"├ {i + 1}. {hbold(db.get_tasks(message['from']['id'], message.chat['id'])[i][2])}\n"
                await message.reply(f"│ Ваши поручения:\n{text}", parse_mode="HTML")

            else:
                await message.reply("У вас нет поручений.")


@dp.message_handler(commands="tagsdel")
async def deltask(message: types.Message):
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
                db.user_del(task[0])
                await message.reply(f"Было удалено поручение: {task[2]}")
        else:
            await message.reply("У вас недостаточно прав.")


button = InlineKeyboardMarkup(row_width=1)
button_on = InlineKeyboardButton(text='Включить', callback_data='button1')
button_off = InlineKeyboardButton(text='Отключить', callback_data='button2')
button_filter = InlineKeyboardButton(text='Дополнить список', callback_data='button3')
delete_button = InlineKeyboardButton(text='Очистить список', callback_data='button4')
button.add(button_on, button_off, button_filter, delete_button)


@dp.message_handler(commands=['filter'])
async def filter_chat(message: types.Message):
    member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    state = dp.current_state(user=message.from_user.id)
    if message.chat.id != message.from_user.id:
        state = dp.current_state(user=message.from_user.id)
        if member.is_chat_admin():
            await message.answer("Хотите ли вы включить фильтрацию чата?", reply_markup=button)
            if db.check_filter(chat_id=message.chat.id):
                await state.reset_state(FilterWords.all()[0])
        else:
            await message.reply('У вас нет прав администратора для выполнения команды.', )


@dp.callback_query_handler(lambda c: c.data == 'button1', state='*')
async def process_callback_button1(callback_query: types.CallbackQuery):
    member = await bot.get_chat_member(callback_query.message.chat.id,
                                       callback_query.from_user.id)
    state = dp.current_state(user=callback_query.from_user.id)
    chat_id = callback_query.message.chat.id
    if member.is_chat_admin():
        if db.check_words(chat_id=chat_id):
            if db.check_filter(chat_id=chat_id):
                await bot.answer_callback_query(callback_query.id)
                await callback_query.bot.edit_message_text(text='Фильтрация чата уже включена.',
                                                           chat_id=callback_query.message.chat.id,
                                                           message_id=callback_query.message.message_id)
            else:
                await state.reset_state(FilterWords.all()[0])
                await bot.answer_callback_query(callback_query.id)
                await callback_query.bot.edit_message_text(text='Фильтрация чата включена.',
                                                           chat_id=callback_query.message.chat.id,
                                                           message_id=callback_query.message.message_id)
                db.filter_is_on(chat_id=callback_query.message.chat.id, filter_stats=1)
        elif db.check_filter(chat_id=chat_id):
            await bot.answer_callback_query(callback_query.id)
            await callback_query.bot.edit_message_text(text='Фильтрация чата уже включена.',
                                                       chat_id=callback_query.message.chat.id,
                                                       message_id=callback_query.message.message_id)
        else:
            await state.set_state(FilterWords.all()[0])
            await bot.answer_callback_query(callback_query.id)
            await callback_query.bot.edit_message_text(text='Укажите через запятую список'
                                                            ' запрещенных слов.\n'
                                                            'Пример: Слово1, Слово2',
                                                       chat_id=callback_query.message.chat.id,
                                                       message_id=callback_query.message.message_id)


@dp.message_handler(state=FilterWords.STATEWORD)
async def bad_words(message: types.Message):
    arguments = message.text
    if '/' in arguments:
        await message.reply('Нельзя добавить команду в список.')
    elif ", " in arguments:
        arguments = message.text.split(", ")
        state = dp.current_state(user=message.from_user.id)
        db.add_words(chat_id=message.chat.id, words=arguments)
        await message.reply('Фильтрация чата включена и слова добавлены в список запрещенных.')
        await state.reset_state(FilterWords.all()[0])
        db.filter_is_on(chat_id=message.chat.id, filter_stats=1)
    else:
        await message.reply('Вы неправильно указали слова.')


@dp.callback_query_handler(lambda c: c.data == 'button2')
async def process_callback_button1(callback_query: types.CallbackQuery):
    member = await bot.get_chat_member(callback_query.message.chat.id,
                                       callback_query.from_user.id)
    chat_id = callback_query.message.chat.id
    if member.is_chat_admin():
        if not db.check_filter(chat_id):
            await bot.answer_callback_query(callback_query.id)
            await callback_query.bot.edit_message_text(text='Фильтрация чата уже отключена.',
                                                       chat_id=callback_query.message.chat.id,
                                                       message_id=callback_query.message.message_id)
        else:
            db.filter_is_off(0)
            await bot.answer_callback_query(callback_query.id)
            await callback_query.bot.edit_message_text(text='Фильтрация чата отключена.',
                                                       chat_id=callback_query.message.chat.id,
                                                       message_id=callback_query.message.message_id)


@dp.callback_query_handler(lambda c: c.data == 'button3', state='*')
async def update_words_list(callback_query: types.CallbackQuery):
    member = await bot.get_chat_member(callback_query.message.chat.id,
                                       callback_query.from_user.id)
    state = dp.current_state(user=callback_query.from_user.id)
    chat_id = callback_query.message.chat.id
    if member.is_chat_admin():
        if db.check_filter(chat_id=chat_id):
            await bot.answer_callback_query(callback_query.id)
            await callback_query.bot.edit_message_text(text='Укажите через запятую слова для дополнения списка.\n'
                                                            'Пример: Слово1, Слово2',
                                                       chat_id=chat_id,
                                                       message_id=callback_query.message.message_id)
            await state.set_state(FilterWords.all()[1])
        else:
            await callback_query.bot.edit_message_text(text='Фильтрация в чате отключена. Включите её, чтобы дополнить '
                                                            'список слов.',
                                                       chat_id=chat_id,
                                                       message_id=callback_query.message.message_id)


@dp.message_handler(state=FilterWords.UPDATESTATEWORD)
async def bad_words_update(message: types.Message):
    arguments = message.text
    if '/' in arguments:
        await message.reply('Нельзя добавить команду в список.')
    elif ", " in arguments:
        k = set()
        arguments = message.text.split(", ")
        for i in arguments:
            k.add(i)
        if db.clone_words(chat_id=message.chat.id):
            state = dp.current_state(user=message.from_user.id)
            db.update_words(chat_id=message.chat.id, words=arguments)
            await message.reply('Слова добавлены в список.')
            await state.reset_state(FilterWords.all()[0])
        else:
            state = dp.current_state(user=message.from_user.id)
            db.update_words(chat_id=message.chat.id, words=k.union(db.clone_words(chat_id=message.chat.id)))
            await message.reply('Слова добавлены в список.')
            await state.reset_state(FilterWords.all()[0])

    else:
        await message.reply('Вы неправильно указали слова.')


@dp.callback_query_handler(lambda c: c.data == 'button4', state='*')
async def delete_words_from_list(callback_query: types.CallbackQuery):
    member = await bot.get_chat_member(callback_query.message.chat.id,
                                       callback_query.from_user.id)
    state = dp.current_state(user=callback_query.from_user.id)
    chat_id = callback_query.message.chat.id
    if member.is_chat_admin():
        if db.check_filter(chat_id=chat_id):
            db.delete_words(chat_id=chat_id)
            await bot.answer_callback_query(callback_query.id)
            await callback_query.bot.edit_message_text(text='Список слов был очищен.',
                                                       chat_id=chat_id,
                                                       message_id=callback_query.message.message_id)


@dp.message_handler()
async def catch_messages(message: types.Message):
    db.add_users(message['from']['id'], message.chat['id'])


if __name__ == '__main__':
    executor.start_polling(dp)
