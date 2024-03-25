import sqlite3
import os
from flask import current_app, g
import click


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def init_db(db_name='database.db'):
    db = get_db()
    sql_dir = os.path.join(os.path.dirname(__file__), 'database')
    sql_files = ['users.sql', 'Orders.sql', 'Order Items.sql', 'Menu Items.sql']

    for file_name in sql_files:
        file_path = os.path.join(sql_dir, file_name)
        with open(file_path, 'r') as f:
            db.executescript(f.read())



def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

