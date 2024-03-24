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
        #convert the datetime object to a string to compare data
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




