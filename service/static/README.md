## Order Listing & Filtering

To apply filters:

- Enter customer ID in input with data-testid="filter-customer-id-input"
- Select status from dropdown with data-testid="filter-status-select"
  - Click to open the dropdown:
    ```python
    # Using data-testid
    driver.find_element(By.CSS_SELECTOR, '[data-testid="filter-status-select"]').click()
    # Or using XPath
    # driver.find_element(By.XPATH, '//*[@data-testid="filter-status-select"]').click()
    ```
  - Select one of: PENDING, SHIPPED, DELIVERED, CANCELED, or ALL
    ```python
    # Example to select 'PENDING'
    driver.find_element(By.XPATH, '//*[@data-testid="filter-status-select"]//div[contains(text(), "PENDING")]').click()
    # Or using CSS selector
    # driver.find_element(By.CSS_SELECTOR, '[data-testid="filter-status-select"] div:contains("PENDING")').click()
    ```
- Enter min price in input with data-testid="filter-min-price-input"
- Enter max price in input with data-testid="filter-max-price-input"
- Click button with data-testid="apply-filters-button"

To clear filters:

- Click button with data-testid="clear-filters-button"

## Order Actions

To search for an order:

- Enter order ID in input with data-testid="search-order-input"
- Click button with data-testid="search-order-button"

To delete an order:

- Click button with data-testid="delete-order-button" next to the order row

To list all orders:

- Click button with data-testid="list-orders-button"

## Order Rows

To manage items for an order:

- Click button with data-testid="manage-items-button" next to the order row

To cancel an order:

- Click button with data-testid="cancel-order-button" next to the order row

To repeat an order:

- Click button with data-testid="repeat-order-button" next to the order row

## Order Creation/Update

To create or update an order:

- Enter customer ID in input with data-testid="customer-id-input"
- Click button with data-testid="create-order-button" (to create) or data-testid="update-order-button" (to update)

To clear form:

- Click button with data-testid="clear-form-button"

## Order Items

To add an item:

- Click button with data-testid="add-item-button"
- Enter item name in input with data-testid="item-name-input"
- Enter product ID in input with data-testid="item-product-id-input"
- Select category from dropdown with data-testid="item-category-select":
  - Click to open the dropdown:
    ```python
    # Using data-testid
    driver.find_element(By.CSS_SELECTOR, '[data-testid="item-category-select"]').click()
    # Or using XPath
    # driver.find_element(By.XPATH, '//*[@data-testid="item-category-select"]').click()
    ```
  - Select from available categories (Electronics, Books, Clothing, etc.):
    ```python
    # Example to select 'Electronics'
    driver.find_element(By.XPATH, '//*[@data-testid="item-category-select"]//div[contains(text(), "Electronics")]').click()
    # Or using CSS selector
    # driver.find_element(By.CSS_SELECTOR, '[data-testid="item-category-select"] div:contains("Electronics")').click()
    ```
- Enter price in input with data-testid="item-price-input"
- Enter quantity in input with data-testid="item-quantity-input"
- Enter description in input with data-testid="item-description-input"
- Click button with data-testid="remove-item-button" to remove item
