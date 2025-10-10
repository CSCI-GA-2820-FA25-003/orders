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
BASE_URL = "/items"


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
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    # Todo: Add your test cases here...
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

        # TODO: uncomment this code when get_orders is implemented
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

    def test_create_item(self):
        """It should Create a new Item"""
        test_item = ItemFactory()
        logging.debug("Test Item: %s", test_item.serialize())
        response = self.client.post(BASE_URL, json=test_item.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_item = response.get_json()
        self.assertEqual(new_item["name"], test_item.name)
        self.assertEqual(new_item["category"], test_item.category)
        self.assertEqual(new_item["description"], test_item.description)
        self.assertEqual(new_item["price"], test_item.price)
        self.assertEqual(new_item["quantity"], test_item.quantity)
        self.assertEqual(new_item["order_id"], test_item.order_id)

        # TODO: uncomment this code when get_items is implemented
        # # Check that the location header was correct
        # response = self.client.get(location)
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        # new_item = response.get_json()
        # self.assertEqual(new_item["name"], test_item.name)
        # self.assertEqual(new_item["category"], test_item.category)
        # self.assertEqual(new_item["description"], test_item.description)
        # self.assertEqual(new_item["price"], test_item.price)
        # self.assertEqual(new_item["quantity"], test_item.quantity)
        # self.assertEqual(new_item["order_id"], test_item.order_id)
