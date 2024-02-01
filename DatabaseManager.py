import sqlite3



class DatabaseManager:
    def __init__(self, database_name=":memory:"):
        self.db_connection = sqlite3.connect(database_name)
        self.db_cursor = self.db_connection.cursor()

    def create_user(self, full_name, username, password, role_id, email):
        self.db_cursor.execute("INSERT INTO users (name, username, password, role_id, email) VALUES (?, ?, ?, ?, ?)", (full_name, username, password, role_id, email))
        self.db_connection.commit()

    def create_order(self, order_date, customer_name, table_number, total, user_id):
         self.db_cursor.execute("INSERT INTO orders (order_date, email, table_number, total, user_id) VALUES (?, ?, ?, ?, ?)", (order_date, customer_name, table_number, total, user_id))
         self.db_connection.commit()

    def close(self):
        self.db_connection.close()



