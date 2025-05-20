from app import db, User, Product
import os

def init_db():
    # Create database tables
    db.create_all()

    # Add test user
    test_user = User(
        username='test',
        email='test@example.com',
        password='password123',
        is_admin=False
    )
    db.session.add(test_user)

    # Add admin user with flag
    admin_user = User(
        username='admin',
        email='admin@vulnshop.com',
        password='FLAG{sql_1nj3ct10n_1s_d4ng3r0us}',
        is_admin=True
    )
    db.session.add(admin_user)

    # Add sample products
    products = [
        Product(
            name='Secure Web Server',
            description='A web server with all the latest security patches. Flag: FLAG{c0mm4nd_1nj3ct10n_br34ks_s3cur1ty}',
            price=999.99,
            stock=10
        ),
        Product(
            name='Encrypted USB Drive',
            description='Store your secrets safely with this encrypted USB drive.',
            price=49.99,
            stock=50
        ),
        Product(
            name='Password Manager',
            description='Never forget your passwords again!',
            price=29.99,
            stock=100
        ),
        Product(
            name='Security Camera',
            description='Monitor your home 24/7 with this high-tech security camera.',
            price=199.99,
            stock=25
        ),
        Product(
            name='VPN Service',
            description='Browse the web anonymously with our premium VPN service.',
            price=9.99,
            stock=1000
        ),
        Product(
            name='Firewall Appliance',
            description='Protect your network with this enterprise-grade firewall.',
            price=1499.99,
            stock=5
        )
    ]

    for product in products:
        db.session.add(product)

    # Commit changes
    db.session.commit()

if __name__ == '__main__':
    # Remove existing database
    if os.path.exists('vulnshop.db'):
        os.remove('vulnshop.db')
    
    # Create uploads directory
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    
    # Initialize database
    init_db()
    print("Database initialized successfully!") 