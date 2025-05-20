from app import db, User
import os

def init_db():
    # Create database tables
    db.create_all()

    # Add test user
    test_user = User(username='test', password='password123')
    db.session.add(test_user)

    # Add hidden user with flag
    hidden_user = User(username='admin', password='FLAG{sql_1nj3ct10n_1s_d4ng3r0us}')
    db.session.add(hidden_user)

    # Commit changes
    db.session.commit()

if __name__ == '__main__':
    # Remove existing database
    if os.path.exists('vulnapp.db'):
        os.remove('vulnapp.db')
    
    # Initialize database
    init_db()
    print("Database initialized successfully!") 