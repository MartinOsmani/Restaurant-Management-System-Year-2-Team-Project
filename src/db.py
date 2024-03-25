import sqlite3
import os
from flask import current_app, g
import click


def get_db():
    """
    Creates a database connection using the database path from Flask's 'current_app' config.
    Accesses SQlite query results by column name.

    Returns:
        A sqlite3 database connection object.
    """
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def init_db(db_name='database.db'):
    """
    Initializes the database by creating tables according to the schema files from
    'database' directory relative to its location.

    Parameters:
        db_name (str): The name of the database file. Default is 'database.db'
    """
    db = get_db()
    sql_dir = os.path.join(os.path.dirname(__file__), 'database')
    sql_files = ['users.sql', 'Orders.sql', 'Order Items.sql', 'Menu Items.sql']

    for file_name in sql_files:
        file_path = os.path.join(sql_dir, file_name)
        with open(file_path, 'r') as f:
            db.executescript(f.read())



def close_db(e=None):
    """
    Closes database connection.

    Parameters:
        e (Exception, optional): An error instance, default to None.
    """
    db = g.pop('db', None)

    if db is not None:
        db.close()

@click.command('init-db')
def init_db_command():
    """
    Command to clear existing data and create new tables in the database.
    """
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    """
    Registers database-related functions with the Flask application

    Parameters:
        app (Flask): The Flask application instance.
    """
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

