DROP TABLE IF EXISTS users;


CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role_id INTEGER DEFAULT 1,
    email TEXT UNIQUE,
    needs_waiter BOOLEAN DEFAULT FALSE,
    tables_assigned INTEGER DEFAULT 0
);


