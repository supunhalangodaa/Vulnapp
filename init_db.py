from app import app, db, User, Product
from werkzeug.security import generate_password_hash

def init_db():
    with app.app_context():
        # Create all tables
        db.create_all()

        # Check if admin user exists
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@example.com',
                is_admin=True
            )
            admin.set_password('admin123')
            db.session.add(admin)

        # Add some sample products if none exist
        if not Product.query.first():
            products = [
                Product(
                    name='Vulnerable Laptop',
                    description='A laptop with intentional security flaws. Perfect for testing!',
                    price=999.99,
                    stock=10,
                    image_path='laptop.jpg'
                ),
                Product(
                    name='Buggy Smartphone',
                    description='A smartphone with exploitable features. Great for CTF practice!',
                    price=699.99,
                    stock=15,
                    image_path='smartphone.jpg'
                ),
                Product(
                    name='Hackable Router',
                    description='A router with known vulnerabilities. Ideal for security research!',
                    price=199.99,
                    stock=20,
                    image_path='router.jpg'
                )
            ]
            db.session.add_all(products)

        # Commit all changes
        db.session.commit()

if __name__ == '__main__':
    init_db() 