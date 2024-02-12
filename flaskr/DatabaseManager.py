import sqlite3

from flaskr.db import get_db


class DatabaseManager:
    def __init__(self, database_name=":memory:"):
        self.db_connection = sqlite3.connect(database_name)
        self.db = get_db()

    @staticmethod
    def create_user(full_name, username, password, role_id, email):
        db = get_db()
        db.execute("INSERT INTO users (name, username, password, role_id, email) VALUES (?, ?, ?, ?, ?)",
                       (full_name, username, password, role_id, email))
        db.commit()

    @staticmethod
    def create_order(order_date, customer_name, table_number, total, user_id):
        db = get_db()
        db.execute(
                "INSERT INTO orders (order_date, customer_name, table_number, total, user_id) VALUES (?, ?, ?, ?, ?)",
                (order_date, customer_name, table_number, total, user_id))
        db.commit()

    def get_all_menu_items(self):
        self.db_cursor.execute("SELECT * FROM menu_items")
        menu_items = self.db_cursor.fetchall()
        return menu_items
    

