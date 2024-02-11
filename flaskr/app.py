from flask import Flask, render_template
from flaskr.auth import bp as auth_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'

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
