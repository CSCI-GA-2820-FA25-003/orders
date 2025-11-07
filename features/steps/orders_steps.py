######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
Order Steps

Steps file for Order.feature

For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""

import requests
from compare3 import expect
from behave import given  # pylint: disable=no-name-in-module

# HTTP Return Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204

WAIT_TIMEOUT = 60


@given("the following orders exist")
def step_impl(context):
    """Delete all Orders and load new ones"""

    # Get a list all of the orders
    rest_endpoint = f"{context.base_url}/orders"
    context.resp = requests.get(rest_endpoint, timeout=WAIT_TIMEOUT)
    expect(context.resp.status_code).equal_to(HTTP_200_OK)
    # and delete them one by one
    for order in context.resp.json():
        context.resp = requests.delete(
            f"{rest_endpoint}/{order['id']}", timeout=WAIT_TIMEOUT
        )
        expect(context.resp.status_code).equal_to(HTTP_204_NO_CONTENT)

    # Store order IDs for later reference
    context.order_id_map = {}

    # load the database with new orders
    for idx, row in enumerate(context.table):
        payload = {
            "customer_id": int(row["customer_id"]),
            "status": row["status"],
            "total_price": str(row["total_price"]),
        }
        context.resp = requests.post(rest_endpoint, json=payload, timeout=WAIT_TIMEOUT)
        expect(context.resp.status_code).equal_to(HTTP_201_CREATED)
        order_data = context.resp.json()
        context.order_id_map[str(idx + 1)] = order_data["id"]


@given("the following order items exist")
def step_impl(context):
    """Add items to orders"""

    # Get all existing orders to map items to them
    rest_endpoint = f"{context.base_url}/orders"
    context.resp = requests.get(rest_endpoint, timeout=WAIT_TIMEOUT)
    expect(context.resp.status_code).equal_to(HTTP_200_OK)
    orders = context.resp.json()

    # Create a mapping of customer_id to list of order_ids
    # Items will be distributed across orders with matching customer_id
    order_map = {}
    for order in orders:
        key = str(order["customer_id"])
        if key not in order_map:
            order_map[key] = []
        order_map[key].append(order["id"])

    # Add items to orders - distribute items across orders with same customer_id
    # Track which order index we're using for sequential distribution
    item_index = 0

    for row in context.table:
        # Try to match by customer_id if we have order_id_map from previous step
        order_id = None
        if hasattr(context, "order_id_map") and context.order_id_map:
            # Use order_id_map to find the right order
            # Items are added sequentially to orders
            order_keys = sorted(context.order_id_map.keys())
            if item_index < len(order_keys):
                order_id = context.order_id_map[order_keys[item_index]]
                item_index += 1

        # Fallback: use first available order
        if not order_id and orders:
            order_id = orders[0]["id"]

        if order_id:
            item_endpoint = f"{rest_endpoint}/{order_id}/items"
            payload = {
                "name": row["name"],
                "category": row["category"],
                "product_id": int(row["product_id"]),
                "description": row["description"],
                "price": str(row["price"]),
                "quantity": int(row["quantity"]),
                "order_id": order_id,  # Required field for Item deserialize
            }
            context.resp = requests.post(
                item_endpoint, json=payload, timeout=WAIT_TIMEOUT
            )
            expect(context.resp.status_code).equal_to(HTTP_201_CREATED)
