"""
Models for Order

All of the models are stored in this module
"""

import logging
from enum import Enum
from typing import List
from decimal import Decimal
from service.models.item import Item
from .persistent_base import PersistentBase, DataValidationError, db

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
    total_price = db.Column(db.Numeric(14, 2), nullable=False)
    items = db.relationship("Item", backref="order", lazy=True, passive_deletes=True)

    def __repr__(self):
        return f" Order of the customer {self.customer_id} with order_id=[{self.id}]>"

    def create(self):
        """Creates an Order to the database."""
        if self.items:
            self.total_price = sum(
                Decimal(item.price) * Decimal(item.quantity) for item in self.items
            )
        elif self.total_price is None:
            self.total_price = Decimal(0.0)
        super().create()

    def update(self):
        """Updates an Order in the database."""
        if self.items:
            self.total_price = sum(
                Decimal(item.price) * Decimal(item.quantity) for item in self.items
            )
        elif self.total_price is None:
            self.total_price = Decimal(0.0)
        super().update()

    def serialize(self):
        """Serializes a Order into a dictionary"""
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "status": self.status,
            "total_price": str(self.total_price),
            "items": [item.serialize() for item in self.items],
        }

    def deserialize(self, data):
        """
        Deserializes a Order from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.id = data.get("id", None)
            self.customer_id = data["customer_id"]
            self.status = data.get("status", OrderStatus.PENDING)
            raw_price = data["total_price"]
            if raw_price == "None":
                self.total_price = None
            elif isinstance(raw_price, str):
                self.total_price = Decimal(raw_price)
            else:
                raise TypeError("Invalid price type")

            incoming = data.get("items")
            if isinstance(incoming, list):
                if incoming and isinstance(incoming[0], dict):
                    built_items: List[Item] = []
                    for payload in incoming:
                        it = Item()
                        it.deserialize(payload)
                        built_items.append(it)
                    self.items = built_items
                else:
                    # not enough info to construct items, ignore
                    pass
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
