import sqlite3
import time
import hashlib

DB_NAME = "anonbot.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    with open("schema.sql", "r") as f:
        cur.executescript(f.read())

    conn.commit()
    conn.close()

def register_user(chat_id, username):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT OR IGNORE INTO users (chat_id, username) VALUES (?, ?)",
        (chat_id, username)
    )
    conn.commit()
    conn.close()

def store_message(sender_chat_id, receiver_chat_id, content):
    sender_hash = hashlib.md5(str(sender_chat_id).encode()).hexdigest()
    ts = int(time.time())

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO messages (sender_hash, receiver_chat_id, content, timestamp) VALUES (?, ?, ?, ?)",
        (sender_hash, receiver_chat_id, content, ts)
    )
    conn.commit()
    conn.close()