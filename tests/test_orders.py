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
Test cases for Pet Model
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest.mock import patch, MagicMock
from unittest import TestCase
from wsgi import app
from service.models.order import Order, DataValidationError, db, OrderStatus
from .factories import OrderFactory, ItemFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  Orders   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestOrder(TestCase):
    """Test Cases for Orders Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Order).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create(self):
        """It should create an Order"""
        order = OrderFactory()
        order.create()
        self.assertIsNotNone(order.id)
        found = Order.all()
        self.assertEqual(len(found), 1)
        data = Order.find(order.id)
        self.assertEqual(data.id, order.id)
        self.assertEqual(data.status, order.status)
        self.assertEqual(data.customer_id, order.customer_id)
        self.assertEqual(data.items, order.items)

    @patch("service.models.order.db.session.commit")
    def test_failed_create(self, mocked_session):
        """It should catch a create exception"""
        mocked_session.side_effect = Exception("Failed to add to session")
        order = OrderFactory()
        with self.assertRaises(DataValidationError):
            order.create()

    def test_update(self):
        """It should update an Order"""
        order = OrderFactory()
        order.create()
        self.assertIsNotNone(order.id)

        order = Order.find(order.id)
        order.status = OrderStatus.DELIVERED
        order.update()

        order = Order.find(order.id)
        self.assertEqual(order.status, OrderStatus.DELIVERED)

    @patch("service.models.order.db.session.commit")
    def test_failed_update(self, mocked_session):
        """It should catch an update exception"""
        mocked_session.side_effect = Exception("Failed to add to session")
        order = OrderFactory()
        with self.assertRaises(DataValidationError):
            order.update()

    def test_delete(self):
        order = OrderFactory()
        order.create()
        order.delete()
        deleted_order = order.find(order.id)
        self.assertIsNone(deleted_order)

    @patch("service.models.order.db.session.commit")
    def test_failed_delete(self, mocked_session):
        """It should catch a delete exception"""
        mocked_session.side_effect = Exception("Failed to add to session")
        order = OrderFactory()
        with self.assertRaises(DataValidationError):
            order.delete()

    def test_find_by_id(self):
        """It should find an Order by id"""
        order = OrderFactory()
        order.create()
        found_order = order.find(order.id)
        self.assertIsNotNone(found_order)
        self.assertEqual(found_order.id, order.id)

    def test_serialize_order(self):
        """It should serialize an Order"""
        order = OrderFactory()
        order_dict = order.serialize()
        self.assertIsInstance(order_dict, dict)
        self.assertEqual(order_dict["id"], order.id)
        self.assertEqual(order_dict["status"], order.status)
        self.assertEqual(order_dict["customer_id"], order.customer_id)
        self.assertEqual(order_dict["items"], order.items)
        self.assertEqual(order_dict["total_price"], order.total_price)

    def test_deserialize_order(self):
        """It should deserialize an Order"""
        order = OrderFactory()
        order_dict = order.serialize()
        new_order = Order()
        new_order.deserialize(order_dict)
        self.assertEqual(new_order.id, order.id)
        self.assertEqual(new_order.status, order.status)
        self.assertEqual(new_order.customer_id, order.customer_id)
        self.assertEqual(new_order.items, order.items)
        self.assertEqual(new_order.total_price, order.total_price)

    def test_deserialize_with_key_error(self):
        """It should not Deserialize an order with a KeyError"""
        order = Order()
        self.assertRaises(DataValidationError, order.deserialize, {})

    def test_deserialize_with_type_error(self):
        """It should not Deserialize an order with a TypeError"""
        order = Order()
        self.assertRaises(DataValidationError, order.deserialize, [])
