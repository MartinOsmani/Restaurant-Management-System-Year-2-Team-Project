import sqlite3
from flask import g, current_app
from flaskr.db import get_db


class DatabaseManager:
    def __init__(self, database_name=":memory:"):
        self.db_connection = sqlite3.connect(database_name)
        self.db = None

    def get_db(self):
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
        if self.db is not None:
            self.db.close()
            g.pop('db', None)

    @staticmethod
    def create_user(full_name, username, password, role_id, email):
        with get_db() as db:
            db.execute("INSERT INTO users (name, username, password, role_id, email) VALUES (?, ?, ?, ?, ?)",
                       (full_name, username, password, role_id, email))
            db.commit()

    @staticmethod
    def create_order(order_date, email, table_number, total, user_id):
        db = get_db()
        db.execute(
                "INSERT INTO orders (order_date, email, table_number, total, user_id) VALUES (?, ?, ?, ?, ?)",
                (order_date, email, table_number, total, user_id))
        db.commit()
    
    def create_menu_item(self, name, description, price, ingredients, calorie, image_url, category):
        db = get_db()
        db.execute(
            "INSERT INTO menu_items (menu_item_name, menu_item_description, menu_item_price, menu_item_ingredients, menu_item_calorie, menu_item_image_url, menu_item_category) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (name, description, price, ingredients, calorie, image_url, category)
        )
        db.commit()

    def get_all_menu_items(self):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM menu_items")
        menu_items = cursor.fetchall()
        return menu_items

    @staticmethod
    def get_role_id(user_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT role_id FROM users where user_id = ?", (user_id,))
        role_id = cursor.fetchone()
        if role_id is None:
            return 1;
        return role_id[0]

    def insert_test_data_for_menu(self):
        self.create_menu_item("Cheesy Fries", "Fries with cheese melted on top.", 6.99, "Potatoes, Mozeralla Cheese", 500, "static/images/testFood.jpg", "starter")
        self.create_menu_item("Curly Fries", "Potatoes sliced with a curly fry clutter.", 5.99, "Potatoes", 400, "static/images/testFood.jpg", "main")
        self.create_menu_item("Standard Cut Fries", "Potatoes evenly cut medium-thin.", 3.99, "Potatoes", 200, "static/images/testFood.jpg", "drink")

    def update_menu_item(self, menu_item_id, name, description, price, ingredients, calorie, image_url, category):
        db = get_db()
        db.execute(
            "UPDATE menu_items SET menu_item_name = ?, menu_item_description = ?, menu_item_price = ?, "
            "menu_item_ingredients = ?, menu_item_calorie = ?, menu_item_image_url = ?, menu_item_category = ? "
            "WHERE menu_item_id = ?",
            (name, description, price, ingredients, calorie, image_url, category, menu_item_id)
        )
        db.commit()

   
