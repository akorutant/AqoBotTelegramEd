import sqlite3


class DataBase:
    def __init__(self, name_db):
        self.con = sqlite3.connect(name_db)
        self.cur = self.con.cursor()

        self.cur.execute("""CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            admin_id INTEGER,
            chat_title TEXT)""")

        self.cur.execute("""CREATE TABLE IF NOT EXISTS bad_words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            word TEXT)""")

        self.cur.execute("""CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            chat_title TEXT,
            filter_state INTEGER DEFAULT 0)""")

        self.cur.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            user_id INTEGER
            )""")

        self.cur.execute("""CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            chat_id INTEGER,
            chat_title TEXT,
            task TEXT,
            admin_id INTEGER)""")

        self.con.commit()

    def add_task(self, user_id, chat_id, chat_title, task, admin_id):
        self.cur.execute("INSERT INTO tasks (user_id, chat_id, chat_title, task, admin_id) "
                         "VALUES (?, ?, ?, ?, ?)",
                         (user_id, chat_id, chat_title, task, admin_id))
        self.con.commit()

    def get_tasks(self, user_id, chat_id):
        self.cur.execute(f"SELECT id, task FROM tasks WHERE user_id = ? AND chat_id = ?",
                         (user_id, chat_id))

        return self.cur.fetchall()

    def check_tasks(self, user_id, chat_id):
        q = self.get_tasks(user_id, chat_id)
        return len(q) >= 5

    def add_user(self, chat_id, user_id):
        self.cur.execute('SELECT user_id FROM users WHERE chat_id = ? AND user_id = ?',
                         (chat_id, user_id))
        user = self.cur.fetchone()
        if not user:
            self.cur.execute('INSERT INTO users (chat_id, user_id) VALUES (?, ?)',
                             (chat_id, user_id))
            self.con.commit()

    def get_users_by_chat_id(self, chat_id):
        self.cur.execute(f"SELECT user_id FROM users WHERE chat_id = ?", (chat_id,))
        users = self.cur.fetchall()
        return [user[0] for user in users]

    def task_delete(self, task_id):
        self.cur.execute(f"DELETE FROM tasks WHERE id = ?", (task_id,))
        self.con.commit()

    def change_filter(self, chat_id, chat_title):
        self.cur.execute(f"SELECT filter_state FROM chats WHERE chat_id = ?", (chat_id,))
        chat = self.cur.fetchone()
        if chat:
            status = 1 if not chat[0] else 0
            self.cur.execute(f'UPDATE chats SET filter_state = ? WHERE chat_id = ? '
                             f'AND chat_title = ?', (status, chat_id, chat_title))
            self.con.commit()
            return status
        else:
            self.cur.execute('INSERT INTO chats (chat_id, chat_title) VALUES (?, ?)',
                             (chat_id, chat_title))
            self.con.commit()

    def check_filter(self, chat_id):
        self.cur.execute(f"SELECT filter_state FROM chats WHERE chat_id = ?", (chat_id,))
        status = self.cur.fetchone()
        if status:
            return status[0]

    def add_words(self, chat_id, word):
        self.cur.execute('SELECT * FROM bad_words WHERE word = ? AND chat_id = ?', (word, chat_id))
        words_db = self.cur.fetchone()

        if not words_db:
            self.cur.execute('INSERT INTO bad_words (chat_id, word) VALUES (?, ?)', (chat_id, word))
            self.con.commit()
        else:
            return True

    def delete_words(self, chat_id):
        self.cur.execute('SELECT * FROM bad_words WHERE chat_id = ?', (chat_id,))
        words = self.cur.fetchall()
        if words:
            self.cur.execute(f"DELETE FROM bad_words WHERE chat_id = ?", (chat_id,))
            self.con.commit()

    def get_words_by_chat(self, chat_id):
        self.cur.execute('SELECT word FROM bad_words WHERE chat_id = ?', (chat_id,))
        words = self.cur.fetchall()
        return [word[0] for word in words]

    def add_admins(self, chat_id, admin_id, chat_title):
        self.cur.execute('SELECT admin_id FROM admins WHERE chat_id = ? AND admin_id = ?',
                         (chat_id, admin_id))

        admin = self.cur.fetchone()
        if not admin:
            self.cur.execute('INSERT INTO admins (chat_id, admin_id, chat_title) VALUES (?, ?, ?)',
                             (chat_id, admin_id, chat_title))
            self.con.commit()

    def get_admin_id(self, admin_id):
        self.cur.execute('SELECT admin_id, chat_id FROM admins WHERE admin_id = ?',
                         (admin_id,))
        admin_info = self.cur.fetchone()
        if admin_info:
            return admin_info

    def get_chat_id_by_user_id(self, user_id):
        self.cur.execute('SELECT chat_id FROM users WHERE user_id = ?', (user_id,))
        chat = self.cur.fetchone()
        if chat:
            return chat

    def get_chat_titles_by_admin_id(self, admin_id):
        self.cur.execute('SELECT chat_title FROM admins WHERE admin_id = ?', (admin_id,))
        chat_titles = self.cur.fetchall()
        if chat_titles:
            return [chat_title[0] for chat_title in chat_titles]

    def get_chat_id_by_chat_title(self, chat_title):
        self.cur.execute('SELECT chat_id FROM admins WHERE chat_title = ?', (chat_title,))
        chat = self.cur.fetchone()
        if chat:
            return chat

    def add_chat_info(self, chat_id, chat_title):
        self.cur.execute('SELECT chat_id FROM chats WHERE chat_id = ?', (chat_id,))
        chat_info = self.cur.fetchone()
        if not chat_info:
            self.cur.execute('INSERT INTO chats (chat_id, chat_title) VALUES (?, ?)',
                             (chat_id, chat_title))
            self.con.commit()

    def get_user(self, user_id):
        self.cur.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
        user = self.cur.fetchone()
        if user:
            return user

    def get_admin_id_from_tasks(self, task):
        self.cur.execute('SELECT admin_id FROM tasks WHERE task = ?', (task,))
        admin_id = self.cur.fetchone()
        if admin_id:
            return admin_id

    def get_chats_ids_by_user_id(self, user_id):
        self.cur.execute('SELECT chat_id FROM users WHERE user_id = ?', (user_id,))
        chats_ids = self.cur.fetchall()
        if chats_ids:
            return [chat_id[0] for chat_id in chats_ids]

    def get_chat_titles_by_chat_id(self, chat_id):
        self.cur.execute('SELECT chat_title FROM chats WHERE chat_id = ?', (chat_id,))
        chat_titles = self.cur.fetchall()
        if chat_titles:
            return [chat_title[0] for chat_title in chat_titles]

    def get_chat_title_by_chat_id(self, chat_id):
        self.cur.execute('SELECT chat_title FROM chats WHERE chat_id = ?', (chat_id,))
        chat_title = self.cur.fetchone()
        if chat_title:
            return chat_title
