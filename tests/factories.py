"""Test factories for creating test data."""

import random
from decimal import Decimal
from factory import Factory, Sequence, Faker, post_generation, LazyFunction
from service.models.order import Order, OrderStatus
from service.models.item import Item


class OrderFactory(Factory):
    """Creates fake Order model instances for tests"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Meta class"""

        model = Order

    id = Sequence(lambda n: n + 1)
    customer_id = Sequence(lambda n: n + 1)
    status = OrderStatus.PENDING

    @post_generation
    def items(
        self, create, extracted, **kwargs
    ):  # pylint: disable=method-hidden, unused-argument
        """Creates the items list"""
        if not create:
            return

        if extracted:
            self.items = extracted


class ItemFactory(Factory):
    """Creates fake Item model instances for tests"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Meta class"""

        model = Item

    id = Sequence(lambda n: n + 1)
    name = Faker("word")
    category = Faker("word")
    product_id = LazyFunction(lambda: random.randint(1000, 9999))
    description = Faker("sentence")
    price = LazyFunction(lambda: Decimal(round(random.uniform(5.0, 100.0), 2)))
    quantity = LazyFunction(lambda: random.randint(1, 5))
    order_id = None
