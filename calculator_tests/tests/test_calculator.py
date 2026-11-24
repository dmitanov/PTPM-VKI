import os
import unittest

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from pages import CalculatorPage


def create_driver():
    browser = os.getenv("BROWSER", "edge").strip().lower()
    headless = os.getenv("HEADLESS", "true").strip().lower() not in {"0", "false", "no"}

    if browser == "chrome":
        options = ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        driver = webdriver.Chrome(options=options)
    elif browser == "edge":
        options = EdgeOptions()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        driver = webdriver.Edge(options=options)
    elif browser == "firefox":
        options = FirefoxOptions()
        if headless:
            options.add_argument("--headless")
        driver = webdriver.Firefox(options=options)
    else:
        raise ValueError(f"Unsupported browser: {browser}. Use chrome, edge or firefox.")

    driver.maximize_window()
    return driver


class CalculatorTests(unittest.TestCase):
    def setUp(self):
        self.driver = create_driver()
        self.page = CalculatorPage(self.driver).open()

    def tearDown(self):
        self.driver.quit()

    def assert_number(self, expected, first, second, operation):
        actual = self.page.calculate(first, second, operation)
        self.assertAlmostEqual(float(actual), float(expected), places=10)

    def test_default_state(self):
        self.assertEqual(self.page.get_result_text(), "0 + 0 = 0")

    def test_addition(self):
        self.assert_number(19, 12, 7, "+")

    def test_subtraction(self):
        self.assert_number(5, 12, 7, "-")

    def test_multiplication(self):
        self.assert_number(84, 12, 7, "*")

    def test_division(self):
        self.assert_number(3, 12, 4, "/")

    def test_decimal_division(self):
        self.assert_number(2.5, 10, 4, "/")

    def test_negative_numbers(self):
        self.assert_number(-5, -8, 3, "+")

    def test_large_numbers(self):
        self.assert_number(999998000001, 999999, 999999, "*")

    def test_division_by_zero_returns_null(self):
        self.assertEqual(self.page.calculate(10, 0, "/"), "null")

    def test_zero_divided_by_zero_returns_null(self):
        self.assertEqual(self.page.calculate(0, 0, "/"), "null")

    def test_increment_first_number(self):
        value = (
            self.page.enter_first_number(1)
            .enter_second_number(2)
            .select_operation("-")
            .increment_first()
            .get_calculated_value()
        )
        self.assertAlmostEqual(float(value), 0, places=10)

    def test_decrement_first_number(self):
        value = (
            self.page.enter_first_number(4)
            .enter_second_number(2)
            .select_operation("-")
            .decrement_first()
            .get_calculated_value()
        )
        self.assertAlmostEqual(float(value), 1, places=10)

    def test_increment_second_number(self):
        value = (
            self.page.enter_first_number(2)
            .enter_second_number(1)
            .select_operation("+")
            .increment_second()
            .get_calculated_value()
        )
        self.assertAlmostEqual(float(value), 4, places=10)

    def test_decrement_second_number(self):
        value = (
            self.page.enter_first_number(5)
            .enter_second_number(2)
            .select_operation("-")
            .decrement_second()
            .get_calculated_value()
        )
        self.assertAlmostEqual(float(value), 4, places=10)

    def test_power_operation_is_not_available_in_application(self):
        self.assertEqual(self.page.get_available_operations(), ["+", "-", "*", "/"])
        self.assertNotIn("**", self.page.get_available_operations())


if __name__ == "__main__":
    unittest.main()
