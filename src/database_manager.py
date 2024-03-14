import sqlite3
from flask import g, current_app
from src.db import get_db


class DatabaseManager:
    """
    A class to manage database operations.

        Attributes:
            database_name (str): Name of the database file to connect to.
            db_connection (sqlite3.connection): A connenction object to the database.
             db (Sqlite3 Database): The SQLite3 database object. Initially None, set when `get_db` is called.


    """
    def __init__(self, database_name=":memory:"):
        """
        Setups the DatabaseManager with a connection to the SQLite database.

            Parameters:
                database_name (str): The name of the database file. Defaults to an in-memory database.

        """
        self.db_connection = sqlite3.connect(database_name)
        self.db = None

    def get_db(self):
        """
        Gets the database connection. If not already setup within the application, a new connection is created and stored.

            Returns:
                self.db (sqlite3.Database): The SQLite3 database object.

        """
        if 'db' not in g:
            app_context = current_app.app_context()
            app_context.push()
            self.db = sqlite3.connect(
                self.database_name,
                detect_types=sqlite3.PARSE_DECLTYPES
            )
            self.db.row_factory = sqlite3.Row

        return self.db
    
    def close_db(self):
        """
        Closes the database connection if it exists.
        """
        if self.db is not None:
            self.db.close()
            g.pop('db', None)

    @staticmethod
    def create_user(full_name, username, password, role_id, email):
        """
        Inserts a new user into the database.

            Parameters:
                full_name (str): The user's full name.
                username (str): The user's username.
                password (str): The user's hashed password.
                role_id (int): The user's rold ID.
                email (str): The user's email address.
        """
        with get_db() as db:
            db.execute("INSERT INTO users (name, username, password, role_id, email) VALUES (?, ?, ?, ?, ?)",
                       (full_name, username, password, role_id, email))
            db.commit()

    @staticmethod
    def create_order(order_date, email, table_number, total, user_id):
        """
        Inserts a new order into the database.

            Parameters:
                order_date (str): The date of the order.
                email (str): The email of the user placing the order.
                table_number (int): The table number associated with the order.
                total (float): The total cost of the order.
                user_id (int): The ID of the user who placed the order.

            Returns:
                order_id (int): The ID of the newly created order.
        """
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
                "INSERT INTO orders (order_date, email, table_number, total, user_id, order_status) VALUES (?, ?, ?, ?, ?, ?)",
                (order_date, email, table_number, total, user_id, 'Order confirmed!'))
        db.commit()
        order_id = cursor.lastrowid
        return order_id


    @staticmethod
    def insert_order_item(order_id, menu_item_id, quantity):
        """
        Inserts menu items in order.

            Parameter:
                order_id (int): The id of the order.
                menu_item_id (int): The id of menu item to insert.
                quantity (int): The quantity of the menu item.
        """
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
                "INSERT INTO order_items (order_id, menu_item_id, quantity) VALUES (?, ?, ?)", (order_id, menu_item_id, quantity))
        db.commit()

    @staticmethod
    def get_order_items(order_id):
        db = get_db()
        cursor = db.cursor()
        query = """
        SELECT mi.menu_item_name, oi.quantity
        FROM order_items oi
        JOIN menu_items mi ON oi.menu_item_id = mi.menu_item_id
        WHERE oi.order_id = ?
        """
        cursor.execute(query, (order_id,))
        items = cursor.fetchall()
        return items

    def create_menu_item(self, name, description, price, ingredients, calorie, image_url, category):
        """
        Inserts a new menu item into the database.

            Parameters:
                name (str): The name of the menu item.
                description (str): The description of the menu item.
                price (float): The price of the menu item.
                ingredients (str): The ingredients of the menu item.
                calorie (int): The calorie count of the menu item.
                image_url (str): The URL to the image of the menu item.
                category (str): The category of the menu item.
                """
        db = get_db()
        db.execute(
            "INSERT INTO menu_items (menu_item_name, menu_item_description, menu_item_price, menu_item_ingredients, menu_item_calorie, menu_item_image_url, menu_item_category) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (name, description, price, ingredients, calorie, image_url, category)
        )
        db.commit()


    def get_all_orders(self):
        """
        Retrieves all orders from the database.

            Returns:
                orders (list of sqlite3.Row): A list of all orders in the database.
        """
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM orders")
        orders = cursor.fetchall()
        return orders


    def delete_order(self, order_id):
        """
        Deletes an order from the database based on its order ID.

            Parameters:
                order_id (int): The ID of the order to delete.
        """
        db = get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM orders WHERE order_id = ?", (order_id,))
        db.commit()

    """
    Retrieves user's orders from the database.

        Returns:
            orders (list of sqlite3.Row): A list of all orders in the database.
    """
    @staticmethod
    def get_user_orders(user_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT order_id,order_date,total,order_status FROM orders WHERE user_id = ?", (user_id,))
        orders = cursor.fetchall()
        return orders

    @staticmethod
    def get_order(order_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT email,total,order_date FROM orders WHERE order_id = ?", (order_id,))
        order = cursor.fetchone()
        return order


    # Database call to update an order based on its order_id and selected order_status.
    def update_order(self, order_id, new_status):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("")
        cursor.execute('UPDATE orders SET order_status = ? WHERE order_id = ?', (new_status, order_id))
        db.commit()


    def delete_order(self, order_id):

        db = get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM orders WHERE order_id = ?", (order_id,))
        db.commit()


    @staticmethod
    def get_all_users():
        """
        Retrieves all users from the database.

            Returns:
                users (list of sqlite3.Row): A list of all users in the database.
        """
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT user_id, name, username, role_id, email FROM users")
        users = cursor.fetchall()
        return users


    def get_all_menu_items(self):
        """
        Retrieves all menu items from the database.

            Returns:
                menu_items (list of sqlite3.Row): A list of all menu items in the database.
        """
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM menu_items")
        menu_items = cursor.fetchall()
        return menu_items

    @staticmethod
    def get_role_id(user_id):
        """
        Retrieves the role ID for a given user ID.

            Parameters:
                user_id (int): The user's ID.

            Returns:
                role_id (int): The role ID of the user. Defaults to 1 if user not found.
        """
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT role_id FROM users where user_id = ?", (user_id,))
        role_id = cursor.fetchone()
        if role_id is None:
            return 1;
        return role_id[0]

    def create_manager_user(self):
        """
            Creates a manager user with predefined credentials and inserts it into the database.
        """
        password="$2b$12$fKgQuaBJa.Z48HvfWLQQoOL2PJZCjgf5JwW0Fflwhp9t6qvvVowqC" # Password123!
        self.create_user("John Doe", "manager", password, 4, "owner@email.com")

    def insert_test_data_for_menu(self):
        """
            Inserts predefined test data for menu items into the database.
        """
        self.create_menu_item("Cheesy Fries", "Fries with cheese melted on top.", 6.99, "Potatoes, Mozeralla Cheese", 500, "static/images/testFood.jpg", "starter")
        self.create_menu_item("Curly Fries", "Potatoes sliced with a curly fry clutter.", 5.99, "Potatoes", 400, "static/images/testFood.jpg", "main")
        self.create_menu_item("Standard Cut Fries", "Potatoes evenly cut medium-thin.", 3.99, "Potatoes", 200, "static/images/testFood.jpg", "drink")

    def update_menu_item(self, menu_item_id, name, description, price, ingredients, calorie, image_url, category):
        """
        Updates an existing menu item in the database based on its menu item ID.

            Parameters:
                menu_item_id (int): The ID of the menu item to update.
                name (str): The new name for the menu item.
                description (str): The new description of the menu item.
                price (float): The new price of the menu item.
                ingredients (str): The new ingredients of the menu item.
                calorie (int): The new calorie count of the menu item.
                image_url (str): The new URL to the image of the menu item.
                category (str): The new category of the menu item.
        """
        db = get_db()
        db.execute(
            "UPDATE menu_items SET menu_item_name = ?, menu_item_description = ?, menu_item_price = ?, "
            "menu_item_ingredients = ?, menu_item_calorie = ?, menu_item_image_url = ?, menu_item_category = ? "
            "WHERE menu_item_id = ?",
            (name, description, price, ingredients, calorie, image_url, category, menu_item_id)
        )
        db.commit()

    @staticmethod
    def delete_user(user_id):
        """
        Deletes a user from the database based on their user ID.

            Parameters:
                user_id (int): The ID of the user to delete.
        """
        db = get_db()
        db.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
        db.commit()

    @staticmethod
    def update_user_role(user_id, role_id):
        """
        Updates the role of an existing user in the database.

            Parameters:
                user_id (int): The ID of the user whose role is to be updated.
                role_id (int): The new role ID for the user.
        """
        db = get_db()
        db.execute('UPDATE users SET role_id = ? WHERE user_id = ?', (role_id, user_id,))
        db.commit()


    @staticmethod
    def change_needs_waiter(user_id):
        """
        Toggles the needs_waiter flag for a user in the database.

            Parameters:
                user_id (int): The ID of the user for whom to toggle the needs_waiter flag.
        """
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT needs_waiter FROM users where user_id = ?", (user_id,))
    
        needs_waiter = cursor.fetchone()
        db.execute('UPDATE users SET needs_waiter=? WHERE user_id=?', (needs_waiter, user_id))

        db.commit()

