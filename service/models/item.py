"""
Models for Item

All of the models are stored in this module
"""

import logging
from flask_sqlalchemy import SQLAlchemy
from .persistent_base import PersistentBase, DataValidationError, db

logger = logging.getLogger("flask.app")


class Item(db.Model, PersistentBase):
    """
    Class that represents an Item
    """

    __tablename__ = "items"

    ##################################################
    # Table Schema
    ##################################################
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(63))
    category = db.Column(db.String(63))
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
            "price": float(self.price),
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
            self.id = data["id"]
            self.name = data["name"]
            self.category = data["category"]
            self.description = data["description"]
            self.price = data["price"]
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
    def all(cls):
        """Returns all of the Item in the database"""
        logger.info("Processing all Item")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds a Item by it's ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.session.get(cls, by_id)

    @classmethod
    def find_by_name(cls, name):
        """Returns all Item with the given name

        Args:
            name (string): the name of the Item you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)
