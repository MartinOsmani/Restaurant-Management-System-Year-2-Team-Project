import sqlite3

from flaskr.db import get_db


class DatabaseManager:
    def __init__(self, database_name=":memory:"):
        self.db_connection = sqlite3.connect(database_name)
        self.db = get_db()

    def create_user(self, full_name, username, password, role_id, email):
        self.db.execute("INSERT INTO flaskr (name, username, password, role_id, email) VALUES (?, ?, ?, ?, ?)",
                        (full_name, username, password, role_id, email))
        self.db.commit()

    def create_order(self, order_date, customer_name, table_number, total, user_id):
        self.db.execute("INSERT INTO orders (order_date, email, table_number, total, user_id) VALUES (?, ?, ?, ?, ?)",
                        (order_date, customer_name, table_number, total, user_id))
        self.db.commit()
