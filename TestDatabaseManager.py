import sqlite3
import pytest
from flaskr.DatabaseManager import DatabaseManager
from flaskr.db import init_db
import os

@pytest.fixture
def db_manager():
    if os.path.exists("TestDatabaseManager.db"):
        os.remove("TestDatabaseManager.db")
    init_db("TestDatabaseManager.db")
    manager = DatabaseManager("TestDatabaseManager.db")    
    return manager

def test_create_user(db_manager):
    user_data = ("John Pork", "johnpork", "password123", 1, "johnpork@cia.gov")
    db_manager.create_user(*user_data)

    db_manager.db_cursor.execute("SELECT * FROM flaskr WHERE username = 'johnpork'")
    user = db_manager.db_cursor.fetchone()
    

    assert user is not None
    assert user[1] == "John Pork" 
    assert user[2] == "johnpork" 
    assert user[3] == "password123" 
    assert user[4] == 1  
    assert user[5] == "johnpork@cia.gov"

    db_manager.db_connection.close()


def test_create_duplicate_user(db_manager):
    user_data = ("John Pork", "johnpork", "password123", 1, "johnpork@cia.gov")

    db_manager.create_user(*user_data)

    with pytest.raises(sqlite3.IntegrityError):
        db_manager.create_user(*user_data)

def test_create_order(db_manager):
    order_data = ("2024-01-01 00:00:00", "johnpork@cia.gov", 1, 50.00, 1)
    db_manager.create_order(*order_data)

    db_manager.db_cursor.execute("SELECT * FROM orders WHERE email = 'johnpork@cia.gov'")
    order = db_manager.db_cursor.fetchone()

    assert order is not None
    assert order[1] == "2024-01-01 00:00:00"
    assert order[2] == "johnpork@cia.gov"
    assert order[3] == 1 #table number
    assert order[4] == 50.00
    assert order[5] == 1 #user id

    db_manager.db_connection.close()

def test_get_all_menu_items(db_manager):
    menu_items_data = [
        ("Dish1", "Description1", 10.99, "Ingredient1", 200),
        ("Dish2", "Description2", 11.99, "Ingredient2", 300),
        ("Dish3", "Description3", 12.99, "Ingredient3", 400),
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

    db_manager.db_connection.close()
