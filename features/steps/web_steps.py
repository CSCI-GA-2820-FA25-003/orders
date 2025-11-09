import re
import time
from typing import Any, Dict, List, Optional
from behave.api.pending_step import StepNotImplementedError
from behave import when, then, given  # pylint: disable=no-name-in-module
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
