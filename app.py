from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import sqlite3
import subprocess
import pickle
import base64
import re
from datetime import datetime, timedelta
import secrets

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Weak secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vulnapp.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# CTF Flags
FLAG_SQLI = 'FLAG{sql_injection_success}'
FLAG_CMDI = 'FLAG{command_injection_success}'
FLAG_XSS = 'FLAG{xss_success}'
FLAG_TRAVERSAL = 'FLAG{directory_traversal_success}'
FLAG_DESERIAL = 'FLAG{insecure_deserialization_success}'
FLAG_RESET = 'FLAG{weak_password_reset_success}'

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    reset_token = db.Column(db.String(100), unique=True)
    reset_token_expiry = db.Column(db.DateTime)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    image_path = db.Column(db.String(200))
    stock = db.Column(db.Integer, default=0)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Vulnerable Routes

# 1. SQL Injection in Product Search
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    conn = sqlite3.connect('vulnapp.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM product WHERE name LIKE '%{query}%' OR description LIKE '%{query}%'")
    results = cursor.fetchall()
    # If the query returns more than 10 results, assume exploitation and show flag
    flag = None
    if len(results) > 10 or (query and 'union' in query.lower()):
        flag = FLAG_SQLI
    conn.close()
    return render_template('search.html', results=results, flag=flag)

# 2. Command Injection in Image Processing
@app.route('/process-image', methods=['POST'])
def process_image():
    if 'image' not in request.files:
        return 'No image uploaded', 400
    image = request.files['image']
    filename = secure_filename(image.filename)
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image.save(image_path)
    command = f"convert {image_path} -resize 800x600 {image_path}"
    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        # If the output contains the flag keyword, return the flag
        if b'cat' in command.encode() or b'flag' in output:
            return FLAG_CMDI
    except subprocess.CalledProcessError as e:
        # If the output contains the flag keyword, return the flag
        if b'flag' in e.output:
            return FLAG_CMDI
    return 'Image processed successfully'

# 3. XSS in Product Reviews
@app.route('/add-review/<int:product_id>', methods=['POST'])
def add_review(product_id):
    review = request.form.get('review', '')
    rating = request.form.get('rating', '')
    # If the review contains <script>, show the flag
    if '<script>' in review.lower():
        return f'<div class="review"><p>Rating: {rating}</p><p>Review: {review}</p><div style="display:none">{FLAG_XSS}</div></div>'
    return f'<div class="review"><p>Rating: {rating}</p><p>Review: {review}</p></div>'

# 4. Directory Traversal in Product Images
@app.route('/product-image/<path:filename>')
def get_product_image(filename):
    # If the filename is flag.txt, return the flag
    if filename == 'flag.txt':
        return FLAG_TRAVERSAL
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# 5. Insecure Deserialization in Cart
@app.route('/update-cart', methods=['POST'])
def update_cart():
    cart_data = request.form.get('cart', '')
    cart = pickle.loads(base64.b64decode(cart_data))
    # If the cart is a dict and contains 'flag', return the flag
    if isinstance(cart, dict) and cart.get('flag') == 'please':
        return FLAG_DESERIAL
    return 'Cart updated successfully'

# 6. Weak Password Reset
@app.route('/reset-password', methods=['POST'])
def reset_password():
    email = request.form.get('email', '')
    user = User.query.filter_by(email=email).first()
    if user:
        token = base64.b64encode(email.encode()).decode()
        user.reset_token = token
        db.session.commit()
        # If the email is 'flag@ctf.com', return the flag
        if email == 'flag@ctf.com':
            return FLAG_RESET
        return f'Reset token: {token}'
    return 'User not found'

# Regular Routes
@app.route('/')
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
            
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('register'))
            
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product_detail.html', product=product)

@app.route('/cart')
@login_required
def cart():
    return render_template('cart.html')

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    if request.method == 'POST':
        # Process checkout
        flash('Order placed successfully!')
        return redirect(url_for('index'))
    return render_template('checkout.html')

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        flash('Access denied')
        return redirect(url_for('index'))
    return render_template('admin.html')

# Initialize database
with app.app_context():
    db.create_all()
    # Create admin user if not exists
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', email='admin@example.com', is_admin=True)
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True) 