import sqlite3


class DataBase:
    def __init__(self, name_db):
        self.con = sqlite3.connect(name_db)
        self.cur = self.con.cursor()

        self.cur.execute("""CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            admin_id INTEGER)""")

        self.cur.execute("""CREATE TABLE IF NOT EXISTS bad_words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            word TEXT)""")

        self.cur.execute("""CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            filter_state INTEGER DEFAULT 0)""")

        self.cur.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            chat_id INTEGER)""")

        self.cur.execute("""CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            chat_id INTEGER,
            task TEXT,
            admin_id INTEGER)""")

        self.con.commit()

    def add_task(self, user_id, task, admin_id, chat_id):
        self.cur.execute("INSERT INTO tasks (user_id, chat_id, task, admin_id) VALUES (?, ?, ?, ?)",
                         (user_id, chat_id, task, admin_id))
        self.con.commit()

    def get_tasks(self, user_id, chat_id):
        self.cur.execute(f"SELECT * FROM tasks WHERE user_id = ? AND chat_id = ?",
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

    def task_delete(self, id):
        self.cur.execute(f"DELETE FROM tasks WHERE id = ?", (id,))
        self.con.commit()

    def change_filter(self, chat_id):
        self.cur.execute(f"SELECT filter_state FROM chats WHERE chat_id = ?", (chat_id,))
        chat = self.cur.fetchone()
        if chat:
            status = 1 if not chat[0] else 0
            self.cur.execute(f'UPDATE chats SET filter_state = ?', (status,))
            self.con.commit()
            return status
        else:
            self.cur.execute('INSERT INTO chats (chat_id) VALUES (?)', (chat_id,))
            self.con.commit()

    def check_filter(self, chat_id):
        self.cur.execute(f"SELECT filter_state FROM chats WHERE chat_id = ?", (chat_id,))
        status = self.cur.fetchone()
        if status:
            return status[0]

    def add_words(self, chat_id, words):
        for i in words:
            self.cur.execute('SELECT * FROM bad_words WHERE word = ? AND chat_id = ?', (i, chat_id))
            words_db = self.cur.fetchone()
            if not words_db:
                self.cur.execute('INSERT INTO chats (chat_id, word) VALUES (?, ?)', (chat_id, i))
                self.con.commit()

    def delete_words(self, chat_id):
        self.cur.execute('SELECT * FROM bad_words WHERE chat_id = ?', (chat_id,))
        words = self.cur.fetchall()
        for _ in words:
            self.cur.execute(f"DELETE FROM bad_words WHERE chat_id = ?", (chat_id,))
            self.con.commit()

    def get_words_by_chat(self, chat_id):
        self.cur.execute('SELECT word FROM bad_words WHERE chat_id = ?', (chat_id,))
        words = self.cur.fetchall()
        return [word[0] for word in words]

    def add_admins(self, chat_id, admin_id):
        self.cur.execute('SELECT * FROM chat_ids WHERE admin_id = ?', (admin_id,))
        admin = self.cur.fetchall()
        if not admin:
            self.cur.execute('INSERT INTO chat_ids VALUES (?, ?)', (chat_id, admin_id))
            self.con.commit()
