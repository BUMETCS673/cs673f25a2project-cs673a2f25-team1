from app import app, db
from models import Portfolio, Asset, Fee
from datetime import datetime, timedelta
import random

def add_sample_data():
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()

        # Clear existing data
        try:
            db.session.query(Fee).delete()
            db.session.query(Asset).delete()
            db.session.query(Portfolio).delete()
            db.session.commit()
        except:
            # Tables might not exist yet, skip deletion
            pass

        # Create sample portfolios
        portfolios = [
            Portfolio(name="Tech Growth Fund", manager="Alpha Investments", total_assets=50000000),
            Portfolio(name="Balanced Portfolio", manager="Beta Capital", total_assets=75000000),
            Portfolio(name="Conservative Fund", manager="Gamma Advisors", total_assets=30000000),
            Portfolio(name="Emerging Markets", manager="Delta Management", total_assets=40000000),
        ]

        for portfolio in portfolios:
            db.session.add(portfolio)
        db.session.commit()

        # Create sample assets for each portfolio
        assets = []
        for portfolio in portfolios:
            for i in range(5):  # 5 assets per portfolio
                asset = Asset(
                    portfolio_id=portfolio.id,
                    symbol=f"AST{i+1}{portfolio.id}",
                    name=f"Asset {i+1} - {portfolio.name}",
                    quantity=random.uniform(100, 10000),
                    purchase_price=random.uniform(10, 500),
                    current_price=random.uniform(10, 500),
                    purchase_date=datetime.now() - timedelta(days=random.randint(30, 365))
                )
                assets.append(asset)
                db.session.add(asset)
        db.session.commit()

        # Create sample fees with some anomalies
        for portfolio in portfolios:
            base_fee = random.uniform(0.5, 2.0)  # Normal fee range 0.5% - 2.0%

            for i in range(12):  # 12 months of data
                date = datetime.now() - timedelta(days=30*i)

                # Introduce anomalies for some portfolios (higher fees)
                if portfolio.id % 2 == 0 and i > 6:  # Every 2nd portfolio has anomalies in recent months
                    fee_amount = base_fee * random.uniform(2.5, 4.0)  # Anomalously high fees
                else:
                    fee_amount = base_fee * random.uniform(0.8, 1.2)  # Normal variation

                fee = Fee(
                    portfolio_id=portfolio.id,
                    amount=fee_amount,
                    date=date.date(),
                    fee_type=random.choice(['management', 'performance', 'administrative']),
                    description=f"Monthly {random.choice(['management', 'performance', 'administrative'])} fee"
                )
                db.session.add(fee)

        db.session.commit()
        print("Sample data added successfully!")

if __name__ == "__main__":
    add_sample_data()
