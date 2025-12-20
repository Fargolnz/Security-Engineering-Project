import sqlite3
import hashlib

conn = sqlite3.connect("anonbot.db")
cur = conn.cursor()

cur.execute("SELECT id, sender_hash, timestamp FROM messages")
messages = cur.fetchall()

cur.execute("SELECT chat_id, username FROM users")
users = cur.fetchall()

for msg_id, sender_hash, ts in messages:
    print(f"\n🔍 Message {msg_id} | timestamp={ts}")

    for chat_id, username in users:
        guess = hashlib.md5(str(chat_id).encode()).hexdigest()
        if guess == sender_hash:
            print(f"❗ Possible sender: {username} (chat_id={chat_id})")

conn.close()