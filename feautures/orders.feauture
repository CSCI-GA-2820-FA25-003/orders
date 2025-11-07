Feature: Order Management System
    As a Store Manager
    I need to manage customer orders
    So that I can process and track all orders efficiently

Background:
    Given the following orders exist
        | customer_id | status   | total_price |
        | 1001        | PENDING  | 999.99      |
        | 1002        | SHIPPED  | 1399.98     |
        | 1001        | PENDING  | 199.99      |
        | 1003        | CANCELED | 49.99       |

    And the following order items exist
        | name       | category   | product_id | description      | price  | quantity |
        | Laptop     | Electronics| 1001       | 15" Laptop      | 999.99 | 1        |
        | Smartphone | Electronics| 1002       | Latest model    | 699.99 | 2        |
        | Headphones | Electronics| 1003       | Noise cancelling| 199.99 | 1        |
        | Mouse      | Accessories| 1004       | Wireless mouse  | 49.99  | 1        |

Scenario: View all orders
    When I visit the "Orders Page"
    Then I should see "Order Management" in the title
    And I should see "1001" in the orders list
    And I should see "1002" in the orders list
    And I should see "1003" in the orders list

Scenario: Filter orders by customer ID
    When I visit the "Orders Page"
    And I set "Customer ID" to "1001"
    And I click the "Apply Filters" button
    Then I should see "1001" in the results
    And I should see 2 orders in the results
    And I should see "Laptop" in the order items
    And I should see "Headphones" in the order items

Scenario: Filter orders by status
    When I visit the "Orders Page"
    And I select "PENDING" from the status dropdown
    And I click the "Apply Filters" button
    Then I should see "PENDING" in the status filter
    And I should see "Laptop" in the results
    And I should not see "Smartphone" in the results


Scenario: Clear all filters
    When I visit the "Orders Page"
    And I set "Customer ID" to "1001"
    And I select "PENDING" from the status dropdown
    And I click the "Clear Filters" button
    Then the "Customer ID" field should be empty
    And the status dropdown should be reset


Scenario: Create a new order
    When I visit the "Orders Page"
    And I click the "Create New Order" button
    And I set "Customer ID" to "1004"
    And I click the "Add Item" button
    And I set "Item 1 Name" to "Keyboard"
    And I set "Item 1 Category" to "accessories"
    And I set "Item 1 Product ID" to "1005"
    And I set "Item 1 Description" to "Mechanical Keyboard"
    And I set "Item 1 Price" to "129.99"
    And I set "Item 1 Quantity" to "1"
    And I click the "Create Order" button
    Then I should see "Order created successfully" message
    When I search for customer "1004"
    Then I should see "Keyboard" in the order items
    And I should see "129.99" as the order total

Scenario: Update order status
    When I visit the "Orders Page"
    And I search for customer "1001" with status "PENDING"
    And I click the "Update Status" button
    And I select "SHIPPED" from the status dropdown
    And I click the "Save Changes" button
    Then I should see "Order status updated" message
    When I search for customer "1001" with status "SHIPPED"
    Then I should see "SHIPPED" in the status field

Scenario: Delete an existing order
    When I visit the "Orders Page"
    And I search for customer "1001" with status "PENDING"
    And I click the "Delete" button for order with items containing "Laptop"
    And I confirm the deletion
    Then I should see "Order deleted successfully" message
    When I search for customer "1001" with status "PENDING"
    Then I should not see "Laptop" in the order items
    And the order should no longer exist in the system

Scenario: Cancel an order
    When I visit the "Orders Page"
    And I search for customer "1001" with status "PENDING"
    And I click the "Cancel Order" button
    And I confirm the cancellation
    Then I should see "Order has been canceled" message
    When I search for customer "1001" with status "CANCELED"
    Then I should see "CANCELED" in the status field

Scenario: Add items to existing order
    When I visit the "Orders Page"
    And I search for customer "1001" with status "PENDING"
    And I click the "Manage Items" button
    And I click the "Add Item" button
    And I set "New Item Name" to "Laptop Bag"
    And I set "New Item Category" to "accessories"
    And I set "New Item Product ID" to "1006"
    And I set "New Item Description" to "15\" Laptop Bag"
    And I set "New Item Price" to "59.99"
    And I set "New Item Quantity" to "1"
    And I click the "Save Items" button
    Then I should see "Items updated successfully" message
    When I search for customer "1001" with status "PENDING"
    Then I should see "Laptop Bag" in the order items
    And I should see "1059.98" as the new order total

Scenario: Search for non-existent customer
    When I visit the "Orders Page"
    And I search for customer "9999"
    Then I should see "No orders found" message

Scenario: Retrieve an existing order
    When I visit the "Orders Page"
    And I search for customer "1001" with status "PENDING"
    And I click the "Retrieve Order" button for order with items containing "Laptop"
    Then I should see the order details with:
        | Field        | Value    |
        | Customer ID  | 1001     |
        | Status       | PENDING  |
        | Total Price  | 999.99   |
    And I should see the following items:
        | Name   | Category   | Price  | Quantity |
        | Laptop | electronics| 999.99 | 1        |

Scenario: Retrieve a non-existent order
    When I visit the "Orders Page"
    And I search for customer "9999"
    And I attempt to retrieve the order
    Then I should see "Order not found" message

Scenario: Repeat a delivered order
    When I visit the "Orders Page"
    And I search for customer "1001" with status "DELIVERED"
    And I click the "Repeat Order" button for order with items containing "Headphones"
    Then I should see a new order form with:
        | Field        | Value    |
        | Customer ID  | 1001     |
        | Status       | PENDING  |
    And I should see the following items pre-filled:
        | Name      | Category   | Price  | Quantity |
        | Headphones| electronics| 199.99 | 1        |
    When I click the "Create Order" button
    Then I should see "Order created successfully" message
    And the new order should have status "PENDING"

Scenario: Attempt to repeat a canceled order
    When I visit the "Orders Page"
    And I search for customer "1003" with status "CANCELED"
    And I click the "Repeat Order" button for order with items containing "Mouse"
    Then I should see a new order form with:
        | Field        | Value    |
        | Customer ID  | 1003     |
        | Status       | PENDING  |
    And I should see the following items pre-filled:
        | Name  | Category   | Price  | Quantity |
        | Mouse | accessories| 49.99  | 1        |
    When I click the "Create Order" button
    Then I should see "Order created successfully" message
    And the new order should have status "PENDING"

Scenario: Retrieve order details after creation
    When I visit the "Orders Page"
    And I create a new order with:
        | Customer ID | 1004        |
        | Item Name   | Keyboard    |
        | Category    | accessories |
        | Product ID  | 1005        |
        | Description | Mechanical  |
        | Price       | 129.99      |
        | Quantity    | 1           |
    And I retrieve the newly created order
    Then I should see the order details with:
        | Field        | Value    |
        | Customer ID  | 1004     |
        | Status       | PENDING  |
        | Total Price  | 129.99   |
    And I should see the following items:
        | Name     | Category   | Price  | Quantity |
        | Keyboard | accessories| 129.99 | 1  