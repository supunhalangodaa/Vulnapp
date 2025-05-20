from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
import sqlite3
import pickle
import subprocess
import base64
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super_secret_key_123'  # Weak secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vulnshop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    reset_token = db.Column(db.String(120), nullable=True)
    orders = db.relationship('Order', backref='user', lazy=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_path = db.Column(db.String(200))
    stock = db.Column(db.Integer, default=0)
    orders = db.relationship('OrderItem', backref='product', lazy=True)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_ordered = db.Column(db.DateTime, default=datetime.utcnow)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')
    items = db.relationship('OrderItem', backref='order', lazy=True)

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

# Create database tables
with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Flag 1: SQL Injection in Product Search
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    # Vulnerable SQL query
    conn = sqlite3.connect('vulnshop.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM product WHERE name LIKE '%{query}%' OR description LIKE '%{query}%'")
    results = cursor.fetchall()
    conn.close()
    return render_template('search.html', results=results)

# Flag 2: Command Injection in Image Processing
@app.route('/process-image', methods=['POST'])
def process_image():
    if 'image' not in request.files:
        return 'No image uploaded', 400
    
    image = request.files['image']
    filename = secure_filename(image.filename)
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image.save(image_path)
    
    # Vulnerable command execution
    command = f"convert {image_path} -resize 800x600 {image_path}"
    subprocess.check_output(command, shell=True)
    return 'Image processed successfully'

# Flag 3: XSS in Product Reviews
@app.route('/add-review/<int:product_id>', methods=['POST'])
def add_review(product_id):
    review = request.form.get('review', '')
    rating = request.form.get('rating', '')
    # Vulnerable XSS
    return f'<div class="review"><p>Rating: {rating}</p><p>Review: {review}</p></div>'

# Flag 4: Directory Traversal in Product Images
@app.route('/product-image/<path:filename>')
def get_product_image(filename):
    # Vulnerable file access
    return send_file(f'uploads/{filename}')

# Flag 5: Insecure Deserialization in Cart
@app.route('/update-cart', methods=['POST'])
def update_cart():
    cart_data = request.form.get('cart', '')
    # Vulnerable deserialization
    cart = pickle.loads(base64.b64decode(cart_data))
    return 'Cart updated successfully'

# Flag 6: Weak Password Reset
@app.route('/reset-password', methods=['POST'])
def reset_password():
    email = request.form.get('email', '')
    user = User.query.filter_by(email=email).first()
    if user:
        # Weak token generation
        token = base64.b64encode(email.encode()).decode()
        user.reset_token = token
        db.session.commit()
        return f'Reset token: {token}'
    return 'User not found'

# Regular Routes
@app.route('/')
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product.html', product=product)

@app.route('/cart')
@login_required
def cart():
    return render_template('cart.html')

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    if request.method == 'POST':
        # Process order
        return redirect(url_for('order_confirmation'))
    return render_template('checkout.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username, password=password).first()
        if user:
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
            
        user = User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 