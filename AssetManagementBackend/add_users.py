from app import app, db, hash_password
from models import User, Portfolio, Asset, Fee
from datetime import datetime

def add_test_users():
    with app.app_context():
        try:
            # Create users if they don't exist
            print("Checking for existing users...")
            if not User.query.filter_by(email="john.doe@example.com").first():
                john = User(
                    email="john.doe@example.com",
                    password=hash_password("password123"),
                    first_name="John",
                    last_name="Doe"
                )
                db.session.add(john)
                db.session.commit()
                print("Created user: john.doe@example.com")

            if not User.query.filter_by(email="jane.smith@example.com").first():
                jane = User(
                    email="jane.smith@example.com",
                    password=hash_password("password123"),
                    first_name="Jane",
                    last_name="Smith"
                )
                db.session.add(jane)
                db.session.commit()
                print("Created user: jane.smith@example.com")

            # Create sample portfolios directly assigned to users
            john_user = User.query.filter_by(email="john.doe@example.com").first()
            jane_user = User.query.filter_by(email="jane.smith@example.com").first()

            print("Creating sample portfolios for users...")
            portfolios_data = [
                Portfolio(name="Tech Growth Fund", manager="Alpha Investments", total_assets=50000000, user_id=john_user.id),
                Portfolio(name="Balanced Portfolio", manager="Beta Capital", total_assets=75000000, user_id=john_user.id),
                Portfolio(name="Conservative Fund", manager="Gamma Advisors", total_assets=30000000, user_id=jane_user.id),
                Portfolio(name="Emerging Markets", manager="Delta Management", total_assets=40000000, user_id=jane_user.id),
            ]

            for portfolio in portfolios_data:
                # Check if portfolio already exists
                existing = Portfolio.query.filter_by(
                    name=portfolio.name,
                    user_id=portfolio.user_id
                ).first()
                if not existing:
                    db.session.add(portfolio)

            db.session.commit()
            print("Sample portfolios created for users")

            # Create sample assets and fees for user's portfolios
            all_user_portfolios = Portfolio.query.filter(
                (Portfolio.user_id == john_user.id) | (Portfolio.user_id == jane_user.id)
            ).all()

            if len(all_user_portfolios) > 0 and Asset.query.count() == 0:
                print("Creating sample assets and fees...")
                for portfolio in all_user_portfolios:
                    # Add some assets
                    for j in range(3):
                        asset = Asset(
                            portfolio_id=portfolio.id,
                            symbol=f"AST{j}{portfolio.id}",
                            name=f"Asset {j+1} - {portfolio.name}",
                            quantity=1000.0,
                            purchase_price=10.0,
                            current_price=12.0,
                            purchase_date=datetime(2024, 1, 1)
                        )
                        db.session.add(asset)

                    # Add some fees with occasional anomalies
                    base_fee = 1000.0
                    for k in range(8):
                        if k > 5:  # Create anomalies in recent months
                            amount = base_fee + (k * 200)  # Anomalies
                        else:
                            amount = base_fee + (k * 50)  # Normal variation

                        fee = Fee(
                            portfolio_id=portfolio.id,
                            amount=amount,
                            date=datetime(2024, k+1, 1).date(),
                            fee_type="management" if k % 2 == 0 else "performance",
                            description=f"Monthly {'management' if k % 2 == 0 else 'performance'} fee"
                        )
                        db.session.add(fee)

                db.session.commit()
                print("Sample assets and fees created")

            print("All sample data created successfully!")
            print("\nLOGIN CREDENTIALS:")
            print("john.doe@example.com / password123")
            print("jane.smith@example.com / password123")
            print("\nJohn's portfolios: Tech Growth Fund, Balanced Portfolio")
            print("Jane's portfolios: Conservative Fund, Emerging Markets")

        except Exception as e:
            db.session.rollback()
            print(f"Error: {e}")

if __name__ == "__main__":
    add_test_users()
