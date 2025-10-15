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
from unittest import TestCase
from wsgi import app
from service.models.item import Item, DataValidationError, db
from service.models.order import Order
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
        db.session.query(Item).delete()  # clean up the last tests
        db.session.query(Order).delete()
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_add_order_item(self):
        """It should create an order with an item and add it to the database"""
        orders = Order.all()
        self.assertEqual(orders, [])
        order = OrderFactory()
        item = ItemFactory()
        # associate item with order
        order.items.append(item)
        order.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(order.id)
        orders = Order.all()
        self.assertEqual(len(orders), 1)

        new_order = Order.find(order.id)
        # items on the order should include the appended item's id
        self.assertEqual(new_order.items[0], item)

    def test_update_order_item(self):
        """It should update an order's item (via item fields)"""
        orders = Order.all()
        self.assertEqual(orders, [])

        order = OrderFactory()
        item = ItemFactory()
        order.create()
        # associate after create (items stored as ids on Order)
        order.items.append(item)
        order.update()

        # Fetch it back
        order = Order.find(order.id)
        self.assertEqual(order.items[0], item)

        # change item fields and update
        item = order.items[0]
        item.quantity = 3
        item.update()
        order.update()

        order = Order.find(order.id)
        self.assertEqual(order.items[0].quantity, 3)
        self.assertEqual(order.items[0].name, item.name)
        self.assertEqual(order.items[0].description, item.description)
        self.assertEqual(order.items[0].product_id, item.product_id)
        self.assertEqual(order.items[0].price, item.price)
        self.assertEqual(order.items[0].category, item.category)

    def test_delete_order_item(self):
        """It should remove an item from an order"""
        orders = Order.all()
        self.assertEqual(orders, [])
        order = OrderFactory()
        item = ItemFactory()
        order.items.append(item)
        order.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(order.id)
        orders = Order.all()
        self.assertEqual(len(orders), 1)

        # Fetch it back
        order = Order.find(order.id)
        # remove item id from order and update
        item = order.items[0]
        item.delete()
        order.update()

        # Fetch it back again
        order = Order.find(order.id)
        self.assertEqual(len(order.items), 0)

    def test_serialize_an_item(self):
        """It should serialize an Item"""
        item = ItemFactory()
        serial_item = item.serialize()
        self.assertEqual(serial_item["id"], item.id)
        self.assertEqual(serial_item["name"], item.name)
        self.assertEqual(serial_item["category"], item.category)
        self.assertEqual(serial_item["description"], item.description)
        self.assertEqual(serial_item["product_id"], item.product_id)
        self.assertEqual(serial_item["price"], float(item.price))
        self.assertEqual(serial_item["order_id"], item.order_id)
        self.assertEqual(serial_item["quantity"], item.quantity)

    def test_deserialize_an_item(self):
        """It should deserialize an Item"""
        order = OrderFactory()
        order.create()

        item = ItemFactory(order_id=order.id)
        item.create()

        new_item = Item()
        new_item.deserialize(item.serialize())

        self.assertEqual(new_item.id, item.id)
        self.assertEqual(new_item.name, item.name)
        self.assertEqual(new_item.category, item.category)
        self.assertEqual(new_item.description, item.description)
        self.assertEqual(new_item.product_id, item.product_id)
        self.assertEqual(float(new_item.price), float(item.price))
        self.assertEqual(new_item.order_id, item.order_id)
        self.assertEqual(new_item.quantity, item.quantity)

    def test_total_price_calculation(self):
        """It should calculate total price based on items"""
        order = OrderFactory()
        item1 = ItemFactory(price=10.00)
        item2 = ItemFactory(price=15.50)
        item3 = ItemFactory(price=4.75)
        order.items.extend([item1, item2, item3])
        order.create()
        price = (
            item1.price * item1.quantity
            + item2.price * item2.quantity
            + item3.price * item3.quantity
        )
        self.assertEqual(order.total_price, price)

    def test_item_repr(self):
        """__repr__ should include the name and id"""
        order = OrderFactory()
        order.create()
        item = ItemFactory(order_id=order.id)
        s = repr(item)
        self.assertIn(item.name, s)
        self.assertIn(str(item.id), s)

    def test_item_deserialize_missing_field_raises(self):
        """deserialize should raise DataValidationError on missing required key"""
        order = OrderFactory()
        order.create()
        bad_payload = {
            "id": 1,
            # no "name" field
            "category": "Books",
            "description": "test",
            "product_id": 1234,
            "price": 12.34,
            "order_id": order.id,
            "quantity": 1,
        }
        with self.assertRaises(DataValidationError):
            Item().deserialize(bad_payload)

    def test_item_deserialize_no_body_raises(self):
        """deserialize should raise DataValidationError when body is None"""
        with self.assertRaises(DataValidationError):
            Item().deserialize(None)

    def test_item_all_and_find(self):
        """all() and find() should return created items"""
        order = OrderFactory()
        order.create()
        i1 = ItemFactory(order_id=order.id)
        i2 = ItemFactory(order_id=order.id)
        i1.create()
        i2.create()

        items = Item.all()
        self.assertGreaterEqual(len(items), 2)

        found = Item.find(i1.id)
        self.assertIsNotNone(found)
        self.assertEqual(found.id, i1.id)
