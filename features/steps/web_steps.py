import re
import time
from typing import Any, Dict, List, Optional
from behave.api.pending_step import StepNotImplementedError
from behave import when, then, given  # pylint: disable=no-name-in-module
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    NoAlertPresentException,
)


def save_screenshot(context: Any, filename: str) -> None:
    """Takes a snapshot of the web page for debugging and validation

    Args:
        context (Any): The session context
        filename (str): The message that you are looking for
    """
    # Remove all non-word characters (everything except numbers and letters)
    filename = re.sub(r"[^\w\s]", "", filename)
    # Replace all runs of whitespace with a single dash
    filename = re.sub(r"\s+", "-", filename)
    context.driver.save_screenshot(f"./captures/{filename}.png")


@when('I visit the "Orders Page"')
def step_impl(context) -> None:
    """Navigate to the Orders Page"""
    context.driver.get(f"{context.base_url}/home")


@then('I should see "Orders Service REST API" in the title')
def step_impl(context) -> None:
    """Verify that the page title contains the expected text"""
    WebDriverWait(context.driver, 1).until(
        expected_conditions.presence_of_element_located(
            (By.CSS_SELECTOR, "h1.text-4xl")
        )
    )
    title = context.driver.find_element(By.CSS_SELECTOR, "h1.text-4xl").text
    assert (
        "Orders Service REST API" in title
    ), f"Expected 'Orders Service REST API' in title, but got '{title}'"


@when('I click the "List All Orders" button')
def step_impl(context) -> None:
    """Click the List All Orders button"""
    button = WebDriverWait(context.driver, 1).until(
        expected_conditions.element_to_be_clickable(
            (By.CSS_SELECTOR, '[data-testid="list-orders-button"]')
        )
    )
    button.click()


@then('I should see order with customer_id "{customer_id}" in the orders list')
def step_impl(context, customer_id: str) -> None:
    """Verify that an order with the specified customer_id is visible in the orders list"""
    # Wait for any order to appear first, so DOM is loaded
    WebDriverWait(context.driver, 1).until(
        expected_conditions.presence_of_element_located(
            (By.CSS_SELECTOR, '[data-testid^="order-row-"]')
        )
    )

    # Find all order rows
    order_rows = context.driver.find_elements(
        By.CSS_SELECTOR, '[data-testid^="order-row-"]'
    )

    # Look for a row where the customer_id column matches
    found = False
    for row in order_rows:
        # This assumes the row has <td> cells:
        # 0: order_id, 1: customer_id, etc.
        cells = row.find_elements(By.TAG_NAME, "td")
        if len(cells) > 1:
            if cells[1].text.strip() == str(customer_id).strip():
                found = True
                break

    assert found, f"Order with customer_id {customer_id} not found in the orders list"


@then('I should see the "Create New Order" section')
def step_impl(context) -> None:
    """Verify that the Create New Order section is visible"""
    # Wait for the customer ID input to be present (indicates the form is visible)
    WebDriverWait(context.driver, 5).until(
        expected_conditions.presence_of_element_located(
            (By.CSS_SELECTOR, '[data-testid="customer-id-input"]')
        )
    )


@then('I set the "Customer ID" to "{value}"')
def step_impl(context, value: str) -> None:
    """Set the Customer ID input field"""
    input_field = WebDriverWait(context.driver, 5).until(
        expected_conditions.presence_of_element_located(
            (By.CSS_SELECTOR, '[data-testid="customer-id-input"]')
        )
    )
    input_field.clear()
    input_field.send_keys(value)
    print(f"✓ Set Customer ID to: {value}")
    print(f"  Actual value in field: {input_field.get_attribute('value')}")


@then('I press the "Add Item" button')
def step_impl(context) -> None:
    """Click the Add Item button"""
    button = WebDriverWait(context.driver, 5).until(
        expected_conditions.element_to_be_clickable(
            (By.CSS_SELECTOR, '[data-testid="add-item-button"]')
        )
    )
    ActionChains(context.driver).move_to_element(button).click().perform()
    print(f"✓ Clicked 'Add Item' button")
    # Wait for the item form to appear
    WebDriverWait(context.driver, 5).until(
        expected_conditions.presence_of_element_located(
            (By.CSS_SELECTOR, '[data-testid="item-0-name"]')
        )
    )
    print(f"  Item form appeared")


@then('I set the "Item Name" to "{value}"')
def step_impl(context, value: str) -> None:
    """Set the Item Name input field for the first item (index 0)"""
    input_field = WebDriverWait(context.driver, 5).until(
        expected_conditions.presence_of_element_located(
            (By.CSS_SELECTOR, '[data-testid="item-0-name"]')
        )
    )
    input_field.clear()
    input_field.send_keys(value)
    print(f"✓ Set Item Name to: {value}")
    print(f"  Actual value in field: {input_field.get_attribute('value')}")
    save_screenshot(context, "after-set-item-name")


@then('I set the "Product ID" to "{value}"')
def step_impl(context, value: str) -> None:
    """Set the Product ID input field for the first item (index 0)"""
    input_field = WebDriverWait(context.driver, 5).until(
        expected_conditions.presence_of_element_located(
            (By.CSS_SELECTOR, '[data-testid="item-0-product-id"]')
        )
    )
    input_field.clear()
    input_field.send_keys(value)
    print(f"✓ Set Product ID to: {value}")
    print(f"  Actual value in field: {input_field.get_attribute('value')}")
    save_screenshot(context, "after-set-product-id")


@then('I select "{category}" in the "Category" dropdown')
def step_impl(context, category: str) -> None:
    """Select a category from the dropdown for the first item (index 0)"""
    # Click the category trigger to open the dropdown
    trigger = WebDriverWait(context.driver, 5).until(
        expected_conditions.element_to_be_clickable(
            (By.CSS_SELECTOR, '[data-testid="item-0-category-trigger"]')
        )
    )
    ActionChains(context.driver).move_to_element(trigger).click().perform()
    print(f"✓ Opened category dropdown")

    # Wait for dropdown to be visible and click the option
    # Category options use kebab-case in data-id (e.g., "electronics")
    option = WebDriverWait(context.driver, 5).until(
        expected_conditions.element_to_be_clickable(
            (By.CSS_SELECTOR, f'[data-testid="item-0-category-{category.lower()}"]')
        )
    )
    ActionChains(context.driver).move_to_element(option).click().perform()
    print(f"✓ Selected category: {category}")
    save_screenshot(context, "after-select-category")


@then('I set the "Price" to "{value}"')
def step_impl(context, value: str) -> None:
    """Set the Price input field for the first item (index 0)"""
    input_field = WebDriverWait(context.driver, 5).until(
        expected_conditions.presence_of_element_located(
            (By.CSS_SELECTOR, '[data-testid="item-0-price"]')
        )
    )
    # Clear the field multiple times to ensure it's empty
    input_field.click()
    input_field.clear()
    # Use JavaScript to set value as backup
    context.driver.execute_script(f"arguments[0].value = '';", input_field)
    input_field.send_keys(value)
    # Verify the value was set
    actual_value = input_field.get_attribute("value")
    print(f"✓ Set Price to: {value}")
    print(f"  Actual value in field: {actual_value}")
    if actual_value != value:
        print(f"  ⚠️  WARNING: Expected '{value}' but got '{actual_value}'")
    save_screenshot(context, "after-set-price")


@then('I set the "Quantity" to "{value}"')
def step_impl(context, value: str) -> None:
    """Set the Quantity input field for the first item (index 0)"""
    input_field = WebDriverWait(context.driver, 5).until(
        expected_conditions.presence_of_element_located(
            (By.CSS_SELECTOR, '[data-testid="item-0-quantity"]')
        )
    )
    # Clear the field multiple times to ensure it's empty
    input_field.click()
    input_field.clear()
    # Use JavaScript to set value as backup
    context.driver.execute_script(f"arguments[0].value = '';", input_field)
    input_field.send_keys(value)
    # Verify the value was set
    actual_value = input_field.get_attribute("value")
    print(f"✓ Set Quantity to: {value}")
    print(f"  Actual value in field: {actual_value}")
    if actual_value != value:
        print(f"  ⚠️  WARNING: Expected '{value}' but got '{actual_value}'")
    save_screenshot(context, "after-set-quantity")


@then('I set the "Description" to "{value}"')
def step_impl(context, value: str) -> None:
    """Set the Description input field for the first item (index 0)"""
    input_field = WebDriverWait(context.driver, 5).until(
        expected_conditions.presence_of_element_located(
            (By.CSS_SELECTOR, '[data-testid="item-0-description"]')
        )
    )
    input_field.clear()
    input_field.send_keys(value)
    print(f"✓ Set Description to: {value}")
    print(f"  Actual value in field: {input_field.get_attribute('value')}")
    save_screenshot(context, "after-set-description")


@then('I press the "Create Order" button')
def step_impl(context) -> None:
    """Click the Create Order button"""
    print("\n=== SUMMARY BEFORE CREATING ORDER ===")
    # Print all form values before submitting
    try:
        customer_id = context.driver.find_element(
            By.CSS_SELECTOR, '[data-testid="customer-id-input"]'
        ).get_attribute("value")
        print(f"Customer ID: {customer_id}")
        item_name = context.driver.find_element(
            By.CSS_SELECTOR, '[data-testid="item-0-name"]'
        ).get_attribute("value")
        print(f"Item Name: {item_name}")
        product_id = context.driver.find_element(
            By.CSS_SELECTOR, '[data-testid="item-0-product-id"]'
        ).get_attribute("value")
        print(f"Product ID: {product_id}")
        price = context.driver.find_element(
            By.CSS_SELECTOR, '[data-testid="item-0-price"]'
        ).get_attribute("value")
        print(f"Price: {price}")
        quantity = context.driver.find_element(
            By.CSS_SELECTOR, '[data-testid="item-0-quantity"]'
        ).get_attribute("value")
        print(f"Quantity: {quantity}")
        description = context.driver.find_element(
            By.CSS_SELECTOR, '[data-testid="item-0-description"]'
        ).get_attribute("value")
        print(f"Description: {description}")
    except Exception as e:
        print(f"Error reading form values: {e}")
        save_screenshot(context, "error-reading-form-values")
    print("====================================\n")

    try:
        button = WebDriverWait(context.driver, 5).until(
            expected_conditions.element_to_be_clickable(
                (By.CSS_SELECTOR, '[data-testid="create-order-button"]')
            )
        )
        # Scroll to button to ensure it's visible
        context.driver.execute_script("arguments[0].scrollIntoView(true);", button)
        save_screenshot(context, "before-clicking-create-order")
        ActionChains(context.driver).move_to_element(button).click().perform()
        print("✓ Clicked 'Create Order' button")
        # Wait a moment and take screenshot after clicking
        time.sleep(0.5)
        save_screenshot(context, "after-clicking-create-order")
    except Exception as e:
        print(f"Error clicking Create Order button: {e}")
        save_screenshot(context, "error-clicking-create-order")
        raise


@then('the new order should appear in the orders list with customer_id "{customer_id}"')
def step_impl(context, customer_id: str) -> None:
    """Verify that the newly created order appears in the orders list"""
    # Click "List All Orders" to refresh the list and show the newly created order
    list_button = WebDriverWait(context.driver, 5).until(
        expected_conditions.element_to_be_clickable(
            (By.CSS_SELECTOR, '[data-testid="list-orders-button"]')
        )
    )
    ActionChains(context.driver).move_to_element(list_button).click().perform()
    print("✓ Clicked 'List All Orders' button")

    # Wait for the table to load
    WebDriverWait(context.driver, 5).until(
        expected_conditions.presence_of_element_located(
            (By.CSS_SELECTOR, '[data-testid^="order-row-"]')
        )
    )
    save_screenshot(context, "after-list-all-orders")

    # Custom wait condition to find the order with specific customer_id
    def order_with_customer_id_present(driver):
        order_rows = driver.find_elements(
            By.CSS_SELECTOR, '[data-testid^="order-row-"]'
        )
        for row in order_rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) >= 2:
                customer_id_text = cells[1].text.strip()
                if customer_id_text == str(customer_id).strip():
                    return True
        return False

    # Wait up to 10 seconds for the order to appear
    try:
        WebDriverWait(context.driver, 10).until(order_with_customer_id_present)
        found = True
        print(f"✓ Order with customer_id {customer_id} found successfully!")

        # Automatically save the order ID for later use
        order_rows = context.driver.find_elements(
            By.CSS_SELECTOR, '[data-testid^="order-row-"]'
        )
        for row in order_rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) >= 2:
                if cells[1].text.strip() == str(customer_id).strip():
                    order_id = cells[0].text.strip()
                    context.saved_order_id = order_id
                    print(f"✓ Automatically saved order ID: {order_id}")
                    break
    except TimeoutException:
        found = False
        # Take screenshot on failure
        save_screenshot(context, f"order-not-found-customer-{customer_id}")

        # Collect all customer IDs for debugging
        order_rows = context.driver.find_elements(
            By.CSS_SELECTOR, '[data-testid^="order-row-"]'
        )
        customer_ids_found = []
        for row in order_rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) >= 2:
                customer_id_text = cells[1].text.strip()
                customer_ids_found.append(customer_id_text)
                print(f"Found customer_id: {customer_id_text}")

        print(
            f"\n❌ Screenshot saved to: ./captures/order-not-found-customer-{customer_id}.png"
        )
        assert False, (
            f"Newly created order with customer_id {customer_id} not found in the orders list after 10 seconds. "
            f"Found customer_ids: {customer_ids_found}"
        )


@then('I save the order ID for customer "{customer_id}"')
def step_impl(context, customer_id: str) -> None:
    """Save the order ID for the given customer_id to context for later use"""
    # Find the order row with the matching customer_id and extract the order ID
    order_rows = context.driver.find_elements(
        By.CSS_SELECTOR, '[data-testid^="order-row-"]'
    )

    for row in order_rows:
        cells = row.find_elements(By.TAG_NAME, "td")
        if len(cells) >= 2:
            # cells[0] = order_id, cells[1] = customer_id
            if cells[1].text.strip() == str(customer_id).strip():
                order_id = cells[0].text.strip()
                context.saved_order_id = order_id
                print(f"✓ Saved order ID: {order_id} for customer {customer_id}")
                save_screenshot(context, f"saved-order-{order_id}")
                return

    save_screenshot(context, f"error-saving-order-id-customer-{customer_id}")
    assert False, f"Could not find order with customer_id {customer_id} to save its ID"


@when('I find the order ID for customer_id "{customer_id}"')
def step_impl(context, customer_id: str) -> None:
    """Find the order ID for a given customer_id from the orders list"""
    print(f"\n=== FINDING ORDER ID FOR CUSTOMER_ID {customer_id} ===")

    save_screenshot(context, "before-finding-order-id")

    # Wait for the table to load
    try:
        WebDriverWait(context.driver, 5).until(
            expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR, '[data-testid^="order-row-"]')
            )
        )
        print("✓ Orders table loaded")
        save_screenshot(context, "orders-table-loaded")
    except Exception as e:
        print(f"❌ Error waiting for orders table: {e}")
        save_screenshot(context, "error-loading-orders-table")
        raise

    # Find the order with the matching customer_id
    order_id = None
    try:
        order_rows = context.driver.find_elements(
            By.CSS_SELECTOR, '[data-testid^="order-row-"]'
        )
        print(f"  Found {len(order_rows)} orders in the table")

        for row in order_rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) >= 2:
                row_customer_id = cells[1].text.strip()
                row_order_id = cells[0].text.strip()
                print(
                    f"  Checking row: order_id={row_order_id}, customer_id={row_customer_id}"
                )

                if row_customer_id == str(customer_id).strip():
                    order_id = row_order_id
                    print(f"✓ Found order ID: {order_id} for customer {customer_id}")
                    save_screenshot(context, f"found-order-{order_id}")
                    break

        if not order_id:
            save_screenshot(context, f"error-order-not-found-customer-{customer_id}")
            assert False, f"Could not find order with customer_id {customer_id}"

        # Save the order ID for the next step
        context.saved_order_id = order_id
        print(f"✓ Saved order ID: {order_id} to context")
    except Exception as e:
        print(f"❌ Error finding order: {e}")
        save_screenshot(context, "error-finding-order")
        raise


@when("I retrieve the order by its ID")
def step_impl(context) -> None:
    """Retrieve an order by searching for it using its ID"""
    assert hasattr(context, "saved_order_id"), "No saved order ID found in context"

    order_id = context.saved_order_id
    print(f"\n=== RETRIEVING ORDER {order_id} ===")

    save_screenshot(context, "before-retrieve-order")

    # Enter the order ID in the search input
    try:
        search_input = WebDriverWait(context.driver, 5).until(
            expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR, '[data-testid="search-order-input"]')
            )
        )
        print(f"✓ Found search input field")
        save_screenshot(context, "found-search-input")

        search_input.clear()
        search_input.send_keys(order_id)
        actual_value = search_input.get_attribute("value")
        print(f"✓ Entered order ID {order_id} in search input")
        print(f"  Actual value in field: {actual_value}")
        save_screenshot(context, f"after-entering-search-order-{order_id}")
    except Exception as e:
        print(f"❌ Error finding/filling search input: {e}")
        save_screenshot(context, "error-search-input")
        raise

    # Click the search button to retrieve the order
    try:
        search_button = WebDriverWait(context.driver, 5).until(
            expected_conditions.element_to_be_clickable(
                (By.CSS_SELECTOR, '[data-testid="search-order-button"]')
            )
        )
        print(f"✓ Found search button")
        save_screenshot(context, "before-clicking-search-button")

        ActionChains(context.driver).move_to_element(search_button).click().perform()
        print(f"✓ Clicked 'Search' button to retrieve order {order_id}")
        time.sleep(0.5)
        save_screenshot(context, f"after-retrieve-order-{order_id}")
    except Exception as e:
        print(f"❌ Error clicking search button: {e}")
        save_screenshot(context, "error-clicking-search-button")
        raise


@then('the order should appear in the "Update Order" section')
def step_impl(context) -> None:
    """Verify that the order appears in the Update Order section"""
    assert hasattr(context, "saved_order_id"), "No saved order ID found in context"

    order_id = context.saved_order_id
    print(f"\n=== VERIFYING ORDER {order_id} IN UPDATE SECTION ===")

    save_screenshot(context, "before-checking-update-section")

    # Wait a moment for the form to load
    time.sleep(1)
    save_screenshot(context, "after-waiting-for-form")

    # Verify the Update Order button is visible (indicates form is in update mode)
    try:
        # Find button by text content since it doesn't have data-testid
        update_button = WebDriverWait(context.driver, 10).until(
            expected_conditions.presence_of_element_located(
                (By.XPATH, "//button[contains(text(), 'Update Order')]")
            )
        )
        print(f"✓ Found Update Order button - form is in update mode")
        save_screenshot(context, "found-update-order-button")
    except Exception as e:
        print(f"❌ Error finding Update Order button: {e}")
        save_screenshot(context, "error-finding-update-button")
        raise

    print(f"✓ Order {order_id} successfully loaded in Update Order section")
    save_screenshot(context, f"order-{order_id}-in-update-section")


@then('I select "{status}" in the "Status" dropdown')
def step_impl(context, status: str) -> None:
    """Select a status from the Status dropdown in the order form"""
    print(f"\n=== SELECTING STATUS: {status} ===")

    save_screenshot(context, "before-opening-status-dropdown")

    # Click the status trigger to open the dropdown
    try:
        trigger = WebDriverWait(context.driver, 5).until(
            expected_conditions.element_to_be_clickable(
                (By.CSS_SELECTOR, '[data-testid="update-order-status-trigger"]')
            )
        )
        print(f"✓ Found status dropdown trigger")
        save_screenshot(context, "found-status-trigger")

        ActionChains(context.driver).move_to_element(trigger).click().perform()
        print(f"✓ Opened status dropdown")
        time.sleep(0.3)
        save_screenshot(context, "after-opening-status-dropdown")
    except Exception as e:
        print(f"❌ Error opening status dropdown: {e}")
        save_screenshot(context, "error-opening-status-dropdown")
        raise

    # Wait for dropdown to be visible and click the option
    # Status options use lowercase in data-id (e.g., "shipped")
    try:
        option = WebDriverWait(context.driver, 5).until(
            expected_conditions.element_to_be_clickable(
                (
                    By.CSS_SELECTOR,
                    f'[data-testid="update-order-status-{status.lower()}"]',
                )
            )
        )
        print(f"✓ Found status option: {status}")
        save_screenshot(context, f"found-status-option-{status.lower()}")

        ActionChains(context.driver).move_to_element(option).click().perform()
        print(f"✓ Selected status: {status}")
        time.sleep(0.3)
        save_screenshot(context, f"after-selecting-status-{status.lower()}")
    except Exception as e:
        print(f"❌ Error selecting status {status}: {e}")
        save_screenshot(context, f"error-selecting-status-{status.lower()}")
        raise


@then('I press the "Update Order" button')
def step_impl(context) -> None:
    """Click the Update Order button"""
    print(f"\n=== CLICKING UPDATE ORDER BUTTON ===")

    save_screenshot(context, "before-finding-update-button")

    try:
        # Find button by text content since it doesn't have data-testid
        button = WebDriverWait(context.driver, 5).until(
            expected_conditions.element_to_be_clickable(
                (By.XPATH, "//button[contains(text(), 'Update Order')]")
            )
        )
        print("✓ Found Update Order button")
        save_screenshot(context, "found-update-button")

        # Scroll to button to ensure it's visible
        context.driver.execute_script("arguments[0].scrollIntoView(true);", button)
        print("✓ Scrolled to Update Order button")
        save_screenshot(context, "before-clicking-update-order")

        ActionChains(context.driver).move_to_element(button).click().perform()
        print("✓ Clicked 'Update Order' button")
        time.sleep(0.5)
        save_screenshot(context, "after-clicking-update-order")
    except Exception as e:
        print(f"❌ Error clicking Update Order button: {e}")
        save_screenshot(context, "error-clicking-update-order")
        raise


@then('the order status should be updated to "{expected_status}"')
def step_impl(context, expected_status: str) -> None:
    """Verify that the order status has been updated"""
    assert hasattr(context, "saved_order_id"), "No saved order ID found in context"

    order_id = context.saved_order_id
    print(f"\n=== VERIFYING STATUS UPDATE FOR ORDER {order_id} ===")

    save_screenshot(context, "before-refresh-to-check-status")

    # Click "List All Orders" to refresh the list
    try:
        list_button = WebDriverWait(context.driver, 5).until(
            expected_conditions.element_to_be_clickable(
                (By.CSS_SELECTOR, '[data-testid="list-orders-button"]')
            )
        )
        print("✓ Found List All Orders button")
        save_screenshot(context, "found-list-orders-button")

        ActionChains(context.driver).move_to_element(list_button).click().perform()
        print("✓ Clicked 'List All Orders' button to refresh")
        time.sleep(0.5)
        save_screenshot(context, "after-clicking-list-orders")
    except Exception as e:
        print(f"❌ Error clicking List All Orders: {e}")
        save_screenshot(context, "error-clicking-list-orders")
        raise

    # Wait for the table to load
    try:
        WebDriverWait(context.driver, 5).until(
            expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR, '[data-testid^="order-row-"]')
            )
        )
        print("✓ Orders table loaded")
        save_screenshot(context, "after-refresh-for-status-check")
    except Exception as e:
        print(f"❌ Error waiting for orders table: {e}")
        save_screenshot(context, "error-loading-orders-table")
        raise

    # Find the order row and check the status
    try:
        order_row = WebDriverWait(context.driver, 5).until(
            expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR, f'[data-testid="order-row-{order_id}"]')
            )
        )
        print(f"✓ Found order row for order {order_id}")
        save_screenshot(context, f"found-order-row-{order_id}")

        cells = order_row.find_elements(By.TAG_NAME, "td")
        print(f"  Order row has {len(cells)} columns")

        # Print all cell values for debugging
        for i, cell in enumerate(cells):
            print(f"  Column {i}: {cell.text.strip()}")

        # Assuming: cells[0] = order_id, cells[1] = customer_id, cells[2] = status
        if len(cells) >= 3:
            actual_status = cells[2].text.strip()
            print(f"✓ Order {order_id} status: {actual_status}")
            save_screenshot(context, f"order-{order_id}-status-{actual_status.lower()}")

            assert (
                actual_status.upper() == expected_status.upper()
            ), f"Expected status '{expected_status}' but got '{actual_status}' for order {order_id}"
            print(f"✓ Order status successfully updated to {expected_status}")
        else:
            save_screenshot(context, f"error-checking-status-order-{order_id}")
            assert (
                False
            ), f"Could not find status column for order {order_id} (only {len(cells)} columns found)"
    except Exception as e:
        print(f"❌ Error checking order status: {e}")
        save_screenshot(context, f"error-checking-status-order-{order_id}")
        raise


@when('I retrieve order with ID "{order_id}"')
def step_impl(context, order_id: str) -> None:
    """Retrieve a specific order by entering its ID and clicking search"""
    print(f"\n=== RETRIEVING ORDER WITH ID {order_id} ===")

    save_screenshot(context, "before-retrieve-by-id")

    # Enter the order ID in the search input
    try:
        search_input = WebDriverWait(context.driver, 5).until(
            expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR, '[data-testid="search-order-input"]')
            )
        )
        print(f"✓ Found search input field")
        save_screenshot(context, "found-search-input-for-retrieve")

        search_input.clear()
        search_input.send_keys(order_id)
        actual_value = search_input.get_attribute("value")
        print(f"✓ Entered order ID {order_id} in search input")
        print(f"  Actual value in field: {actual_value}")
        save_screenshot(context, f"after-entering-order-id-{order_id}")
    except Exception as e:
        print(f"❌ Error finding/filling search input: {e}")
        save_screenshot(context, "error-search-input-retrieve")
        raise

    # Click the search button to retrieve the order
    try:
        search_button = WebDriverWait(context.driver, 5).until(
            expected_conditions.element_to_be_clickable(
                (By.CSS_SELECTOR, '[data-testid="search-order-button"]')
            )
        )
        print(f"✓ Found search button")
        save_screenshot(context, "before-clicking-search-for-retrieve")

        ActionChains(context.driver).move_to_element(search_button).click().perform()
        print(f"✓ Clicked 'Search' button to retrieve order {order_id}")
        time.sleep(0.5)
        save_screenshot(context, f"after-retrieve-order-{order_id}")

        # Save the order ID for later use
        context.saved_order_id = order_id
    except Exception as e:
        print(f"❌ Error clicking search button: {e}")
        save_screenshot(context, "error-clicking-search-for-retrieve")
        raise


@then("I should see only {count:d} order in the orders list")
def step_impl(context, count: int) -> None:
    """Verify that exactly the specified number of orders are displayed in the orders list"""
    print(f"\n=== VERIFYING ORDER COUNT: {count} ===")

    save_screenshot(context, "before-counting-orders")

    # Wait for orders table to be present
    try:
        WebDriverWait(context.driver, 5).until(
            expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR, '[data-testid^="order-row-"]')
            )
        )
        print("✓ Orders table loaded")
        save_screenshot(context, "orders-table-loaded-for-count")
    except Exception as e:
        print(f"❌ Error waiting for orders table: {e}")
        save_screenshot(context, "error-waiting-for-orders-table")
        raise

    # Count the orders in the table
    order_rows = context.driver.find_elements(
        By.CSS_SELECTOR, '[data-testid^="order-row-"]'
    )
    actual_count = len(order_rows)

    print(f"  Expected: {count} order(s)")
    print(f"  Actual: {actual_count} order(s)")

    # Print details of each order for debugging
    for i, row in enumerate(order_rows, 1):
        cells = row.find_elements(By.TAG_NAME, "td")
        if len(cells) >= 2:
            order_id = cells[0].text.strip()
            customer_id = cells[1].text.strip()
            print(f"  Order {i}: ID={order_id}, Customer={customer_id}")

    save_screenshot(context, f"order-count-{actual_count}")

    assert (
        actual_count == count
    ), f"Expected {count} order(s) in the list, but found {actual_count}"
    print(f"✓ Verified: exactly {count} order(s) in the list")


@when('I find the retrieved order ID for customer_id "{customer_id}"')
def step_impl_retrieve(context, customer_id: str) -> None:
    """Find the order ID for a given customer_id from the orders list (for retrieve scenario)"""
    print(f"\n=== FINDING ORDER ID FOR CUSTOMER_ID {customer_id} (RETRIEVE) ===")

    save_screenshot(context, "before-finding-order-id-retrieve")

    # Wait for the table to load
    try:
        WebDriverWait(context.driver, 5).until(
            expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR, '[data-testid^="order-row-"]')
            )
        )
        print("✓ Orders table loaded")
        save_screenshot(context, "orders-table-loaded-retrieve")
    except Exception as e:
        print(f"❌ Error waiting for orders table: {e}")
        save_screenshot(context, "error-loading-orders-table-retrieve")
        raise

    # Find the order with the matching customer_id
    order_id = None
    try:
        order_rows = context.driver.find_elements(
            By.CSS_SELECTOR, '[data-testid^="order-row-"]'
        )
        print(f"  Found {len(order_rows)} orders in the table")

        for row in order_rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) >= 2:
                row_customer_id = cells[1].text.strip()
                row_order_id = cells[0].text.strip()
                print(
                    f"  Checking row: order_id={row_order_id}, customer_id={row_customer_id}"
                )

                if row_customer_id == str(customer_id).strip():
                    order_id = row_order_id
                    print(f"✓ Found order ID: {order_id} for customer {customer_id}")
                    save_screenshot(context, f"found-order-{order_id}-retrieve")
                    break

        if not order_id:
            save_screenshot(
                context, f"error-order-not-found-customer-{customer_id}-retrieve"
            )
            assert False, f"Could not find order with customer_id {customer_id}"

        # Save the order ID for the next step
        context.saved_order_id = order_id
        print(f"✓ Saved order ID: {order_id} to context")
    except Exception as e:
        print(f"❌ Error finding order: {e}")
        save_screenshot(context, "error-finding-order-retrieve")
        raise


@when("I retrieve the order by its saved ID")
def step_impl_retrieve_by_saved_id(context) -> None:
    """Retrieve an order by searching for it using its saved ID"""
    assert hasattr(context, "saved_order_id"), "No saved order ID found in context"

    order_id = context.saved_order_id
    print(f"\n=== RETRIEVING ORDER BY SAVED ID {order_id} ===")

    save_screenshot(context, "before-retrieve-by-saved-id")

    # Enter the order ID in the search input
    try:
        search_input = WebDriverWait(context.driver, 5).until(
            expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR, '[data-testid="search-order-input"]')
            )
        )
        print(f"✓ Found search input field")
        save_screenshot(context, "found-search-input-retrieve-saved")

        search_input.clear()
        search_input.send_keys(order_id)
        actual_value = search_input.get_attribute("value")
        print(f"✓ Entered order ID {order_id} in search input")
        print(f"  Actual value in field: {actual_value}")
        save_screenshot(context, f"after-entering-search-order-{order_id}-retrieve")
    except Exception as e:
        print(f"❌ Error finding/filling search input: {e}")
        save_screenshot(context, "error-search-input-retrieve-saved")
        raise

    # Click the search button to retrieve the order
    try:
        search_button = WebDriverWait(context.driver, 5).until(
            expected_conditions.element_to_be_clickable(
                (By.CSS_SELECTOR, '[data-testid="search-order-button"]')
            )
        )
        print(f"✓ Found search button")
        save_screenshot(context, "before-clicking-search-button-retrieve")

        ActionChains(context.driver).move_to_element(search_button).click().perform()
        print(f"✓ Clicked 'Search' button to retrieve order {order_id}")
        time.sleep(0.5)
        save_screenshot(context, f"after-retrieve-order-{order_id}-saved")
    except Exception as e:
        print(f"❌ Error clicking search button: {e}")
        save_screenshot(context, "error-clicking-search-button-retrieve")
        raise


@when('I enter order ID "{order_id}" in the search field')
def step_impl_enter_order_id_for_delete(context, order_id: str) -> None:
    """Enter order ID in the search field for deletion"""
    print(f"\n=== ENTERING ORDER ID {order_id} FOR DELETE ===")

    save_screenshot(context, "before-entering-order-id-for-delete")

    # Enter the order ID in the search input
    try:
        search_input = WebDriverWait(context.driver, 5).until(
            expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR, '[data-testid="search-order-input"]')
            )
        )
        print(f"✓ Found search input field")
        save_screenshot(context, "found-search-input-for-delete")

        search_input.clear()
        search_input.send_keys(order_id)
        actual_value = search_input.get_attribute("value")
        print(f"✓ Entered order ID {order_id} in search input")
        print(f"  Actual value in field: {actual_value}")
        save_screenshot(context, f"after-entering-order-id-{order_id}-for-delete")

        # Save the order ID for verification
        context.order_id_to_delete = order_id
    except Exception as e:
        print(f"❌ Error finding/filling search input: {e}")
        save_screenshot(context, "error-search-input-for-delete")
        raise


@when('I click the "Delete" button')
def step_impl_click_delete_button(context) -> None:
    """Click the Delete button"""
    print(f"\n=== CLICKING DELETE BUTTON ===")

    save_screenshot(context, "before-clicking-delete-button")

    # Find and click the delete button
    try:
        delete_button = WebDriverWait(context.driver, 5).until(
            expected_conditions.element_to_be_clickable(
                (By.CSS_SELECTOR, '[data-testid="delete-order-button"]')
            )
        )
        print(f"✓ Found Delete button")
        save_screenshot(context, "found-delete-button")

        ActionChains(context.driver).move_to_element(delete_button).click().perform()
        print(f"✓ Clicked Delete button")
        time.sleep(0.5)
        save_screenshot(context, "after-clicking-delete-button")
    except Exception as e:
        print(f"❌ Error clicking Delete button: {e}")
        save_screenshot(context, "error-clicking-delete-button")
        raise


@then("the order should be removed from the orders list")
def step_impl_verify_order_removed(context) -> None:
    """Verify that the order has been removed from the orders list"""
    assert hasattr(
        context, "order_id_to_delete"
    ), "No order ID to delete found in context"

    order_id = context.order_id_to_delete
    print(f"\n=== VERIFYING ORDER {order_id} IS REMOVED ===")

    save_screenshot(context, f"before-verifying-removal-order-{order_id}")

    # Refresh the orders list to see the updated state
    try:
        list_button = WebDriverWait(context.driver, 5).until(
            expected_conditions.element_to_be_clickable(
                (By.CSS_SELECTOR, '[data-testid="list-orders-button"]')
            )
        )
        print("✓ Found List All Orders button")
        save_screenshot(context, "found-list-orders-button-for-verification")

        ActionChains(context.driver).move_to_element(list_button).click().perform()
        print("✓ Clicked 'List All Orders' button to refresh")
        time.sleep(0.5)
        save_screenshot(context, "after-clicking-list-orders-for-verification")
    except Exception as e:
        print(f"❌ Error clicking List All Orders: {e}")
        save_screenshot(context, "error-clicking-list-orders-for-verification")
        raise

    # Wait for the table to load
    try:
        WebDriverWait(context.driver, 5).until(
            expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR, '[data-testid^="order-row-"]')
            )
        )
        print("✓ Orders table loaded")
        save_screenshot(context, "orders-table-loaded-after-delete")
    except Exception as e:
        # If no orders exist, that's also valid
        print(f"  No orders found in table (might be empty): {e}")
        save_screenshot(context, "no-orders-in-table-after-delete")

    # Verify the order is NOT in the list
    try:
        order_rows = context.driver.find_elements(
            By.CSS_SELECTOR, '[data-testid^="order-row-"]'
        )
        print(f"  Found {len(order_rows)} orders in the table after deletion")

        # Check that the deleted order is not present
        for row in order_rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) >= 1:
                row_order_id = cells[0].text.strip()
                print(f"  Checking row: order_id={row_order_id}")

                assert (
                    row_order_id != order_id
                ), f"Order {order_id} should have been deleted but is still present"

        print(f"✓ Verified: Order {order_id} has been successfully removed")
        save_screenshot(context, f"verified-order-{order_id}-removed")
    except Exception as e:
        print(f"❌ Error verifying order removal: {e}")
        save_screenshot(context, f"error-verifying-removal-order-{order_id}")
        raise
