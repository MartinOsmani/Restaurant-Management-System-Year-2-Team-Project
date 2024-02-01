import sqlite3
import pytest
from DatabaseManager import DatabaseManager
from InitDatabase import init_db
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

    db_manager.db_cursor.execute("SELECT * FROM users WHERE username = 'johnpork'")
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

