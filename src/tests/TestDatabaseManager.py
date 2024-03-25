import pytest
import sqlite3
from flask import Flask, g
from src.database_manager import DatabaseManager
from src.db import init_db, get_db
from datetime import datetime


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['DATABASE'] = 'database.db'
    return app


@pytest.fixture
def db_manager(app):
    with app.app_context():
        init_db("database.db")
        manager = DatabaseManager("database.db")
    return manager

@pytest.fixture(scope="function")
def setup_user_data(db_manager, app):
    with app.app_context():
        user_data = [("John Dan", "johndan", "password123", 1, "johndan@email.com"),
                     ("Harry Potter", "harrypotter", "password321", 2, "hp@email.com")]
        for user in user_data:
            db_manager.create_user(*user)
        menu_items_data = [
            ("Dish1", "Description1", 10.99, "Ingredient1", 200, "static/images/testFood.jpg", "category1"),
            ("Dish2", "Description2", 11.99, "Ingredient2", 300, "static/images/testFood.jpg", "category2"),
            ("Dish3", "Description3", 12.99, "Ingredient3", 400, "static/images/testFood.jpg", "category3"),
        ]
        for item in menu_items_data:
            db_manager.create_menu_item(*item)


def test_create_user(db_manager, app):
    with app.app_context():
        user_data = ("John Pork", "johnpork", "password123", 1, "johnpork@cia.gov")
        db_manager.create_user(*user_data)

        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username = 'johnpork'")
        user = cursor.fetchone()

        assert user is not None
        assert user[1] == "John Pork"
        assert user[2] == "johnpork"
        assert user[3] == "password123"
        assert user[4] == 1
        assert user[5] == "johnpork@cia.gov"


def test_create_duplicate_user(db_manager, app):
    with app.app_context():
        user_data = ("John Pork", "johnpork", "password123", 1, "johnpork@cia.gov")

        db_manager.create_user(*user_data)

        with pytest.raises(sqlite3.IntegrityError):
            with app.app_context():
                db_manager.create_user(*user_data)


def test_create_order(db_manager, app):
    with app.app_context():
        order_data = ("2024-01-01 00:00:00", "johnpork@cia.gov", 1, 50.00, 1)
        db_manager.create_order(*order_data)

        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM orders WHERE email = 'johnpork@cia.gov'")
        order = cursor.fetchone()

        assert order is not None
        # convert the datetime object to a string to compare data
        assert order[1].strftime('%Y-%m-%d %H:%M:%S') == '2024-01-01 00:00:00'
        assert order[2] == "johnpork@cia.gov"
        assert order[3] == 1  # table number
        assert order[4] == 50.00
        assert order[5] == 1  # user id


def test_create_menu_item(db_manager, app):
    with app.app_context():
        menu_item_data = ("Dish1", "Description1", 10.99, "Ingredient1", 200, "static/images/testFood.jpg", "category1")

        db_manager.create_menu_item(*menu_item_data)

        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM menu_items WHERE menu_item_name = 'Dish1'")
        created_menu_item = cursor.fetchone()

        assert created_menu_item is not None
        assert created_menu_item[1] == "Dish1"
        assert created_menu_item[2] == "Description1"
        assert created_menu_item[3] == 10.99
        assert created_menu_item[4] == "Ingredient1"
        assert created_menu_item[5] == 200


def test_get_all_menu_items(db_manager, app):
    with app.app_context():
        menu_items_data = [
            ("Dish1", "Description1", 10.99, "Ingredient1", 200, "static/images/testFood.jpg", "category1"),
            ("Dish2", "Description2", 11.99, "Ingredient2", 300, "static/images/testFood.jpg", "category2"),
            ("Dish3", "Description3", 12.99, "Ingredient3", 400, "static/images/testFood.jpg", "category3"),
        ]

        for item_data in menu_items_data:
            db_manager.create_menu_item(*item_data)

        menu_items = db_manager.get_all_menu_items()

        # Checks to see if the retrieved menu items match the expected values
        assert len(menu_items) == len(menu_items_data)

        for i, menu_item in enumerate(menu_items):
            assert menu_item[1] == menu_items_data[i][0]
            assert menu_item[2] == menu_items_data[i][1]
            assert menu_item[3] == menu_items_data[i][2]
            assert menu_item[4] == menu_items_data[i][3]
            assert menu_item[5] == menu_items_data[i][4]
            assert menu_item[6] == menu_items_data[i][5]
            assert menu_item[7] == menu_items_data[i][6]


def test_get_menu_item_by_id(db_manager, app):
    with app.app_context():
        db = get_db()
        cursor = db.cursor()

        # Get second menu item in database:
        cursor.execute("SELECT * FROM menu_items WHERE menu_item_id = ?", (2,))
        item = cursor.fetchone()

        # Get second menu item from menu_items by id:
        menu_item = db_manager.get_menu_item_by_id(1)
        assert menu_item == item, "Menu item by menu_item_id not retrieved!"


def test_get_all_orders(db_manager, app):
    with app.app_context():
        orders_data = [
            ("2024-01-01 00:00:00", "johndoe@email.com", 1, 20.0, 1),
            ("2024-01-01 00:00:00", "johndoe2@email.com", 2, 30.0, 2),
            ("2024-01-01 00:00:00", "johndoe@email.com", 1, 20.0, 1),
            ("2024-01-01 00:00:00", "johndoe@email.com", 1, 20.2, 4),
        ]
        for order_data in orders_data:
            db_manager.create_order(*order_data)

        all_orders = db_manager.get_all_orders()

        # Assert that we got the correct number of orders back
        assert len(all_orders) == len(orders_data)

        # Convert String dates in orders_data to datetime objects.
        orders_data_dates = [datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S') for date_str, _, _, _, _ in orders_data]

        for order in all_orders:
            assert order['order_date'] in orders_data_dates
            assert order['email'] in [od[1] for od in orders_data]
            assert order['table_number'] in [od[2] for od in orders_data]
            assert order['total'] in [od[3] for od in orders_data]
            assert order['user_id'] in [od[4] for od in orders_data]


def test_delete_order(db_manager, app):
    # Create an order in the database.
    with app.app_context():
        order_data = ("2024-01-01 00:00:00", "testuser@email.com", 1, 25.0, 1)
        db_manager.create_order(*order_data)
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT order_id FROM orders WHERE email = ?", (order_data[1],))
        order = cursor.fetchone()
        assert order is not None, "Order setup for delete test failed."

        # Delete the order by order_id.
        db_manager.delete_order(order[0])

        # Verify the order has been deleted.
        cursor.execute("SELECT * FROM orders WHERE order_id = ?", (order[0],))
        deleted_order = cursor.fetchone()
        assert deleted_order is None, "Order was not deleted."


def test_get_user_orders(db_manager, app):
    with app.app_context():
        # Create a test user:
        user_data = ("Test User", "testuser", "password123", 1, "testuser@email.com")
        db_manager.create_user(*user_data)

        # Get the id for that user:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT user_id FROM users WHERE username = 'testuser'")
        user = cursor.fetchone()
        user_id = user[0]

        # Insert orders from that user:
        orders_data = [
            ("2024-01-01 00:00:00", 1, 20.0, "Order confirmed!", user_id),
            ("2024-01-02 00:00:00", 1, 30.0, "The order has been delivered!", user_id),
        ]

        for order_date, table_number, total, order_status, user_id in orders_data:
            cursor.execute("INSERT INTO orders (order_date, table_number, total, order_status, user_id) VALUES (?, ?, ?, ?, ?)",
                           (order_date, table_number, total, order_status, user_id))
        db.commit()

        # Test the get_user_orders() function.
        retrieved_orders = db_manager.get_user_orders(user_id)

        # Convert String dates in orders_data to datetime objects:
        orders_data_dates = [datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S') for date_str, _, _, _, _ in orders_data]

        # Assert all orders have been retrieved correctly:
        assert len(retrieved_orders) == len(orders_data)

        for i, order in enumerate(retrieved_orders):
            assert order['order_date'] == orders_data_dates[i]
            assert order['total'] == orders_data[i][2]
            assert order['order_status'] == orders_data[i][3]

def test_update_menu_item(db_manager, app):
    with app.app_context():
        # Create a menu item:
        insert_data = ("Cake", "Delicious Cake", 10.00, "Cake ingridients", 100,
                       "http://original-url.com/image.jpg", "Desert")
        db = get_db()
        db.execute(
            "INSERT INTO menu_items (menu_item_name, menu_item_description, menu_item_price, menu_item_ingredients, menu_item_calorie, menu_item_image_url, menu_item_category) VALUES (?, ?, ?, ?, ?, ?, ?)",
            insert_data
        )
        db.commit()

        # Get the menu item id.
        menu_item_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]

        # Update menu item
        updated_data = (
        "Choco Cake", "Chocolate Cake ", 12.00, "Chocolate", 200, "http://updated-url.com/image.jpg",
        "Appetisers")
        db_manager.update_menu_item(menu_item_id, *updated_data)

        # Fetch updated item from database
        updated_item = db.execute("SELECT * FROM menu_items WHERE menu_item_id = ?", (menu_item_id,)).fetchone()

        # Assert that the changes have been made
        assert updated_item["menu_item_name"] == updated_data[0]
        assert updated_item["menu_item_description"] == updated_data[1]
        assert updated_item["menu_item_price"] == updated_data[2]
        assert updated_item["menu_item_ingredients"] == updated_data[3]
        assert updated_item["menu_item_calorie"] == updated_data[4]
        assert updated_item["menu_item_image_url"] == updated_data[5]
        assert updated_item["menu_item_category"] == updated_data[6]

def test_delete_user(db_manager, app, setup_user_data):
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (1,))
        user = cursor.fetchone()
        assert user is not None
        # Delete user by user_id
        db_manager.delete_user(1)

        # Verify that the second user has been deleted and only one remains.
        cursor.execute("SELECT COUNT(*) FROM users")
        remaining_users = cursor.fetchone()[0]
        assert remaining_users == 1, "User was not deleted!"

def test_update_user_role(db_manager, app, setup_user_data):
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        # Check current user id (i.e. customer)
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (1,))
        user = cursor.fetchone()
        assert user is not None
        # Update user by user_id from customer to waiter
        db_manager.update_user_role(1, 2)

        # Verify user_role has been updated
        cursor.execute("SELECT role_id FROM users WHERE user_id = ?", (1,))
        updated_user_role = cursor.fetchone()["role_id"]
        assert updated_user_role == 2, "User's role was not changed!"

def test_change_needs_waiter(db_manager, app, setup_user_data):
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        # Check current Boolean for needs_waiter is False:
        cursor.execute("SELECT needs_waiter FROM users WHERE user_id = ?", (1,))
        user = cursor.fetchone()
        assert user is not None
        # Change needs_waiter to True:
        db_manager.change_needs_waiter(1)

        # Verify needs_waiter has been set to True
        cursor.execute("SELECT needs_waiter FROM users WHERE user_id = ?", (1,))
        updated_needs_waiter = cursor.fetchone()["needs_waiter"]
        assert updated_needs_waiter == True, "User's needs_waiter has not been updated!"






