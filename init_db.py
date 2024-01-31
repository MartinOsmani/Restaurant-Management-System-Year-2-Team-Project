import sqlite3

def init_db():
    with sqlite3.connect('users.db') as conn:
        with open('users.sql', 'r') as f:
            conn.executescript(f.read())
        
        with open('Orders.sql', 'r') as f:
            conn.executescript(f.read())

        with open('Order Items.sql', 'r') as f:
            conn.executescript(f.read())


if __name__ == '__main__':
    init_db()
    print("Database Created!")

