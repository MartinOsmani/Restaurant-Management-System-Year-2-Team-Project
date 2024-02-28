from flask import Flask, render_template, session, redirect, url_for, request
from flaskr.auth import bp as auth_bp, login_required
from flaskr.db import init_db
from flaskr.DatabaseManager import DatabaseManager
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['DATABASE'] = 'database.db'
app.config['UPLOAD_FOLDER'] = 'static/images'

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

@app.route('/book')
def book():
    return render_template('book.html')

if __name__ == '__main__':
    app.run(debug=True)
