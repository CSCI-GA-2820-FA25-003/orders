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
Orders Service with Flask-RESTx

This service implements a REST API that allows you to Create, Read, Update
and Delete Orders and Items using Flask-RESTx for Swagger/OpenAPI documentation
"""

from flask import jsonify, request, abort, url_for, current_app as app
from flask_restx import Api, Resource, fields, reqparse, inputs
from service.models.order import Order, OrderStatus
from service.models.item import Item
from service.common import status  # HTTP Status Codes


@app.route("/health")
def health_check():
    """Let them know our heart is still beating"""
    return jsonify(status=200, message="Healthy"), status.HTTP_200_OK


@app.route("/")
def index():
    """Root URL response for Orders Service"""
    app.logger.info("Request for the root URL")
    return (
        jsonify(
            name="Orders REST API Service",
            version="1.0",
            docs=f"{request.url_root}apidocs",
        ),
        status.HTTP_200_OK,
    )


@app.route("/home")
def home():
    """Home page"""
    return app.send_static_file("index.html")


api = Api(
    app,
    version="1.0",
    title="Orders REST API Service",
    description="This service implements a REST API for Orders management",
    doc="/apidocs",
)


######################################################################
# API INITIALIZATION
######################################################################
order_ns = api.namespace("orders", description="Order operations")
# Не используем параметры в определении namespace, вместо этого используем @ns.param в ресурсах
item_ns = api.namespace("items", description="Item operations")

# Переопределим маршруты для item_ns, чтобы работать с /orders/{order_id}/items
def item_url(order_id):
    """Возвращает URL для item operations"""
    return f"{BASE_URL}/{order_id}/items"

# Определим базовый URL для API
BASE_URL = "/orders"

######################################################################
######################################################################
# API Models
######################################################################


item_model = api.model(
    "Item",
    {
        "id": fields.Integer(
            readonly=True, description="The unique ID assigned to an Item"
        ),
        "name": fields.String(required=True, description="The name of the Item"),
        "category": fields.String(
            required=True, description="The category of the Item"
        ),
        "description": fields.String(
            required=True, description="The description of the Item"
        ),
        "product_id": fields.Integer(
            required=True, description="The product ID of the Item"
        ),
        "price": fields.String(required=True, description="The price of the Item"),
        "quantity": fields.Integer(default=1, description="The quantity of the Item"),
        "order_id": fields.Integer(
            required=True, description="The order ID that the Item belongs to"
        ),
    },
)

# Item creation model (without id)
item_create_model = api.model(
    "ItemCreate",
    {
        "name": fields.String(required=True, description="The name of the Item"),
        "category": fields.String(
            required=True, description="The category of the Item"
        ),
        "description": fields.String(
            required=True, description="The description of the Item"
        ),
        "product_id": fields.Integer(
            required=True, description="The product ID of the Item"
        ),
        "price": fields.String(required=True, description="The price of the Item"),
        "quantity": fields.Integer(default=1, description="The quantity of the Item"),
        "order_id": fields.Integer(
            required=True, description="The order ID that the Item belongs to"
        ),
    },
)

# Order model
order_model = api.model(
    "Order",
    {
        "id": fields.Integer(
            readonly=True, description="The unique ID assigned to an Order"
        ),
        "customer_id": fields.Integer(
            required=True, description="The customer ID of the Order"
        ),
        "status": fields.String(
            enum=[e.value for e in OrderStatus], description="The status of the Order"
        ),
        "total_price": fields.String(
            readonly=True, description="The total price of the Order"
        ),
        "items": fields.List(
            fields.Nested(item_model), description="The items in the Order"
        ),
    },
)

# Order creation model
order_create_model = api.model(
    "OrderCreate",
    {
        "customer_id": fields.Integer(
            required=True, description="The customer ID of the Order"
        ),
        "status": fields.String(
            enum=[e.value for e in OrderStatus], description="The status of the Order"
        ),
        "total_price": fields.String(description="The total price of the Order"),
        "items": fields.List(
            fields.Nested(item_create_model), description="The items in the Order"
        ),
    },
)

# Define request parsers
order_list_parser = reqparse.RequestParser()
order_list_parser.add_argument("customer_id", type=int, help="Filter by customer ID")
order_list_parser.add_argument("status", type=str, help="Filter by order status")
order_list_parser.add_argument("min_total", type=float, help="Minimum total price")
order_list_parser.add_argument("max_total", type=float, help="Maximum total price")

# Item list request parser
item_list_parser = reqparse.RequestParser()
item_list_parser.add_argument("category", type=str, help="Filter by item category")
item_list_parser.add_argument(
    "name", type=str, help="Filter by item name (substring match)"
)
item_list_parser.add_argument(
    "description", type=str, help="Filter by item description (substring match)"
)
item_list_parser.add_argument("product_id", type=int, help="Filter by product ID")
item_list_parser.add_argument("min_price", type=float, help="Minimum item price")
item_list_parser.add_argument("max_price", type=float, help="Maximum item price")
item_list_parser.add_argument("quantity", type=int, help="Filter by item quantity")


# Helper function for applying string filters
def _apply_string_filters(query, args):
    """Apply string-based filters (category, name, description)"""
    if args.category:
        query = query.filter(Item.category.ilike(args.category))

    if args.name:
        query = query.filter(Item.name.ilike(f"%{args.name}%"))

    if args.description:
        query = query.filter(Item.description.ilike(f"%{args.description}%"))

    return query


# Helper function for applying numeric filters
def _apply_numeric_filters(query, args):
    """Apply numeric filters (product_id, quantity, price range)"""
    if args.product_id:
        query = query.filter(Item.product_id == args.product_id)

    if args.quantity:
        query = query.filter(Item.quantity == args.quantity)

    if args.min_price:
        query = query.filter(Item.price >= args.min_price)

    if args.max_price:
        query = query.filter(Item.price <= args.max_price)

    return query


# Define a model for repeat order response
repeat_order_response = api.model(
    "RepeatOrderResponse",
    {
        "order_id": fields.Integer(description="The ID of the newly created order"),
        "status": fields.String(description="The status of the newly created order"),
    },
)


# All Order resource classes have been moved inside init_api function


# READ AN ORDER is now part of OrderResource class above


# UPDATE AN EXISTING ORDER is now part of OrderResource class above


# DELETE AN ORDER is now part of OrderResource class above


# ---------------------------------------------------------------------
#                I T E M   M E T H O D S
# ---------------------------------------------------------------------

# All Item methods have been moved inside the init_api function


# Item collection class has been moved inside the init_api function


# Item resource class has been moved inside the init_api function


# All Item endpoints have been moved to the respective classes inside init_api function


######################################################################
# ORDER RESOURCE CLASSES
######################################################################


# ORDER COLLECTION RESOURCE
@order_ns.route("", strict_slashes=False)
class OrderCollection(Resource):
    """Handle all interactions with Order collection"""

    @order_ns.doc("list_orders")
    @order_ns.expect(order_list_parser)
    @order_ns.marshal_list_with(order_model)
    def get(self):
        """Lists all of the Orders with optional filtering"""
        app.logger.info("Request for Order list with filters: %s", request.args)

        args = order_list_parser.parse_args()
        query = Order.query

        # customer_id
        if args.customer_id:
            query = query.filter(Order.customer_id == args.customer_id)

        # status
        if args.status:
            try:
                valid_status = OrderStatus(args.status)
                query = query.filter(Order.status == valid_status)
            except ValueError:
                order_ns.abort(
                    status.HTTP_400_BAD_REQUEST,
                    f"Invalid status value: {args.status}. "
                    f"Must be one of {[s.value for s in OrderStatus]}",
                )

        # price range
        if args.min_total is not None:
            query = query.filter(Order.total_price >= args.min_total)
        if args.max_total is not None:
            query = query.filter(Order.total_price <= args.max_total)

        orders = query.all()
        return [order.serialize() for order in orders]

    @order_ns.doc("create_order")
    @order_ns.expect(order_create_model)
    @order_ns.response(201, "Order created", order_model)
    @order_ns.marshal_with(order_model, code=201)
    def post(self):
        """Create an Order"""
        app.logger.info("Request to Create an Order...")

        order = Order()
        # Get the data from the request and deserialize it
        app.logger.info("Processing: %s", api.payload)
        order.deserialize(api.payload)

        # Save the new Order to the database
        order.create()
        app.logger.info("Order with new id [%s] saved!", order.id)

        return (
            order.serialize(),
            201,
            {"Location": api.url_for(OrderResource, order_id=order.id)},
        )


# ORDER RESOURCE BY ID
@order_ns.route("/<int:order_id>", strict_slashes=False)
@order_ns.param("order_id", "The Order identifier")
class OrderResource(Resource):
    """Handle all interactions with a single Order"""

    @order_ns.doc("get_order")
    @order_ns.response(404, "Order not found")
    @order_ns.marshal_with(order_model)
    def get(self, order_id):
        """Get an Order by ID"""
        app.logger.info("Request for order with id: %s", order_id)
        # Retrieve the order from the database
        order = Order.find(order_id)
        if not order:
            order_ns.abort(
                status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found."
            )
        return order.serialize()

    @order_ns.doc("update_order")
    @order_ns.expect(order_create_model)
    @order_ns.response(404, "Order not found")
    @order_ns.marshal_with(order_model)
    def put(self, order_id):
        """Update an Order"""
        app.logger.info("Request to update order with id: %s", order_id)

        # See if the order exists and abort if it doesn't
        order = Order.find(order_id)
        if not order:
            order_ns.abort(
                status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found."
            )

        # Update from the json in the body of the request
        order.deserialize(api.payload)
        order.id = order_id
        order.update()

        return order.serialize()

    @order_ns.doc("delete_order")
    @order_ns.response(204, "Order deleted")
    def delete(self, order_id):
        """Delete an Order"""
        app.logger.info("Request to delete order with id: %s", order_id)

        # Retrieve the order to delete and delete it if it exists
        order = Order.find(order_id)
        if order:
            order.delete()
            app.logger.info("Order with id [%s] deleted!", order_id)

        return "", status.HTTP_204_NO_CONTENT


######################################################################
# ITEM RESOURCE CLASSES
######################################################################


# Регистрация item ресурсов в основном API с правильным путем
# Маршрут для коллекции элементов
@order_ns.route("/<int:order_id>/items", strict_slashes=False)
@order_ns.param("order_id", "The Order identifier")
class ItemCollection(Resource):
    """Handle all interactions with collections of Items"""

    @order_ns.doc("list_items")
    @order_ns.expect(item_list_parser)
    @order_ns.marshal_list_with(item_model)
    def get(self, order_id):
        """List all Items for a given Order"""
        app.logger.info(
            "Request to list Items for Order id: %s with filters: %s",
            order_id,
            request.args,
        )

        # See if the order exists and abort if it doesn't
        order = Order.find(order_id)
        if not order:
            item_ns.abort(
                status.HTTP_404_NOT_FOUND,
                f"Order with id '{order_id}' could not be found.",
            )

        # Parse arguments
        args = item_list_parser.parse_args()

        # Start with base query for items in this order
        query = Item.query.filter(Item.order_id == order_id)

        # Apply filters
        query = _apply_string_filters(query, args)
        query = _apply_numeric_filters(query, args)

        # Execute query
        items = query.all()

        # Return as an array of dictionaries
        return [item.serialize() for item in items]

    @item_ns.doc("create_item")
    @item_ns.expect(item_create_model)
    @item_ns.response(201, "Item created", item_model)
    @item_ns.marshal_with(item_model, code=201)
    def post(self, order_id):
        """Create an Item on an Order"""
        app.logger.info("Request to create an Item for Order with id: %s", order_id)

        # See if the order exists and abort if it doesn't
        order = Order.find(order_id)
        if not order:
            item_ns.abort(
                status.HTTP_404_NOT_FOUND,
                f"Order with id '{order_id}' could not be found.",
            )

        # Create an item from the json data
        item = Item()
        data = api.payload
        data["order_id"] = order_id  # Set the order_id from the path parameter
        item.deserialize(data)

        # Append the item to the order
        order.items.append(item)
        order.update()

        return (
            item.serialize(),
            201,
            {"Location": api.url_for(ItemResource, order_id=order_id, item_id=item.id)},
        )


# ITEM RESOURCE BY ID
@item_ns.route("/<int:item_id>", strict_slashes=False)
@item_ns.param("order_id", "The Order identifier")
@item_ns.param("item_id", "The Item identifier")
class ItemResource(Resource):
    """Handle all interactions with a single Item"""

    @item_ns.doc("get_item")
    @item_ns.response(404, "Item not found")
    @item_ns.marshal_with(item_model)
    def get(self, order_id, item_id):
        """Get an Item"""
        app.logger.info(
            "Request to retrieve Item %s for Order id: %s", (item_id, order_id)
        )

        # See if the item exists and abort if it doesn't
        item = Item.find(item_id)
        if not item:
            item_ns.abort(
                status.HTTP_404_NOT_FOUND,
                f"Item with id '{item_id}' could not be found.",
            )

        return item.serialize()

    @item_ns.doc("update_item")
    @item_ns.expect(item_create_model)
    @item_ns.response(404, "Item not found")
    @item_ns.marshal_with(item_model)
    def put(self, order_id, item_id):
        """Update an Item"""
        app.logger.info(
            "Request to update Item %s for Order id: %s", (item_id, order_id)
        )

        # See if the item exists and abort if it doesn't
        item = Item.find(item_id)
        if not item:
            item_ns.abort(
                status.HTTP_404_NOT_FOUND,
                f"Item with id '{item_id}' could not be found.",
            )

        # Update from the json in the body of the request
        data = api.payload
        data["order_id"] = order_id  # Set the order_id from the path parameter
        item.deserialize(data)
        item.id = item_id
        item.update()

        return item.serialize()

    @item_ns.doc("delete_item")
    @item_ns.response(204, "Item deleted")
    def delete(self, order_id, item_id):
        """Delete an Item"""
        app.logger.info(
            "Request to delete Item %s for Order id: %s", (item_id, order_id)
        )

        # See if the item exists and delete it if it does
        order = Order.find(order_id)
        item = Item.find(item_id)
        if item:
            item.delete()
            order.update()

        return "", status.HTTP_204_NO_CONTENT


######################################################################
# ORDER ACTIONS
######################################################################
@order_ns.route("/<int:order_id>/cancel", strict_slashes=False)
@order_ns.param("order_id", "The Order identifier")
class CancelOrderResource(Resource):
    """Cancel an Order"""

    @order_ns.doc("cancel_order")
    @order_ns.response(200, "Order canceled")
    @order_ns.response(400, "Cannot cancel shipped or delivered orders")
    @order_ns.response(404, "Order not found")
    def put(self, order_id):
        """Cancel an Order"""
        order = Order.find(order_id)

        if not order:
            order_ns.abort(
                status.HTTP_404_NOT_FOUND,
                f"Order with id '{order_id}' could not be found.",
            )

        if order.status in [OrderStatus.DELIVERED, OrderStatus.SHIPPED]:
            order_ns.abort(
                status.HTTP_400_BAD_REQUEST,
                "Orders that have already been shipped or delivered can't be cancelled.",
            )

        order.status = OrderStatus.CANCELED
        order.update()

        return "", status.HTTP_200_OK


# REPEAT ORDER RESOURCE
@order_ns.route("/<int:order_id>/repeat", strict_slashes=False)
@order_ns.param("order_id", "The Order identifier")
class RepeatOrderResource(Resource):
    """Repeat an existing Order"""

    @order_ns.doc("repeat_order")
    @order_ns.response(201, "Order repeated", repeat_order_response)
    @order_ns.response(400, "Cannot repeat cancelled orders")
    @order_ns.response(404, "Order not found")
    @order_ns.marshal_with(repeat_order_response, code=201)
    def post(self, order_id):
        """Repeat a previous Order"""
        app.logger.info("Request to repeat Order with id: %s", order_id)

        order = Order.find(order_id)
        if not order:
            order_ns.abort(
                status.HTTP_404_NOT_FOUND,
                f"Order with id '{order_id}' could not be found.",
            )

        if order.status == OrderStatus.CANCELED:
            order_ns.abort(
                status.HTTP_400_BAD_REQUEST, "Cannot repeat a cancelled order."
            )

        new_order = Order()
        new_order.customer_id = order.customer_id
        new_order.status = OrderStatus.PENDING
        new_order.create()

        for item in order.items:
            new_item = Item()
            new_item.name = item.name
            new_item.category = item.category
            new_item.description = item.description
            new_item.product_id = item.product_id
            new_item.quantity = item.quantity
            new_item.price = item.price
            new_item.order_id = new_order.id
            new_item.create()

        response = {
            "order_id": new_order.id,
            "status": new_order.status.value,
        }
        return response, status.HTTP_201_CREATED


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def check_content_type(content_type) -> None:
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )


######################################################################
# Flask Basic Routes (defined after API routes to avoid conflicts)
######################################################################
