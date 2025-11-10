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
            | name       | category    | product_id | description      | price  | quantity |
            | Laptop     | Electronics | 1001       | 15" Laptop       | 999.99 | 1        |
            | Smartphone | Electronics | 1002       | Latest model     | 699.99 | 2        |
            | Headphones | Electronics | 1003       | Noise cancelling | 199.99 | 1        |
            | Mouse      | Accessories | 1004       | Wireless mouse   | 49.99  | 1        |

    Scenario: View all orders
        When I visit the "Orders Page"
        Then I should see "Orders Service REST API" in the title
        When I click the "List All Orders" button
        Then I should see order with customer_id "1001" in the orders list
        And I should see order with customer_id "1002" in the orders list
        And I should see order with customer_id "1003" in the orders list
    
    Scenario: Create a new order with items
        When I visit the "Orders Page"
        Then I should see the "Create New Order" section
        And I set the "Customer ID" to "3001"
        And I set the "Item Name" to "New Product"
        And I set the "Product ID" to "99999"
        And I select "Electronics" in the "Category" dropdown
        And I set the "Price" to "149.99"
        And I set the "Quantity" to "2"
        And I set the "Description" to "New item description"
        And I press the "Create Order" button
        Then the new order should appear in the orders list with customer_id "3001"

    Scenario: Update order status to SHIPPED
        When I visit the "Orders Page"
        And I click the "List All Orders" button
        And I find the order ID for customer_id "1001"
        And I retrieve the order by its ID
        Then the order should appear in the "Update Order" section
        And I select "SHIPPED" in the "Status" dropdown
        And I press the "Update Order" button
        Then the order status should be updated to "SHIPPED"
