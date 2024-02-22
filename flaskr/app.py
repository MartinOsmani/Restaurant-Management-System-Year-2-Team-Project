from flask import Flask, render_template, session, redirect
from flaskr.auth import bp as auth_bp
from flaskr.db import init_db
from flaskr.DatabaseManager import DatabaseManager
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['DATABASE'] = 'database.db'

db_manager = DatabaseManager()

with app.app_context():
    init_db()
    db_manager.insert_test_data_for_menu()

# Register the auth blueprint
app.register_blueprint(auth_bp)

@app.route('/')
def index():
    user_id = session.get('user_id')
    if user_id is None:
        return redirect('/auth/register')
    if DatabaseManager.get_role_id(user_id) == 2:
        return render_template('waiter.html')
    elif DatabaseManager.get_role_id(user_id) == 3:
        return render_template('kitchen_staff.html')
    elif DatabaseManager.get_role_id(user_id) == 4:
        return render_template('manager.html')
    elif DatabaseManager.get_role_id(user_id) == 1:
        return render_template('home.html')

@app.route('/menu')
def menu():
    menu_items = db_manager.get_all_menu_items()
    return render_template('menu.html', menu_items=menu_items)

@app.route('/book')
def book():
    return render_template('book.html')

if __name__ == '__main__':
    app.run(debug=True)
