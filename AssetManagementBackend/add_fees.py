#!/usr/bin/env python3

import os
import sys

# Add current directory to path so we can import
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from datetime import datetime

def add_fees():
    with app.app_context():
        print("Adding sample fees for anomaly detection testing...")

        try:
            # Get all portfolios
            result = db.session.execute(db.text("SELECT id, name FROM portfolios")).fetchall()
            portfolios = [{'id': row[0], 'name': row[1]} for row in result]

            print(f"Found {len(portfolios)} portfolios")
            for portfolio in portfolios:
                print(f"Processing {portfolio['name']} (ID: {portfolio['id']})")

                # Check existing fees count
                existing_count = db.session.execute(db.text(
                    "SELECT COUNT(*) FROM fees WHERE portfolio_id = :pid"
                ), {'pid': portfolio['id']}).fetchone()[0]

                if existing_count == 0:
                    # Add sample fees with some anomalies
                    fees = []
                    for month in range(1, 11):  # 10 months of data
                        # Add some varying fees with occasional anomalies
                        base_fee = 1000.0 + (month * 50)  # Gradually increasing

                        # Make some irregularities (anomalies)
                        if portfolio['id'] in [1, 3] and month in [3, 8]:  # Anomalies in some portfolios
                            amount = base_fee * 2.5  # Significantly higher
                        elif portfolio['id'] == 2 and month == 6:
                            amount = base_fee * 0.3  # Significantly lower
                        else:
                            # Normal variation
                            import random
                            amount = base_fee * (0.9 + random.random() * 0.2)  # ±10% variation

                        fee_date = datetime(2024, month, 15)  # Mid-month

                        fees.append({
                            'portfolio_id': portfolio['id'],
                            'amount': round(amount, 2),
                            'date': fee_date,
                            'fee_type': 'management' if month % 2 == 0 else 'performance',
                            'description': f'Monthly {"management" if month % 2 == 0 else "performance"} fee for {portfolio["name"]}'
                        })

                    # Insert fees
                    for fee in fees:
                        db.session.execute(db.text("""
                            INSERT INTO fees (portfolio_id, amount, date, fee_type, description)
                            VALUES (:portfolio_id, :amount, :date, :fee_type, :description)
                        """), fee)

                    db.session.commit()
                    print(f"  ✓ Added {len(fees)} fees (with {len([f for f in fees if f['amount'] > base_fee * 1.5])} anomalies)")
                else:
                    print(f"  - Already has {existing_count} fees, skipping")

            print("\n🎯 All portfolios now have fee data for anomaly testing!")
            print("Anomalies have been baked into some portfolios:")
            print("- Portfolios 1 & 3 have high fee anomalies in months 3 and 8")
            print("- Portfolio 2 has low fee anomaly in month 6")

        except Exception as e:
            print(f"❌ Error: {e}")
            db.session.rollback()

if __name__ == "__main__":
    add_fees()
