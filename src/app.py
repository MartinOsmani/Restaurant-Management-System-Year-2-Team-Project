from flask import Flask, render_template, session, request, g, jsonify, redirect, url_for
from src.auth import bp as auth_bp
from src.auth import login_required
import random, json
from datetime import datetime
from db import init_db
from werkzeug.utils import secure_filename
from database_manager import DatabaseManager
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['DATABASE'] = 'database.db'
app.config['UPLOAD_FOLDER'] = 'static/images'

db_manager = DatabaseManager()
template_mapping = {
    1: 'home.html',
    2: 'waiter.html',
    3: 'kitchen_staff.html',
    4: 'manager.html'
}

with app.app_context():
    init_db()
    db_manager.insert_test_data_for_menu()
    db_manager.create_manager_user()

# Register the auth blueprint
app.register_blueprint(auth_bp)

@app.route('/')
def index():
    if 'user_id' in session:
        user_id = session['user_id']
        role_id = db_manager.get_role_id(user_id)
        template = template_mapping.get(role_id, 'home.html')
        is_logged_in = True
    else:
        template = 'home.html'
        is_logged_in = False

    # Assuming your templates can handle a context variable to check login status
    return render_template(template, is_logged_in=is_logged_in)

@app.route('/menu')
def menu():
    menu_items = db_manager.get_all_menu_items()
    is_logged_in = 'user_id' in session
    return render_template('menu.html', menu_items=menu_items, is_logged_in=is_logged_in)

@app.route('/call-waiter')
def call_waiter():

    user_id = session.get('user.id')

    if user_id != None:
        db_manager.change_needs_waiter(user_id)

    role_id = DatabaseManager.get_role_id(user_id)
    template = template_mapping.get(role_id, 'home.html')

    return render_template(template)

# Route to view all orders.
@app.route('/view-orders')
def show_orders():
    orders = db_manager.get_all_orders()
    return render_template('orders.html', orders=orders)

# Function to change order status for waiters.
@app.route('/update-status/<int:order_id>', methods=['POST'])
def update_order_status(order_id):
    new_status = request.form['status']
    db_manager.update_order(order_id, new_status)
    return redirect(url_for('show_orders'))


# Function to delete an order from the orders page` for waiters.
@app.route('/delete-order/<int:order_id>', methods=['POST'])
@login_required
def delete_order(order_id):
    db_manager.delete_order(order_id)
    return redirect(url_for('show_orders'))

@app.route('/update-menu', methods=['GET', 'POST'])
@login_required
def update_menu():
    menu_items = db_manager.get_all_menu_items()
    if request.method == 'POST':
        selected_menu_item_id = request.form.get('menu_item')
        new_name = request.form.get('name')
        new_description = request.form.get('description')
        new_price = request.form.get('price')
        new_ingredients = request.form.get('ingredients')
        new_calorie = request.form.get('calorie')
        new_category = request.form.get('category')

        new_image_url = None
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':
                filename = secure_filename(file.filename)
                file_path = os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                new_image_url = f'static/images/{filename}'

        db_manager.update_menu_item(selected_menu_item_id, new_name, new_description, new_price, new_ingredients,
                                    new_calorie, new_image_url, new_category)

        menu_items = db_manager.get_all_menu_items()
        return render_template('menu.html', menu_items=menu_items)

    return render_template('update_menu.html', menu_items=menu_items)

@app.route('/create-menu-item', methods=['GET', 'POST'])
@login_required
def create_menu_item():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price')
        ingredients = request.form.get('ingredients')
        calorie = request.form.get('calorie')
        category = request.form.get('category')

        image_url = None
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':
                filename = secure_filename(file.filename)
                file_path = os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                image_url = f'static/images/{filename}'

        db_manager.create_menu_item(name, description, price, ingredients, calorie, image_url, category)
        return redirect(url_for('menu'))

    return render_template('create_menu_item.html')


@app.route('/create-order', methods=['POST'])
@login_required
def create_order():
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

@app.route('/order-confirmation')
@login_required
def order_confirmation():
    return render_template('order_confirmation.html')


@app.route('/my-orders')
@login_required
def my_orders():
    if 'user_id' in session:
        user_id = session['user_id']
        orders = db_manager.get_user_orders(user_id)
        return render_template('my_orders.html', orders=orders)
    else:
        return redirect(url_for('login'))


@app.route('/checkout')
def checkout():
    return render_template('checkout.html')

@app.route('/manage-users', methods=["POST", "GET"])
@login_required
def manager_users():
    user_id = session.get('user_id')

    role_id = db_manager.get_role_id(user_id)
    if role_id == 4:
        users = db_manager.get_all_users()
    else:
        return render_template('404.html'), 404


    if request.method == "POST":
        data = request.get_json()
        action = data.get('action', '')
        user_id = data.get('user_id', '')
        if action == 'delete':
            try:
                db_manager.delete_user(user_id)
                return jsonify({"message": "User deleted successfully", "user_id": user_id}), 200
            except Exception as e:
                return jsonify({"error": "An error occurred while deleting the user"}), 500
        elif action == 'change-role':
            new_role_id = data.get('role_id', '')
            try:
                db_manager.update_user_role(user_id, new_role_id)
                return jsonify({"message": "User role updated successfully", "user_id": user_id}), 200
            except Exception as e:
                return jsonify({"error": "An error occurred while updating the user's role"}), 500

        return jsonify({"error": "Invalid action"}), 400

    return render_template('manage_users.html', users=users)



if __name__ == '__main__':
    app.run(debug=True)
