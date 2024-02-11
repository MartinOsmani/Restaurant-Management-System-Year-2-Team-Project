from flask import Flask, render_template
from flaskr.auth import bp as auth_bp
from flaskr.db import init_db
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['DATABASE'] = 'database.db'


with app.app_context():
    init_db()

# Register the auth blueprint
app.register_blueprint(auth_bp)



@app.route('/')
def index():
    return render_template('home.html')

@app.route('/menu')
def menu():
    return render_template('menu.html')

@app.route('/book')
def book():
    return render_template('book.html')

if __name__ == '__main__':
    app.run(debug=True)
