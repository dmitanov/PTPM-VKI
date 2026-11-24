from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

BASE_URL = "https://www.globalsqa.com/angularJs-protractor/SimpleCalculator/"


class CalculatorPage:
    _FIRST_NUMBER = (By.CSS_SELECTOR, 'input[ng-model="a"]')
    _SECOND_NUMBER = (By.CSS_SELECTOR, 'input[ng-model="b"]')
    _OPERATION = (By.CSS_SELECTOR, 'select[ng-model="operation"]')
    _RESULT = (By.CSS_SELECTOR, "b.result")
    _INCREMENT_FIRST = (By.CSS_SELECTOR, 'button[ng-click="inca()"]')
    _DECREMENT_FIRST = (By.CSS_SELECTOR, 'button[ng-click="deca()"]')
    _INCREMENT_SECOND = (By.CSS_SELECTOR, 'button[ng-click="incb()"]')
    _DECREMENT_SECOND = (By.CSS_SELECTOR, 'button[ng-click="decb()"]')

    def __init__(self, driver: WebDriver, timeout: int = 10) -> None:
        self._driver = driver
        self._timeout = timeout

    def open(self) -> "CalculatorPage":
        self._driver.get(BASE_URL)
        self._wait_for(self._RESULT)
        return self

    def enter_first_number(self, number) -> "CalculatorPage":
        self._set_input(self._FIRST_NUMBER, number)
        return self

    def enter_second_number(self, number) -> "CalculatorPage":
        self._set_input(self._SECOND_NUMBER, number)
        return self

    def select_operation(self, operation: str) -> "CalculatorPage":
        Select(self._wait_for(self._OPERATION)).select_by_value(operation)
        return self

    def get_available_operations(self) -> list[str]:
        select = Select(self._wait_for(self._OPERATION))
        return [option.get_attribute("value") for option in select.options]

    def increment_first(self) -> "CalculatorPage":
        self._click(self._INCREMENT_FIRST)
        return self

    def decrement_first(self) -> "CalculatorPage":
        self._click(self._DECREMENT_FIRST)
        return self

    def increment_second(self) -> "CalculatorPage":
        self._click(self._INCREMENT_SECOND)
        return self

    def decrement_second(self) -> "CalculatorPage":
        self._click(self._DECREMENT_SECOND)
        return self

    def get_result_text(self) -> str:
        return self._wait_for(self._RESULT).text.strip()

    def get_calculated_value(self) -> str:
        return self.get_result_text().rsplit("=", 1)[-1].strip()

    def calculate(self, first, second, operation: str) -> str:
        return (
            self.enter_first_number(first)
            .enter_second_number(second)
            .select_operation(operation)
            .get_calculated_value()
        )

    def _set_input(self, locator, value) -> None:
        field = self._wait_for(locator)
        field.clear()
        field.send_keys(str(value))
        self._wait_for_result()

    def _click(self, locator) -> None:
        self._wait_for(locator).click()
        self._wait_for_result()

    def _wait_for(self, locator):
        return WebDriverWait(self._driver, self._timeout).until(
            EC.visibility_of_element_located(locator)
        )

    def _wait_for_result(self) -> None:
        WebDriverWait(self._driver, self._timeout).until(
            lambda driver: "=" in driver.find_element(*self._RESULT).text
        )
