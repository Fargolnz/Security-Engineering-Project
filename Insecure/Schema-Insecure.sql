CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER UNIQUE,
    username TEXT
);

CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_hash TEXT,
    receiver_chat_id INTEGER,
    content TEXT,
    timestamp INTEGER
);