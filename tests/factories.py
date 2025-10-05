"""
Test Factory to make fake objects for testing
"""

"""
Test Factory to make fake objects for testing
"""

import factory
import random
from decimal import Decimal
from service.models.orders import Order, OrderStatus
from service.models.items import Item


class OrderFactory(factory.Factory):
    """Creates fake Order model instances for tests"""

    class Meta:  # pylint: disable=too-few-public-methods
        model = Order

    id = factory.Sequence(lambda n: n + 1)
    customer_id = factory.Sequence(lambda n: n + 1)
    status = OrderStatus.PENDING
    total_price = factory.LazyFunction(
        lambda: float(round(random.uniform(10.0, 200.0), 2))
    )
    # items should be a list (relationship), default empty list per-instance
    items = factory.LazyFunction(list)


class ItemFactory(factory.Factory):
    """Creates fake Item model instances for tests"""

    class Meta:  # pylint: disable=too-few-public-methods
        model = Item

    id = factory.Sequence(lambda n: n + 1)
    name = factory.Faker("word")
    category = factory.Faker("word")
    description = factory.Faker("sentence")
    price = factory.LazyFunction(
        lambda: Decimal(str(round(random.uniform(1.0, 100.0), 2)))
    )
    quantity = factory.LazyFunction(lambda: random.randint(1, 5))
    order_id = factory.Sequence(lambda n: n + 1)
