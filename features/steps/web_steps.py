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
