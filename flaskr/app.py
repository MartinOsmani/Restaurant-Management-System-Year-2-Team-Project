from flask import Flask, render_template, session, request, g, jsonify
from flaskr.auth import bp as auth_bp
from flaskr.auth import login_required
import random, json
from datetime import datetime
from flaskr.db import init_db
from flaskr.DatabaseManager import DatabaseManager

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
@login_required
def menu():
    menu_items = db_manager.get_all_menu_items()
    return render_template('menu.html', menu_items=menu_items)


@app.route('/createOrder', methods=['POST'])
@login_required
def checkout():
    data = request.get_json()
    current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    table_number = random.randint(1, 20)
    menu_items = db_manager.get_all_menu_items()
    menu_items_dict = {item['menu_item_name']: item['menu_item_price'] for item in menu_items}

    total_price = 0

    for item in data:
        name = item["name"]
        quantity = item["quantity"]

        if name in menu_items_dict:
            price = menu_items_dict[name]
            total_price += price * quantity
        else:
            print(f"Warning: Item '{name}' not found in the menu.")

    db_manager.create_order(current_date, g.user['email'], table_number, total_price, g.user['user_id'])
    return jsonify({"status": "success", "message": "Order processed successfully."})


@app.route('/order_confirmation')
@login_required
def order_confirmation():
    return render_template('order_confirmation.html')

@app.route('/book')
@login_required
def book():
    return render_template('book.html')

if __name__ == '__main__':
    app.run(debug=True)
