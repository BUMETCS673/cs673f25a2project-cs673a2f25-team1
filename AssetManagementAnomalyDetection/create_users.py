#!/usr/bin/env python3

import os
import sys

# Add current directory to path so we can import
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, hash_password
from models import User

from datetime import datetime

def create_test_users():
    with app.app_context():
        print("Creating test users and sample data...")

        # Create users
        john = User(
            email="john.doe@example.com",
            password=hash_password("password123"),
            first_name="John",
            last_name="Doe"
        )

        jane = User(
            email="jane.smith@example.com",
            password=hash_password("password123"),
            first_name="Jane",
            last_name="Smith"
        )

        try:
            db.session.add(john)
            db.session.add(jane)
            db.session.commit()
            print("✅ Test users created")

            # Create portfolios for each user
            from models import Portfolio, Asset, Fee

            portfolios = [
                Portfolio(name="Tech Growth Fund", manager="Alpha Investments", total_assets=50000000),
                Portfolio(name="Balanced Portfolio", manager="Beta Capital", total_assets=75000000),
                Portfolio(name="Conservative Fund", manager="Gamma Advisors", total_assets=30000000),
                Portfolio(name="Emerging Markets", manager="Delta Management", total_assets=40000000),
            ]

            for portfolio in portfolios:
                db.session.add(portfolio)
            db.session.commit()
            print("✅ Portfolios created")

            # Add sample fees (some with anomalies) for anomaly detection
            for portfolio in portfolios:
                # Regular fees
                for month in range(1, 8):  # 8 months of data
                    # Create some fee anomalies in recent months
                    if month > 5 and portfolio.id in [1, 3]:  # Anomalies in some portfolios
                        amount = 1000 + (month * 300)  # Anomalous high fees
                    else:
                        amount = 1000 + (month * 50)   # Normal fee range

                    fee = Fee(
                        portfolio_id=portfolio.id,
                        amount=amount,
                        date=datetime(2024, month, 1).date(),
                        fee_type="management",
                        description=f"Monthly management fee for {portfolio.name}"
                    )
                    db.session.add(fee)
            db.session.commit()
            print("✅ Sample fees created with anomalies for testing")

            print("\n🎯 SETUP COMPLETE!")
            print("Login credentials:")
            print("john.doe@example.com / password123")
            print("jane.smith@example.com / password123")
            print("\nAvailable portfolios:")
            print("- Tech Growth Fund (has anomalies)")
            print("- Balanced Portfolio (normal)")
            print("- Conservative Fund (normal)")
            print("- Emerging Markets (has anomalies)")

        except Exception as e:
            print(f"❌ Error: {e}")
            db.session.rollback()

if __name__ == "__main__":
    create_test_users()
