#!/usr/bin/env python3

import requests

def test_api():
    print("Testing Asset Management API...")

    # First, test login
    print("\n1. Testing login...")
    login_data = {
        "email": "john.doe@example.com",
        "password": "password123"
    }

    try:
        response = requests.post("http://127.0.0.1:5000/api/auth/login", json=login_data)
        print(f"Login response: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"User: {data['user']['first_name']} {data['user']['last_name']}")
            print(f"Token: {data['access_token'][:20]}...")

            # Now test portfolios endpoint with token
            print("\n2. Testing portfolios endpoint...")
            headers = {"Authorization": f"Bearer {data['access_token']}"}
            portfolio_response = requests.get("http://127.0.0.1:5000/api/portfolios", headers=headers)
            print(f"Portfolios response: {portfolio_response.status_code}")

            if portfolio_response.status_code == 200:
                portfolios = portfolio_response.json()
                print(f"Found {len(portfolios)} portfolios:")
                for p in portfolios[:2]:  # Show first 2
                    print(f"  - {p['name']} (Manager: {p['manager']})")
            else:
                print(f"Error: {portfolio_response.text[:100]}")

        else:
            print(f"Login failed: {response.text}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api()
