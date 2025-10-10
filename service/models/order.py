"""
Models for Order

All of the models are stored in this module
"""

import logging
from flask_sqlalchemy import SQLAlchemy
from .persistent_base import PersistentBase, DataValidationError, db
from .item import Item
from enum import Enum

logger = logging.getLogger("flask.app")


class OrderStatus(str, Enum):
    """Order Status Enum"""

    PENDING = "PENDING"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELED = "CANCELED"


class Order(db.Model, PersistentBase):
    """
    Class that represents an Order
    """

    __tablename__ = "order"
    ##################################################
    # Table Schema
    ##################################################
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, nullable=False)
    status = db.Column(
        db.Enum(OrderStatus, native=False, length=30),
        default=OrderStatus.PENDING,
        nullable=False,
    )
    total_price = db.Column(db.Float, nullable=False)
    items = db.relationship("Item", backref="order", lazy=True, passive_deletes=True)

    def __repr__(self):
        return f" Order of the customer {self.customer_id} with order_id=[{self.id}]>"

    def create(self):
        self.total_price = sum(float(item.price) * item.quantity for item in self.items)
        super().create()

    def update(self):
        self.total_price = sum(float(item.price) * item.quantity for item in self.items)
        super().update()

    def serialize(self):
        """Serializes a Order into a dictionary"""
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "status": self.status,
            "total_price": self.total_price,
            "items": [item.id for item in self.items],
        }

    def deserialize(self, data):
        """
        Deserializes a Order from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.id = data["id"]
            self.customer_id = data["customer_id"]
            self.status = data["status"]
            self.total_price = data["total_price"]
            self.items = data["items"]
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid Order: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Order: body of request contained bad or no data " + str(error)
            ) from error
        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def all(cls):
        """Returns all of the Orders in the database"""
        logger.info("Processing all Orders")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds a Order by it's ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.session.get(cls, by_id)

    @classmethod
    def find_by_name(cls, name):
        """Returns all Orders with the given name

        Args:
            name (string): the name of the Orders you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)
