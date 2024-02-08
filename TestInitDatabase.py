from flaskr.db import init_db
import pytest
import sqlite3
import os


def check_table_exists(db_connection, table_name):
    cursor = db_connection.cursor()
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';")
    return cursor.fetchone() is not None

@pytest.fixture
def db_connection():
    os.system("rm test.db")
    init_db("test.db")
    connection = sqlite3.connect("test.db")
  
    yield connection

    connection.close()

def test_tables_exist(db_connection):
    assert check_table_exists(db_connection, "flaskr"), "The Table flaskr does not exist"
    assert check_table_exists(db_connection, "orders"), "The Table orders does not exist"
    assert check_table_exists(db_connection, "order_items"), "The Table order_items does not exist"
    assert check_table_exists(db_connection, "menu_items"), "The Table menu_items does not exist"

