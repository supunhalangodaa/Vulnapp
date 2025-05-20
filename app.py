from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
import sqlite3
import pickle
import subprocess
import base64

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super_secret_key_123'  # Weak secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vulnapp.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    reset_token = db.Column(db.String(120), nullable=True)

# Create database tables
with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Flag 1: SQL Injection
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    # Vulnerable SQL query
    conn = sqlite3.connect('vulnapp.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM users WHERE username LIKE '%{query}%'")
    results = cursor.fetchall()
    conn.close()
    return render_template('search.html', results=results)

# Flag 2: Command Injection
@app.route('/ping', methods=['GET'])
def ping():
    host = request.args.get('host', '127.0.0.1')
    # Vulnerable command execution
    result = subprocess.check_output(f'ping -c 1 {host}', shell=True)
    return result

# Flag 3: XSS
@app.route('/comment', methods=['POST'])
def comment():
    comment = request.form.get('comment', '')
    # Vulnerable XSS
    return f'<div class="comment">{comment}</div>'

# Flag 4: Directory Traversal
@app.route('/file', methods=['GET'])
def get_file():
    filename = request.args.get('name', '')
    # Vulnerable file access
    return send_file(f'files/{filename}')

# Flag 5: Insecure Deserialization
@app.route('/profile', methods=['POST'])
def update_profile():
    data = request.form.get('data', '')
    # Vulnerable deserialization
    user_data = pickle.loads(base64.b64decode(data))
    return 'Profile updated'

# Flag 6: Weak Password Reset
@app.route('/reset-password', methods=['POST'])
def reset_password():
    username = request.form.get('username', '')
    user = User.query.filter_by(username=username).first()
    if user:
        # Weak token generation
        token = base64.b64encode(username.encode()).decode()
        user.reset_token = token
        db.session.commit()
        return f'Reset token: {token}'
    return 'User not found'

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 