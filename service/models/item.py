"""
Models for Item

All of the models are stored in this module
"""

import logging
from decimal import Decimal
from .persistent_base import PersistentBase, DataValidationError, db

logger = logging.getLogger("flask.app")


class Item(db.Model, PersistentBase):  # pylint: disable=too-many-instance-attributes
    """
    Class that represents an Item
    """

    __tablename__ = "item"

    ##################################################
    # Table Schema
    ##################################################
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(63))
    category = db.Column(db.String(63))
    product_id = db.Column(db.BigInteger, nullable=False)
    description = db.Column(db.String(1023))
    price = db.Column(db.Numeric(14, 2), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id", ondelete="CASCADE"))

    def __repr__(self):
        return f" Item {self.name} id=[{self.id}]>"

    def serialize(self):
        """Serializes an Item into a dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "product_id": self.product_id,
            "price": str(self.price),
            "order_id": self.order_id,
            "quantity": self.quantity,
        }

    def deserialize(self, data):
        """
        Deserializes an Item from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.id = data.get("id", None)
            self.name = data["name"]
            self.category = data["category"]
            self.description = data["description"]
            raw_price = data["price"]
            if raw_price == "None":
                self.price = None
            elif isinstance(raw_price, str):
                self.price = Decimal(raw_price)
            else:
                raise TypeError("Invalid price type")
            self.product_id = data["product_id"]
            self.order_id = data["order_id"]
            self.quantity = data.get("quantity", 1)
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid Item: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Item: body of request contained bad or no data " + str(error)
            ) from error
        return self

    ##################################################
    # CLASS METHODS
    ##################################################
    @classmethod
    def find_by_name(cls, name):
        """Returns all Item with the given name

        Args:
            name (string): the name of the Item you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)

    @classmethod
    def find_by_order_id(cls, order_id):
        """Returns all Items with the given order_id

        Args:
            order_id (int): the order_id of the Items you want to match
        """
        logger.info("Processing order_id query for %s ...", order_id)
        return cls.query.filter(cls.order_id == order_id)
