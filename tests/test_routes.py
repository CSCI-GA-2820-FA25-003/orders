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
TestYourResourceModel API Service Test Suite
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from wsgi import app
from service.common import status
from service.models.order import db, Order
from .factories import OrderFactory, ItemFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)

BASE_URL = "/orders"


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestOrderService(TestCase):
    """REST API Server Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Order).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  H E L P E R   M E T H O D S
    ######################################################################

    def _create_orders(self, count):
        """Factory method to create orders in bulk"""
        orders = []
        for _ in range(count):
            order = OrderFactory()
            resp = self.client.post(BASE_URL, json=order.serialize())
            self.assertEqual(
                resp.status_code,
                status.HTTP_201_CREATED,
                "Could not create test Order",
            )
            new_order = resp.get_json()
            order.id = new_order["id"]
            orders.append(order)
        return orders

    ######################################################################
    #  O R D E R   T E S T   C A S E S
    ######################################################################

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_create_order(self):
        """It should Create a new Order"""
        test_order = OrderFactory()
        logging.debug("Test Order: %s", test_order.serialize())
        response = self.client.post(BASE_URL, json=test_order.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_order = response.get_json()
        self.assertIn("id", new_order)
        self.assertEqual(new_order["customer_id"], test_order.customer_id)
        self.assertEqual(new_order["status"], test_order.status)
        expected_total = sum(
            float(item.price) * item.quantity for item in test_order.items
        )
        self.assertAlmostEqual(new_order["total_price"], expected_total, places=2)
        self.assertListEqual(
            [item["id"] for item in new_order["items"]],
            [item.id for item in test_order.items],
        )

        # # Check that the location header was correct
        # response = self.client.get(location)
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        # new_order = response.get_json()
        # self.assertIn("id", new_order)
        # self.assertEqual(new_order["customer_id"], test_order.customer_id)
        # self.assertEqual(new_order["status"], test_order.status)
        # self.assertEqual(new_order["total_price"], test_order.total_price)
        # self.assertListEqual(
        #     [item["id"] for item in new_order["items"]],
        #     [item.id for item in test_order.items],
        # )

    def test_get_order_list(self):
        """It should Get a list of Orders"""
        self._create_orders(5)
        resp = self.client.get(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 5)

    def test_bad_request(self):
        """It should not Create when sending the wrong data"""
        resp = self.client.post(BASE_URL, json={"name": "not enough data"})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unsupported_media_type(self):
        """It should not Create when sending wrong media type"""
        order = OrderFactory()
        resp = self.client.post(
            BASE_URL, json=order.serialize(), content_type="test/html"
        )
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_method_not_allowed(self):
        """It should not allow an illegal method call"""
        resp = self.client.put(BASE_URL, json={"not": "today"})
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_check_content_type(self):
        """check_content_type should 415 when Content-Type header is missing"""
        resp = self.client.post(BASE_URL)  # no headers
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_update_order(self):
        """It should Update an existing Order"""
        # create an Order to update
        test_order = OrderFactory()
        resp = self.client.post(BASE_URL, json=test_order.serialize())
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # update the order
        new_order = resp.get_json()
        new_order["status"] = "PENDING"
        new_order_id = new_order["id"]
        resp = self.client.put(f"{BASE_URL}/{new_order_id}", json=new_order)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_order = resp.get_json()
        self.assertEqual(updated_order["status"], "PENDING")

        new_order_2 = resp.get_json()
        new_order_2["status"] = "SHIPPED"
        new_order_id_2 = new_order_2["id"]
        resp = self.client.put(f"{BASE_URL}/{new_order_id_2}", json=new_order_2)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_order_2 = resp.get_json()
        self.assertEqual(updated_order_2["status"], "SHIPPED")

        new_order_3 = resp.get_json()
        new_order_3["total_price"] = 0.0
        new_order_3["items"] = []
        new_order_id_3 = new_order_3["id"]
        resp = self.client.put(f"{BASE_URL}/{new_order_id_3}", json=new_order_3)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_order_3 = resp.get_json()
        self.assertEqual(updated_order_3["total_price"], 0.0)
        self.assertListEqual(updated_order_3["items"], [])

    def test_update_order_not_found_returns_404(self):
        """PUT /orders/<id> should 404 when the order does not exist"""
        payload = {
            "customer_id": 1,
            "status": "PENDING",
            "total_price": 0.0,
            "items": [],
        }
        resp = self.client.put(f"{BASE_URL}/999999", json=payload)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_order(self):
        """It should Delete an Order"""
        # Create a test order first
        test_order = OrderFactory()
        test_order.create()
        order_id = test_order.id

        # Verify the order exists
        self.assertIsNotNone(Order.find(order_id))

        # Delete the order
        response = self.client.delete(f"{BASE_URL}/{order_id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verify the order is deleted
        self.assertIsNone(Order.find(order_id))

    def test_delete_order_not_found(self):
        """It should return 404 when deleting a non-existent Order"""
        # Try to delete a non-existent order
        response = self.client.delete(f"{BASE_URL}/999")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_order(self):
        """It should Get an Order by ID"""
        # create an Order to get
        test_order = OrderFactory()
        resp = self.client.post(BASE_URL, json=test_order.serialize())
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        new_order = resp.get_json()
        new_order_id = new_order["id"]

        # get the order
        resp = self.client.get(f"{BASE_URL}/{new_order_id}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        order = resp.get_json()
        self.assertEqual(order["id"], new_order_id)
        self.assertEqual(order["customer_id"], test_order.customer_id)
        self.assertEqual(order["status"], test_order.status)
        expected_total = sum(
            float(item.price) * item.quantity for item in test_order.items
        )
        self.assertAlmostEqual(order["total_price"], expected_total, places=2)
        self.assertListEqual(
            [item["id"] for item in order["items"]],
            [item.id for item in test_order.items],
        )

    def test_get_order_not_found(self):
        """It should return 404 when the Order is not found"""
        resp = self.client.get(f"{BASE_URL}/999")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_order_internal_server_error(self):
        """It should return 500 when there is a server error"""
        with self.assertRaises(Exception):
            resp = self.client.get(f"{BASE_URL}/error")
            self.assertEqual(resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    ######################################################################
    #  I T E M   T E S T   C A S E S
    ######################################################################

    def test_add_item(self):
        """It should Add an item to an order"""
        order = self._create_orders(1)[0]
        item = ItemFactory()
        resp = self.client.post(
            f"{BASE_URL}/{order.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = resp.headers.get("Location", None)
        self.assertIsNotNone(location)

        data = resp.get_json()
        logging.debug(data)
        self.assertEqual(data["order_id"], order.id)
        self.assertEqual(data["name"], item.name)
        self.assertEqual(data["category"], item.category)
        self.assertEqual(data["description"], item.description)
        self.assertEqual(data["price"], float(item.price))
        self.assertEqual(data["quantity"], item.quantity)

        # # Check that the location header was correct by getting it
        # resp = self.client.get(location, content_type="application/json")
        # self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # new_item = resp.get_json()
        # self.assertEqual(new_item["name"], item.name, "Item name does not match")

    def test_get_item(self):
        """It should Get an item from an order"""
        # create a known item
        order = self._create_orders(1)[0]
        item = ItemFactory()
        resp = self.client.post(
            f"{BASE_URL}/{order.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        data = resp.get_json()
        logging.debug(data)
        item_id = data["id"]

        # retrieve it back
        resp = self.client.get(
            f"{BASE_URL}/{order.id}/items/{item_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        logging.debug(data)
        self.assertEqual(data["order_id"], order.id)
        self.assertEqual(data["name"], item.name)
        self.assertEqual(data["category"], item.category)
        self.assertEqual(data["description"], item.description)
        self.assertEqual(data["price"], float(item.price))
        self.assertEqual(data["quantity"], item.quantity)
