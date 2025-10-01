from app import app, db, hash_password
from models import User, Portfolio, Asset, Fee
from datetime import datetime, timedelta
import random

def add_sample_data():
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()

        # Create sample users if they don't exist
        if User.query.filter_by(email="john.doe@example.com").first() is None:
            users = [
                User(email="john.doe@example.com", password=hash_password("password123"),
                     first_name="John", last_name="Doe"),
                User(email="jane.smith@example.com", password=hash_password("password123"),
                     first_name="Jane", last_name="Smith"),
            ]

            for user in users:
                db.session.add(user)
            db.session.commit()

            print("Sample users created:")
            print("- john.doe@example.com / password123")
            print("- jane.smith@example.com / password123")
        else:
            print("Sample users already exist")

        # Update existing portfolios to have user assignments
        users = User.query.all()
        if users and Portfolio.query.filter_by(user_id=None).first():
            portfolios = Portfolio.query.filter_by(user_id=None).all()
            for i, portfolio in enumerate(portfolios):
                portfolio.user_id = users[i % len(users)].id
            db.session.commit()
            print(f"Updated {len(portfolios)} portfolios with user assignments")

        print("Sample data initialization complete!")

if __name__ == "__main__":
    add_sample_data()
