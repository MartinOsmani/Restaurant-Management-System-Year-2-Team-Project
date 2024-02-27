from flask import Flask, render_template, session, request, jsonify
from flaskr.auth import bp as auth_bp, login_required

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
@login_required
def index():
    user_id = session.get('user_id')

    role_id = DatabaseManager.get_role_id(user_id)
    template_mapping = {
        1: 'home.html',
        2: 'waiter.html',
        3: 'kitchen_staff.html',
        4: 'manager.html'
    }
    template = template_mapping.get(role_id, 'home.html')

    return render_template(template)

@app.route('/menu')
def menu():
    menu_items = db_manager.get_all_menu_items()
    return render_template('menu.html', menu_items=menu_items)

@app.route('/checkout', methods=['POST'])
def checkout():
    data = request.get_json()
    return jsonify({"status": "success", "message": "Order processed successfully."})


@app.route('/book')
def book():
    return render_template('book.html')

if __name__ == '__main__':
    app.run(debug=True)
