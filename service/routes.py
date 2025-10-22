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
YourResourceModel Service

This service implements a REST API that allows you to Create, Read, Update
and Delete YourResourceModel
"""

from flask import jsonify, request, abort, url_for
from flask import current_app as app  # Import Flask application
from service.models.order import Order, OrderStatus
from service.models.item import Item
from service.common import status  # HTTP Status Codes


######################################################################
# GET HEALTH CHECK
######################################################################
@app.route("/health")
def health_check():
    """Let them know our heart is still beating"""
    return jsonify(status=200, message="Healthy"), status.HTTP_200_OK


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response for Orders Service"""
    app.logger.info("Request for the root URL")
    return (
        jsonify(
            name="Orders REST API Service",
            version="1.0",
            paths=url_for("list_orders", _external=True),
        ),
        status.HTTP_200_OK,
    )


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


######################################################################
# CREATE A NEW ORDER
######################################################################
@app.route("/orders", methods=["POST"])
def create_orders():
    """
    Create an Order
    This endpoint will create an Order based the data in the body that is posted
    """
    app.logger.info("Request to Create an Order...")
    check_content_type("application/json")

    order = Order()
    # Get the data from the request and deserialize it
    data = request.get_json()
    app.logger.info("Processing: %s", data)
    order.deserialize(data)

    # Save the new Order to the database
    order.create()
    app.logger.info("Order with new id [%s] saved!", order.id)

    # Return the location of the new Order
    location_url = url_for("list_orders", order_id=order.id, _external=True)
    return (
        jsonify(order.serialize()),
        status.HTTP_201_CREATED,
        {"Location": location_url},
    )


######################################################################
# LIST ALL ORDERS WITH OPTIONAL FILTERS
######################################################################
@app.route("/orders", methods=["GET"])
def list_orders():
    """
    Lists all of the Orders with optional filtering by:
      - customer_id (int)
      - status (OrderStatus enum)
      - min_total / max_total (float range)
    """
    app.logger.info("Request for Order list with filters: %s", request.args)

    query = Order.query

    allowed_params = {"customer_id", "status", "min_total", "max_total"}
    unknown_params = set(request.args.keys()) - allowed_params
    if unknown_params:
        abort(
            status.HTTP_400_BAD_REQUEST,
            f"Invalid query parameters: {', '.join(unknown_params)}",
        )

    # customer_id
    customer_id = request.args.get("customer_id", type=int)
    if customer_id is not None:
        query = query.filter(Order.customer_id == customer_id)

    # status
    status_param = request.args.get("status")
    if status_param:
        try:
            valid_status = OrderStatus(status_param)
            query = query.filter(Order.status == valid_status)
        except ValueError:
            abort(
                status.HTTP_400_BAD_REQUEST,
                f"Invalid status value: {status_param}. "
                f"Must be one of {[s.value for s in OrderStatus]}",
            )

    # range
    min_total = request.args.get("min_total", type=float)
    max_total = request.args.get("max_total", type=float)
    if min_total is not None:
        query = query.filter(Order.total_price >= min_total)
    if max_total is not None:
        query = query.filter(Order.total_price <= max_total)

    orders = query.all()

    results = [order.serialize() for order in orders]

    return jsonify(results), status.HTTP_200_OK


######################################################################
# READ AN ORDER
######################################################################
@app.route("/orders/<int:order_id>", methods=["GET"])
def get_orders(order_id):
    """
    Read an Order

    This endpoint will read an Order based the id that is specified in the path
    """
    app.logger.info("Request for order with id: %s", order_id)
    # Retrieve the order from the database
    order = Order.find(order_id)
    if not order:
        abort(status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found.")

    return jsonify(order.serialize()), status.HTTP_200_OK


######################################################################
# UPDATE AN EXISTING ORDER
######################################################################


@app.route("/orders/<int:order_id>", methods=["PUT"])
def update_orders(order_id):
    """
    Update an Order

    This endpoint will update an Order based the body that is posted
    """
    app.logger.info("Request to update order with id: %s", order_id)
    check_content_type("application/json")

    # See if the order exists and abort if it doesn't
    order = Order.find(order_id)
    if not order:
        abort(status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found.")

    # Update from the json in the body of the request
    order.deserialize(request.get_json())
    order.id = order_id
    order.update()

    return jsonify(order.serialize()), status.HTTP_200_OK


######################################################################
# DELETE AN ORDER
######################################################################
@app.route("/orders/<int:order_id>", methods=["DELETE"])
def delete_orders(order_id):
    """
    Delete an Order

    This endpoint will delete an Order based the id specified in the path
    """
    app.logger.info("Request to delete order with id: %s", order_id)

    # Retrieve the order to delete and delete it if it exists
    order = Order.find(order_id)
    if not order:
        abort(status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found.")

    order.delete()
    app.logger.info("Order with id [%s] deleted!", order_id)

    return "", status.HTTP_204_NO_CONTENT


# ---------------------------------------------------------------------
#                I T E M   M E T H O D S
# ---------------------------------------------------------------------


######################################################################
# HELPER FUNCTIONS FOR ITEM FILTERING
######################################################################
def _validate_and_get_int_param(param_name, param_value):
    """Validate and return integer parameter value"""
    try:
        return int(param_value)
    except ValueError:
        abort(status.HTTP_400_BAD_REQUEST, f"{param_name} must be an integer")


def _validate_and_get_float_param(param_name, param_value):
    """Validate and return float parameter value"""
    try:
        return float(param_value)
    except ValueError:
        abort(status.HTTP_400_BAD_REQUEST, f"{param_name} must be a number")


def _apply_string_filters(query, args):
    """Apply string-based filters (category, name, description)"""
    category = args.get("category")
    if category:
        query = query.filter(Item.category.ilike(category))

    name = args.get("name")
    if name:
        query = query.filter(Item.name.ilike(f"%{name}%"))

    description = args.get("description")
    if description:
        query = query.filter(Item.description.ilike(f"%{description}%"))

    return query


def _apply_numeric_filters(query, args):
    """Apply numeric filters (product_id, quantity, price range)"""
    product_id_str = args.get("product_id")
    if product_id_str:
        product_id = _validate_and_get_int_param("product_id", product_id_str)
        query = query.filter(Item.product_id == product_id)

    quantity_str = args.get("quantity")
    if quantity_str:
        quantity = _validate_and_get_int_param("quantity", quantity_str)
        query = query.filter(Item.quantity == quantity)

    min_price_str = args.get("min_price")
    if min_price_str:
        min_price = _validate_and_get_float_param("min_price", min_price_str)
        query = query.filter(Item.price >= min_price)

    max_price_str = args.get("max_price")
    if max_price_str:
        max_price = _validate_and_get_float_param("max_price", max_price_str)
        query = query.filter(Item.price <= max_price)

    return query


######################################################################
# CREATE AN ITEM
######################################################################
@app.route("/orders/<int:order_id>/items", methods=["POST"])
def create_items(order_id):
    """
    Create an Item on an Order

    This endpoint will add an item to an order
    """
    app.logger.info("Request to create an Item for Order with id: %s", order_id)
    check_content_type("application/json")

    # See if the order exists and abort if it doesn't
    order = Order.find(order_id)
    if not order:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Order with id '{order_id}' could not be found.",
        )

    # Create an item from the json data
    item = Item()
    item.deserialize(request.get_json())

    # Append the item to the order
    order.items.append(item)
    order.update()

    # Prepare a message to return
    message = item.serialize()
    location_url = "unknown"

    # Send the location to GET the new item
    # location_url = url_for(
    #     "get_items", order_id=order.id, item_id=item.id, _external=True
    # )
    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
# LIST ALL ITEMS IN AN ORDER WITH OPTIONAL FILTERS
######################################################################
@app.route("/orders/<int:order_id>/items", methods=["GET"])
def list_items(order_id):
    """
    List all Items in an Order with optional filtering by:
      - category (string, case-insensitive exact match)
      - name (string, substring match)
      - description (string, substring match)
      - product_id (int, exact match)
      - min_price / max_price (float range, inclusive)
      - quantity (int, exact match)
    """
    app.logger.info(
        "Request to list Items for Order id: %s with filters: %s",
        order_id,
        request.args,
    )

    # See if the order exists and abort if it doesn't
    order = Order.find(order_id)
    if not order:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Order with id '{order_id}' could not be found.",
        )

    # Define allowed query parameters
    allowed_params = {
        "category",
        "name",
        "description",
        "product_id",
        "min_price",
        "max_price",
        "quantity",
    }
    unknown_params = set(request.args.keys()) - allowed_params
    if unknown_params:
        abort(
            status.HTTP_400_BAD_REQUEST,
            f"Invalid query parameters: {', '.join(unknown_params)}",
        )

    # Start with base query for items in this order
    query = Item.query.filter(Item.order_id == order_id)

    # Apply filters
    query = _apply_string_filters(query, request.args)
    query = _apply_numeric_filters(query, request.args)

    # Execute query
    items = query.all()

    # Return as an array of dictionaries
    results = [item.serialize() for item in items]

    return jsonify(results), status.HTTP_200_OK


######################################################################
# READ AN ITEM
######################################################################
@app.route("/orders/<int:order_id>/items/<int:item_id>", methods=["GET"])
def get_items(order_id, item_id):
    """
    Get an Item

    This endpoint returns just an item
    """
    app.logger.info("Request to retrieve Item %s for Order id: %s", (item_id, order_id))

    # See if the item exists and abort if it doesn't
    item = Item.find(item_id)
    if not item:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Item with id '{item_id}' could not be found.",
        )

    return jsonify(item.serialize()), status.HTTP_200_OK


######################################################################
# DELETE AN ITEM
######################################################################
@app.route("/orders/<int:order_id>/items/<int:item_id>", methods=["DELETE"])
def delete_items(order_id, item_id):
    """
    Delete an Item

    This endpoint will delete an Item based on the id specified in the path
    """
    app.logger.info("Request to delete Item %s for Order id: %s", (item_id, order_id))

    # See if the item exists and delete it if it does
    item = Item.find(item_id)
    if item:
        item.delete()

    return "", status.HTTP_204_NO_CONTENT


######################################################################
# UPDATE AN ITEM
######################################################################
@app.route("/orders/<int:order_id>/items/<int:item_id>", methods=["PUT"])
def update_items(order_id, item_id):
    """
    Update an Item

    This endpoint will update an Item based the body that is posted
    """
    app.logger.info("Request to update Item %s for Order id: %s", (item_id, order_id))
    check_content_type("application/json")

    # See if the item exists and abort if it doesn't
    item = Item.find(item_id)
    if not item:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Order with id '{item_id}' could not be found.",
        )

    # Update from the json in the body of the request
    item.deserialize(request.get_json())
    item.id = item_id
    item.update()

    return jsonify(item.serialize()), status.HTTP_200_OK


######################################################################
# ACTIONS
######################################################################


@app.route("/orders/<int:order_id>/cancel", methods=["PUT"])
def cancel_order(order_id: int):
    """
    Cancel an Order

    This endpoint will cancel an Order based on the id specified in the path
    """
    order = Order.find(order_id)

    if not order:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Order with id '{order_id}' could not be found.",
        )

    if order.status in [OrderStatus.DELIVERED, OrderStatus.SHIPPED]:
        abort(
            status.HTTP_400_BAD_REQUEST,
            "Orders that have already been shipped or delivered can’t be cancelled.",
        )

    order.status = OrderStatus.CANCELED
    order.update()

    return "", status.HTTP_200_OK


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


######################################################################
# Checks the ContentType of a request
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
