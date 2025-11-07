# Selenium Test Automation Guide

This document provides a comprehensive guide to the test IDs and data attributes available for Selenium test automation.

## Test ID Naming Convention

- `data-testid`: Used for general test identification
- `data-id`: Used for simplified selectors and dynamic content

## 1. Order Listing & Filtering

### Filter Controls

| Element           | Test ID                   | Data ID                | Type   | Description              |
| ----------------- | ------------------------- | ---------------------- | ------ | ------------------------ |
| Customer ID Input | `filter-customer-id`      | `filter-customer-id`   | Input  | Filter by customer ID    |
| Status Dropdown   | `filter-status`           | -                      | Select | Filter by order status   |
| Status Trigger    | `filter-status-trigger`   | -                      | Button | Opens status dropdown    |
| Status Value      | `filter-status-value`     | -                      | Span   | Displays selected status |
| Status Options    | `filter-status-all`       | `all`                  | Option | All statuses             |
|                   | `filter-status-pending`   | `pending`              | Option | Pending status           |
|                   | `filter-status-shipped`   | `shipped`              | Option | Shipped status           |
|                   | `filter-status-delivered` | `delivered`            | Option | Delivered status         |
|                   | `filter-status-canceled`  | `canceled`             | Option | Canceled status          |
| Min Price Input   | `filter-min-price`        | `filter-min-price`     | Input  | Filter by minimum price  |
| Max Price Input   | `filter-max-price`        | `filter-max-price`     | Input  | Filter by maximum price  |
| Apply Filters     | `apply-filters`           | `apply-filters-button` | Button | Apply selected filters   |
| Clear Filters     | `clear-filters`           | `clear-filters-button` | Button | Clear all filters        |

### Example: Filtering by Status

```python
# Open status dropdown
driver.find_element(By.CSS_SELECTOR, '[data-testid="filter-status-trigger"]').click()

# Select specific status (e.g., PENDING)
driver.find_element(By.CSS_SELECTOR, '[data-id="pending"]').click()

# Apply filters
driver.find_element(By.CSS_SELECTOR, '[data-testid="apply-filters"]').click()
```

### Example: Filtering by Price Range

```python
# Set minimum price
driver.find_element(By.CSS_SELECTOR, '[data-testid="filter-min-price"]').send_keys("10.00")

# Set maximum price
driver.find_element(By.CSS_SELECTOR, '[data-testid="filter-max-price"]').send_keys("100.00")

# Apply filters
driver.find_element(By.CSS_SELECTOR, '[data-testid="apply-filters"]').click()
```

## 2. Order Actions

### Search and List Controls

| Element         | Test ID               | Data ID               | Type   | Description           |
| --------------- | --------------------- | --------------------- | ------ | --------------------- |
| Search Input    | `search-order-input`  | `search-order-input`  | Input  | Search by order ID    |
| Search Button   | `search-order-button` | `search-order-button` | Button | Execute search        |
| List All Button | `list-orders-button`  | `list-orders-button`  | Button | List all orders       |
| Delete Button   | `delete-order-{id}`   | `delete-order-{id}`   | Button | Delete specific order |

### Example: Searching for an Order

```python
# Enter order ID
driver.find_element(By.CSS_SELECTOR, '[data-testid="search-order-input"]').send_keys("123")

# Click search
driver.find_element(By.CSS_SELECTOR, '[data-testid="search-order-button"]').click()
```

### Example: Deleting an Order

```python
# Delete order with ID 123
driver.find_element(By.CSS_SELECTOR, '[data-testid="delete-order-123"]').click()
```

## 3. Order Rows

### Order Actions

| Element      | Test ID             | Data ID             | Type   | Description           |
| ------------ | ------------------- | ------------------- | ------ | --------------------- |
| Manage Items | `manage-items-{id}` | `manage-items-{id}` | Button | Open items management |
| Cancel Order | `cancel-order-{id}` | `cancel-order-{id}` | Button | Cancel specific order |
| Repeat Order | `repeat-order-{id}` | `repeat-order-{id}` | Button | Duplicate order       |
| Edit Order   | `edit-order-{id}`   | `edit-order-{id}`   | Button | Edit order details    |

### Example: Managing Order Items

```python
# Click manage items for order 123
driver.find_element(By.CSS_SELECTOR, '[data-testid="manage-items-123"]').click()
```

## 4. Order Creation/Update

### Form Controls

| Element           | Test ID               | Data ID               | Type   | Description        |
| ----------------- | --------------------- | --------------------- | ------ | ------------------ |
| Customer ID Input | `customer-id-input`   | `customer-id-input`   | Input  | Customer ID field  |
| Create Order      | `create-order-button` | `create-order-button` | Button | Submit new order   |
| Update Order      | `update-order-button` | `update-order-button` | Button | Save order changes |
| Clear Form        | `clear-form-button`   | `clear-form-button`   | Button | Reset form         |

### Example: Creating a New Order

```python
# Enter customer ID
driver.find_element(By.CSS_SELECTOR, '[data-testid="customer-id-input"]').send_keys("456")

# Click create order
driver.find_element(By.CSS_SELECTOR, '[data-testid="create-order-button"]').click()
```

## 5. Order Items Management

### Item Form Controls

| Element          | Test ID                         | Data ID                    | Type   | Description                   |
| ---------------- | ------------------------------- | -------------------------- | ------ | ----------------------------- |
| Add Item         | `add-item-button`               | `add-item-button`          | Button | Add new item row              |
| Item Name        | `item-{index}-name`             | `item-{index}-name`        | Input  | Item name field               |
| Product ID       | `item-{index}-product-id`       | `item-{index}-product-id`  | Input  | Product identifier            |
| Category Select  | `item-{index}-category`         | -                          | Select | Item category                 |
| Category Trigger | `item-{index}-category-trigger` | -                          | Button | Opens category dropdown       |
| Category Value   | `item-{index}-category-value`   | -                          | Span   | Displays selected category    |
| Category Options | `item-{index}-category-{name}`  | `{name}`                   | Option | Category options (kebab-case) |
| Price            | `item-{index}-price`            | `item-{index}-price`       | Input  | Item price                    |
| Quantity         | `item-{index}-quantity`         | `item-{index}-quantity`    | Input  | Item quantity                 |
| Description      | `item-{index}-description`      | `item-{index}-description` | Input  | Item description              |
| Remove Item      | `remove-item-{index}`           | `remove-item-{index}`      | Button | Remove item row               |
| Save Item        | `save-item-{id}`                | `save-item-{id}`           | Button | Save item changes             |
| Cancel Edit      | `cancel-edit-item`              | `cancel-edit-item`         | Button | Cancel item editing           |

### Example: Adding a New Item

```python
# Click add item button
driver.find_element(By.CSS_SELECTOR, '[data-testid="add-item-button"]').click()

# Fill item details
driver.find_element(By.CSS_SELECTOR, '[data-testid="item-0-name"]').send_keys("Laptop")
driver.find_element(By.CSS_SELECTOR, '[data-testid="item-0-product-id"]').send_keys("LP123")

# Select category
driver.find_element(By.CSS_SELECTOR, '[data-testid="item-0-category-trigger"]').click()
driver.find_element(By.CSS_SELECTOR, '[data-id="electronics"]').click()

# Set price and quantity
driver.find_element(By.CSS_SELECTOR, '[data-testid="item-0-price"]').send_keys("999.99")
driver.find_element(By.CSS_SELECTOR, '[data-testid="item-0-quantity"]').clear()
driver.find_element(By.CSS_SELECTOR, '[data-testid="item-0-quantity"]').send_keys("1")
```

## 6. Status Messages

| Element        | Test ID          | Description                     |
| -------------- | ---------------- | ------------------------------- |
| Status Message | `status-message` | Displays success/error messages |

## 7. Data Rows

| Element   | Test ID          | Description                  |
| --------- | ---------------- | ---------------------------- |
| Order Row | `order-row-{id}` | Table row for specific order |
| Item Row  | `item-row-{id}`  | Table row for specific item  |

## Best Practices

1. **Prefer `data-testid` over other selectors** for better test stability
2. Use `data-id` for simplified selectors when the exact test ID is not needed
3. For dynamic content (like order items), use the pattern `{prefix}-{index}-{field}`
4. When testing dropdowns, always wait for the dropdown to be visible before interacting with it
5. Use explicit waits when elements might take time to load

## Example: Complete Test Case

```python
def test_create_order_with_items():
    # Navigate to orders page
    driver.get("https://your-app.com/orders")

    # Click create new order
    driver.find_element(By.CSS_SELECTOR, '[data-testid="create-order-button"]').click()

    # Fill customer ID
    driver.find_element(By.CSS_SELECTOR, '[data-testid="customer-id-input"]').send_keys("CUST123")

    # Add first item
    driver.find_element(By.CSS_SELECTOR, '[data-testid="add-item-button"]').click()
    driver.find_element(By.CSS_SELECTOR, '[data-testid="item-0-name"]').send_keys("Laptop")
    driver.find_element(By.CSS_SELECTOR, '[data-testid="item-0-product-id"]').send_keys("LP123")
    driver.find_element(By.CSS_SELECTOR, '[data-testid="item-0-price"]').send_keys("999.99")

    # Submit order
    driver.find_element(By.CSS_SELECTOR, '[data-testid="create-order-button"]').click()

    # Verify success message
    status_message = driver.find_element(By.CSS_SELECTOR, '[data-testid="status-message"]').text
    assert "Order created" in status_message
```
