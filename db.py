import sqlite3
import json
import random

con = sqlite3.connect('work.sqlite')
cur = con.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      tag_user INTEGER,
      tag TEXT,
      from_id INTEGER,
      chat_id INTEGER
      )""")

cur.execute("""CREATE TABLE IF NOT EXISTS users1 (
      chat_id INTEGER,
      users
      )""")

cur.execute("""CREATE TABLE IF NOT EXISTS filters (
    chat_id INTEGER,
    filter_stats INTEGER
    )""")

cur.execute("""CREATE TABLE IF NOT EXISTS words (
    chat_id INTEGER,
    ban_words TEXT
    )""")


def add_tag(tag_user, tag, from_id, chat_id):
    q = "INSERT INTO users VALUES (?, ?, ?, ?, ?)"
    cur.execute(q, (None, tag_user, tag, from_id, chat_id))
    con.commit()


def get_tasks(user_id, chat_id):
    cur.execute(f"SELECT * FROM users WHERE tag_user = ? AND chat_id = ?", (user_id, chat_id))
    return cur.fetchall()


def check_tasks(user_id, chat_id):
    q = get_tasks(user_id, chat_id)
    return len(q) >= 5


def add_users(user_id, chat_id):
    cur.execute(f"SELECT * FROM users1 WHERE chat_id = ?", (chat_id,))
    check = cur.fetchall()
    if not check:
        cur.execute(f"INSERT INTO users1 VALUES (?, ?)", (chat_id, json.dumps([user_id])))

    else:
        cur.execute(f"SELECT users FROM users1 WHERE chat_id = ?", (chat_id,))
        r = json.loads(cur.fetchone()[0])
        if not user_id in r:
            r.append(user_id)
            cur.execute("UPDATE users1 SET users = ? WHERE chat_id = ?", (json.dumps(r), chat_id,))
    con.commit()


def get_users(chat_id):
    cur.execute(f"SELECT users FROM users1 WHERE chat_id = ?", (chat_id,))
    r = json.loads(cur.fetchone()[0])
    return r


def user_del(id):
    cur.execute(f"DELETE FROM users WHERE id = ?", (id,))
    con.commit()


def filter_is_on(chat_id, filter_stats):
    cur.execute(f"SELECT * FROM filters WHERE chat_id = ?", (chat_id,))
    sss = cur.fetchall()
    if not sss:
        cur.execute(f"INSERT INTO filters VALUES (?, ?)", (chat_id, filter_stats))
        con.commit()
    else:
        cur.execute(f'UPDATE filters SET filter_stats = ?', (filter_stats,))
        con.commit()


def filter_is_off(filter_stats):
    cur.execute(f'UPDATE filters SET filter_stats = ?', (filter_stats,))
    con.commit()


def check_filter(chat_id):
    cur.execute(f"SELECT * FROM filters WHERE chat_id = ?", (chat_id,))
    sss = cur.fetchone()
    if not sss:
        return False
    else:
        return int(sss[1])


def check_words(chat_id):
    cur.execute('SELECT * FROM words WHERE chat_id = ?', (chat_id,))
    sss = cur.fetchone()
    if not sss:
        return False
    else:
        return int(sss[0])


def add_words(chat_id, words):
    cur.execute("SELECT * FROM words WHERE chat_id = ? ", (chat_id,))
    sss = cur.fetchall()

    if not sss:
        ss = ' '.join(words)
        cur.execute("INSERT INTO words VALUES (?, ?)", (chat_id, ss))
        con.commit()


def update_words(chat_id, words):
    cur.execute('SELECT * FROM words WHERE chat_id = ?', (chat_id,))
    ss = cur.fetchone()
    t = list()
    for i in words:
        t.append(i)
    sss = ' '.join(t)
    if not ss:
        cur.execute("INSERT INTO words VALUES (?, ?)", (chat_id, sss))
        con.commit()
    else:
        cur.execute('UPDATE words SET chat_id = ? AND ban_words = ?', (chat_id, sss))
        con.commit()


def clone_words(chat_id):
    cur.execute('SELECT * FROM words WHERE chat_id = ?', (chat_id,))
    ss = cur.fetchone()
    set1 = set()
    if not ss:
        return True
    else:
        ss1 = str(ss[1]).split()
        for i in ss1:
            set1.add(i)
        return set1


def delete_words(chat_id):
    cur.execute('SELECT * FROM words WHERE chat_id = ?', (chat_id,))
    ss = cur.fetchone()
    ss1 = ss[1]
    cur.execute(f"DELETE FROM words WHERE ban_words = ?", (ss1,))
    con.commit()



