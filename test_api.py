#!/usr/bin/env python3
"""
Test script to check API endpoints
"""

import requests

# Base URL
BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health check: {response.status_code}")
    print(response.json())
    
def test_index():
    """Test index endpoint"""
    response = requests.get(f"{BASE_URL}/")
    print(f"Index: {response.status_code}")
    print(response.json())

def test_orders():
    """Test orders endpoint"""
    response = requests.get(f"{BASE_URL}/orders")
    print(f"Orders: {response.status_code}")
    if response.status_code == 200:
        print(response.json())
    else:
        print(response.text)
        
def test_items():
    """Test to create and get items"""
    # First create an order
    order_data = {
        "customer_id": 123,
        "status": "PENDING"
    }
    
    # Create order
    response = requests.post(f"{BASE_URL}/orders", json=order_data)
    print(f"Create order: {response.status_code}")
    if response.status_code == 201:
        order = response.json()
        order_id = order["id"]
        print(f"Created order with ID: {order_id}")
        
        # Now try to access items
        response = requests.get(f"{BASE_URL}/orders/{order_id}/items")
        print(f"Get items: {response.status_code}")
        print(response.text)
    else:
        print(response.text)

if __name__ == "__main__":
    print("Testing API endpoints...")
    test_health()
    print("\n")
    test_index()
    print("\n")
    test_orders()
    print("\n")
    test_items()
