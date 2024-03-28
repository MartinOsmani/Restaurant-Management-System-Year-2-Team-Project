from flask import Flask, render_template, session, request, g, jsonify, redirect, url_for
from src.auth import bp as auth_bp
from src.auth import login_required
import random, json
from datetime import datetime
from src.db import init_db
from werkzeug.utils import secure_filename
from src.database_manager import DatabaseManager
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
    """
    Checks to see if a user is logged in by checking if 'user_id' is in the session.
    If a user is logged in, it retrieves their role_id from the database and 
    determines the template to render based on the role_id. Otherwise, 
    renders the default home template.
    
        Returns:
            str: The rendered index template.
    """
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
    """
    Retrieves all menu items from the database and checks to see if a user is logged in
    by checking if 'user_id' is in the session and then renders the menu page.

        Returns:
            str: The rendered menu template.
    """
    menu_items = db_manager.get_all_menu_items()
    is_logged_in = 'user_id' in session
    return render_template('menu.html', menu_items=menu_items, is_logged_in=is_logged_in)

@app.route('/call-waiter')
def call_waiter():
    """
    If a user is logged in, the function changes the 'needs_waiter' status 
    in the database for that user. Then, it determines the template to render 
    based on the user's role_id. If the user is not logged in, it renders the 
    default 'home.html' template.

        Returns:
            str: The rendered HTML template.
    """

    user_id = session.get('user_id')
    is_logged_in = 'user_id' in session

    if user_id != None: 
        db_manager.change_needs_waiter(user_id)

    role_id = DatabaseManager.get_role_id(user_id)
    template = template_mapping.get(role_id, 'home.html')

    return render_template(template, is_logged_in=is_logged_in)

@app.route('/view-orders')
def show_orders():
    """
    Route to view all orders.

    Retrieves the user's role ID from the session and checks if user is staff. If so, it fetches 
    all orders from the database and renders them using the 'orders.html' template. If the user
    is a customer, it redirects them to the '/my-orders' page.

        Returns:
            str/Response: The rendered HTML content of the orders page as staff or a redirects to page
            to view their orders as a customer.
    """
    user_id = session.get('user_id')
    role_id = db_manager.get_role_id(user_id)
    if role_id > 1:
        orders = db_manager.get_all_orders()
        return render_template('orders.html', orders=orders)
    else:
        return redirect('/my-orders', 302)

@app.route('/update-status/<int:order_id>', methods=['POST'])
def update_order_status(order_id):
    """
    Updates the status of a specific order as a waiter.

        Parameters:
            order_id (int): The ID of the order to be updated.

        Returns:
            Response: Redirects the user to 'show_orders' after updating the order status.
    """
    new_status = request.form['status']
    db_manager.update_order(order_id, new_status)
    return redirect(url_for('show_orders'))


# Function to delete an order from the orders page for waiters.
@app.route('/delete-order/<int:order_id>', methods=['POST'])
@login_required
def delete_order(order_id):
    """
    Deletes an order by its ID and redirects to the orders page.

        Parameters:
            order_id (int): The ID of the order to be deleted.

        Returns:
            Response: Redirects the user to 'show_orders' after deleting the order.
    """
    db_manager.delete_order(order_id)
    return redirect(url_for('show_orders'))

@app.route('/update-menu', methods=['GET', 'POST'])
@login_required
def update_menu():
    """
    Route for updating menu items.

    Retrieves all menu items from the database. If request method is POST, it retrieves 
    all the data from the form submitted and updates the database accordingly.
    Then, renders the 'menu.html' template. If the request method is GET,
    it renders the 'update_menu.html' template.

        Returns:
            str: The rendered 'menu.html' or 'update_menu.html' template.
    """
    menu_items = db_manager.get_all_menu_items()
    if request.method == 'POST':
        # Retrieves the data from the form
        selected_menu_item_id = request.form.get('menu_item')
        new_name = request.form.get('name')
        new_description = request.form.get('description')
        new_price = request.form.get('price')
        new_ingredients = request.form.get('ingredients')
        new_calorie = request.form.get('calorie')
        new_category = request.form.get('category')

        # Retrieves the menu items data from the database
        current_item_data = db_manager.get_menu_item_by_id(selected_menu_item_id)
        current_image_url = current_item_data['menu_item_image_url']

        new_image_url = None
        # Checks to see if the image file is in the request
        if 'image' in request.files:
            file = request.files['image']
            # Checks to see if the file has a filename
            if file.filename != '':
                filename = secure_filename(file.filename)
                # Creates the file path where the new uploaded image will be saved
                file_path = os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                # Updates the new_image_url to the path where the file will be saved
                new_image_url = f'static/images/{filename}'
            else:
                # Retains current image if no new image is uploaded
                new_image_url = current_image_url

        # Updates the menu item in the database
        db_manager.update_menu_item(selected_menu_item_id, new_name, new_description, new_price, new_ingredients,
                                    new_calorie, new_image_url, new_category)

        menu_items = db_manager.get_all_menu_items()
        return render_template('menu.html', menu_items=menu_items)

    return render_template('update_menu.html', menu_items=menu_items)

@app.route('/get-menu-item-details/<int:menu_item_id>', methods=['GET'])
def get_menu_item_details(menu_item_id):
    """
    Retrieves details of a specific menu item by its ID.

        Parameters:
            menu_item_id (int): The ID of the menu item to retrieve details for.

        Returns:
            Response: JSON response containing details of the menu item.
    """
    # Retrieves the data of the menu item from the database based on its ID
    menu_item_details = db_manager.get_menu_item_by_id(menu_item_id)
    # Returns it in JSON format
    return jsonify(menu_item_details)

@app.route('/create-menu-item', methods=['GET', 'POST'])
@login_required
def create_menu_item():
    """
    Route for creating menu items.

    If the request method is POST, it retrieves data from the form submitted and creates
    the menu item in the database. Then it redirects the user to the menu page
    to view the updated menu. If the request method is GET, it renders the 'create_menu_item.html'
    template to allow the user to create a new menu item.

        Returns:
            Response/str: Redirects the user to the 'menu' page or renders the 'create_menu_item.html'
            template.
    """
    if request.method == 'POST':
        # Retrieves the data from the form
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price')
        ingredients = request.form.get('ingredients')
        calorie = request.form.get('calorie')
        category = request.form.get('category')

        # Checks to see if the image file is in the request 
        image_url = None
        if 'image' in request.files:
            file = request.files['image']
            # Checks to see if the file has a filename
            if file.filename != '':
                filename = secure_filename(file.filename)
                # Constructs the file path where the uploaded image will be saved
                file_path = os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                # Updates the image_url to the path where the file is saved
                image_url = f'static/images/{filename}'

        # Creates a new menu item in the database
        db_manager.create_menu_item(name, description, price, ingredients, calorie, image_url, category)
        # Redirects user to the menu to view the menu with the newly created menu item
        return redirect(url_for('menu'))

    return render_template('create_menu_item.html')

@app.route('/view-tables', methods=['GET', 'POST'])
@login_required
def view_tables():
    """
    Route to view assigned tables and their corresponding orders as a waiter.

        Returns:
            str: The rendered 'waiter-tables.html' template.
    """
    user_id = session.get('user_id')
    role_id = db_manager.get_role_id(user_id)
    if role_id != 2:
        return redirect(url_for('index'))

    assigned_tables_bitmask = db_manager.get_waiter_tables(user_id)
    assigned_tables = db_manager.decode_bitmask(assigned_tables_bitmask)

    tables_with_orders = {}
    for table in assigned_tables:
        orders = db_manager.get_orders_by_table(table)
        detailed_orders = [db_manager.get_order(order['order_id']) for order in orders]
        tables_with_orders[table] = detailed_orders

    return render_template('waiter-tables.html', tables_with_orders=tables_with_orders)

@app.route('/create-order', methods=['POST'])
@login_required
def create_order():
    """
    Route for creating a new order.

    Creates a new order based on the JSON payload. Processes the table number, order items, 
    calculates the total price, and saves the order to the database. 
    Returns a JSON response with the success or failure of the order creation.

        Returns:
            Response: JSON response indicating the success or failure of the order creation.
    """
    payload = request.get_json()
    current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')


    table_number = payload.get('tableNumber')
    order_items = payload.get('orderItems', [])

    menu_items = db_manager.get_all_menu_items()
    menu_items_dict = {item['menu_item_name']: {'id': item['menu_item_id'], 'price': item['menu_item_price']} for item
                       in menu_items}

    total_price = 0


    for item in order_items:
        name = item["name"]
        quantity = item["quantity"]
        if name in menu_items_dict:
            price = menu_items_dict[name]['price']
            total_price += price * quantity
        else:
            return jsonify({"status": "error", "message": f"Item '{name}' not found in the menu."}), 400

    order_id = db_manager.create_order(current_date, g.user['email'], table_number, total_price, g.user['user_id'])

    for item in order_items:
        name = item["name"]
        quantity = item["quantity"]
        if name in menu_items_dict:
            menu_item_id = menu_items_dict[name]['id']
            db_manager.insert_order_item(order_id, menu_item_id, quantity)

    return jsonify({"status": "success", "message": "Order processed successfully."})

@app.route('/order-items/<int:order_id>')
@login_required
def view_order(order_id):
    """
    Retrieves the order items that are associated with the order ID from the database.
    Then it renders the 'view-order.html' template with the retrieved items and the order ID.

        Parameters:
            order_id (int): The ID of the order to view its items.

        Returns:
            str/Response: The rendered HTML of the 'view-order.html' template or redirects to
            login page if not logged in.
    """
    if 'user_id' in session:
        items = db_manager.get_order_items(order_id)
        return render_template('view-order.html', items=items, order_id=order_id)
    else:
        return redirect(url_for('login'))


@app.route('/edit-waiter-tables', methods=['GET', 'POST'])
@login_required
def edit_waiter_tables():
    """
    Route for editing tables assigned to a waiter.

    If request method is POST, it will update tables assigned to the waiter
    according to the submitted form data and then redirect to 'edit_waiter_tables'.
    If request method is GET, it will retrieve all current tables assigned to the waiter
    and render the 'assign_tables' template in order for waiter to be able to edit tables.

        Returns:
            Response/str: Redirects to 'edit_waiter_tables' or renders 'assign_tables.html' template.
    """
    user_id = session.get('user_id')
    role_id = db_manager.get_role_id(user_id)

    if role_id != 2:
        return redirect(url_for('index'))

    if request.method == 'POST':
        new_tables = request.form.getlist('tables')
        new_tables_set = set(map(int, new_tables))

        current_bitmask = db_manager.get_waiter_tables(user_id)
        current_tables = db_manager.decode_bitmask(current_bitmask)
        db_manager.remove_waiter_tables(user_id, current_tables)

        db_manager.add_waiter_tables(user_id, new_tables_set)

        return redirect(url_for('edit_waiter_tables'))

    current_bitmask = db_manager.get_waiter_tables(user_id)
    current_tables = db_manager.decode_bitmask(current_bitmask)
    all_tables = set(range(1, 21))  # Assuming there are 20 tables in total

    return render_template('assign_tables.html', current_tables=current_tables, all_tables=all_tables)


@app.route('/order-confirmation')
@login_required
def order_confirmation():
    """
    Renders the 'order_confirmation.html' template to confirm order has been accepted.

        Returns:
            str: The rendered 'order_confirmation.html' template.
    """
    return render_template('order_confirmation.html')


@app.route('/my-orders')
@login_required
def my_orders():
    """
    Retrieves all orders associated with the logged-in user ID from the database and
    then renders the 'my_orders.html' template with the associated orders.

        Returns:
            str/Response: The rendered 'my_orders.html' template or redirects to login page if
            not logged in.
    """
    if 'user_id' in session:
        user_id = session['user_id']
        orders = db_manager.get_user_orders(user_id)
        return render_template('my_orders.html', orders=orders)
    else:
        return redirect(url_for('login'))


@app.route('/checkout/<int:order_id>', methods=["POST", "GET"])
def checkout(order_id):
    """
    If request method is POST, it will update the order status to 'Paid' and
    redirects to 'my_orders' page. If request method is GET, retrieves the order
    thats associated with the order ID and renders 'checkout.html' template

        Parameters:
            order_id (int): The ID of the order to be checked out.

        Returns:
            Response/str: Redirects to 'my_orders' page or renders the 'checkout.html' template.
    """
    if request.method == 'POST':
        db_manager.update_order(order_id, 'The order has been Paid!')
        return redirect(url_for('my_orders'))
    else:
        order = db_manager.get_order(order_id)
        if order:
            return render_template('checkout.html', order=order)
        else:
            return redirect(url_for('my_orders'))

@app.route('/calling-waiter-list')
@login_required
def calling_waiter():
    """
    Retrieves customers that require the waiter from the database.

        Returns:
            str: The rendered 'calling-waiter-list.html' template.
    """
    customers = db_manager.get_customers_need_waiter()

    return render_template('calling-waiter-list.html', customers=customers)


@app.route('/calling-waiter-list/edit-table', methods=["POST"])
@login_required
def calling_waiter_edit_table():
    """
    Retrieves customers that require the waiter from the database. If request method
    is POST, it will retrieve the user ID from submitted form and changes status
    the need for the waiter for the customer.

        Returns:
            str: The rendered 'calling-waiter-list.html' template.
    """
    customers = db_manager.get_customers_need_waiter()

    if request.method == "POST":
        user_id = request.form.get('user_id')
        db_manager.change_needs_waiter(user_id)

    return render_template('calling-waiter-list.html', customers=customers)

@app.route('/manage-users', methods=["POST", "GET"])
@login_required
def manager_users():
    """
    Ensures that the user is a Manager then retrieves all users from the database. If
    request method is POST, handles all operations such as deleting a user or changing
    a user's ID. If request method is GET, renders 'manage_users.html' template so
    the manager is able to manage the users.

        Returns:
            Response/str: JSON response indicating the result of the action of the manager or
            the rendered 'manage_users.html' template.
    """
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


@app.route('/view-order-times')
@login_required
def view_order_times():
    """
    Route for viewing order times as kitchen staff.

    Retrieves all orders from the database and renders the 'order_times.html' template
    with the retrieved orders.

        Returns:
            str: The rendered 'order_times.html' template.
    """
    orders = db_manager.get_all_orders()
    
    return render_template('order_times.html', orders=orders)

if __name__ == '__main__':
    app.run(debug=True)
