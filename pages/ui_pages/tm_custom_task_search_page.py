import logging

import allure
from playwright.sync_api import Page

from dao.test_execution_db_updater_dao import DBReporter
from lib.hitl_logger import LoggerPage
from utils.ado.ado_step_logger import StepLogger
from utils.generic.get_readable_method_name import get_method_name
from utils.generic.post_test_actions_handler import save_success

hitlLogger = logging.getLogger("HitlLogger")


class CustomTaskSearchPage:
    def __init__(self, page: Page):
        self.page = page
        self.log = LoggerPage(page)

    @allure.step("Validate task search filters Error Missing data schema or form schema")
    def validate_custom_task_search_with_empty_schema(self, reporter: DBReporter, step_logger: StepLogger):
        method_name = get_method_name()

        try:

            filter_icon = self.page.get_by_role("button").filter(has_text="filter_alt")
            self.log.click(filter_icon, "Filter Icon")

            error_locator = self.page.locator("mat-sidenav .red")
            self.log.highlight_only(error_locator, "Error message")
            error_text = error_locator.text_content().strip()

            assert "Missing data schema" in error_text

            self.page.keyboard.press("Escape")
            self.log.log("info", "Pressed Escape to close modal")

            save_success(reporter, method_name)
            step_logger.add_step("Clear fields", "Clear Parameters button reset all fields")
        except Exception as e:
            step_logger.fail_step(method_name, "Search filter flow failed", str(e))
            raise

    @allure.step("Validate task search filters including optional fields")
    def validate_custom_task_search_with_correct_schema(self, reporter: DBReporter, step_logger: StepLogger):
        method_name = get_method_name()

        try:
            filter_icon = self.page.get_by_role("button").filter(has_text="filter_alt")
            self.log.click(filter_icon, "Filter Icon")
            step_logger.add_step("Open filter panel", "Filters panel is accessible")

            # Ensure Search button is initially disabled
            search_button = self.page.get_by_role("button", name="Search", exact=True)
            assert search_button.is_disabled(), "Search button should be disabled initially"
            step_logger.add_step("Initial state", "Search button is disabled without required fields")

            # Fill Description field
            desc_input = self.page.get_by_label("Description")
            self.log.fill(desc_input, "Good", "Description Field")

            # Fill Product Key (find input under label)
            product_key_input = self.page.locator("label:text-is('Product Key')").locator("..").locator(
                "input[matinput]")
            self.log.fill(product_key_input, "164756", "Product Key")
            self.page.keyboard.press("Enter")

            # Fill Product Base Key
            product_base_key_input = self.page.locator("label:text-is('Product Base Key')").locator("..").locator(
                "input[matinput]")
            self.log.fill(product_base_key_input, "500157664", "Product Base Key")
            self.page.keyboard.press("Enter")

            # vendor search is not available at the moment.
            # # Step 1: Click on the dropdown arrow to open Vendor list
            # vendor_input = self.page.locator("div").filter(has_text=re.compile(r"^\+10$")).nth(2)
            # self.log.click(vendor_input, "Vendor dropdown arrow")
            #
            # search_area = self.page.get_by_role("textbox", name="Search...")
            # self.log.click(search_area, "Search Area")
            #
            # search_area.fill("501")
            # option_checkbox = self.page.get_by_role("checkbox", name="501k Recycling LLC")
            # self.log.check(option_checkbox, "501k Recycling LLC")

            search_button = self.page.get_by_role("button", name="Search", exact=True)
            self.log.click(search_button, "Search Button")

            save_success(reporter, method_name)
            step_logger.add_step("Clear fields", "Clear Parameters button reset all fields")

        except Exception as e:
            step_logger.fail_step(method_name, "Search filter flow failed", str(e))
            raise

    @allure.step("Populate task search filters")
    def set_custom_task_search_to_product_task(self, reporter: DBReporter, step_logger: StepLogger, product_key: str, product_base_key: str):
        method_name = get_method_name()

        try:
            filter_icon = self.page.get_by_role("button").filter(has_text="filter_alt")
            self.log.click(filter_icon, "Filter Icon")
            step_logger.add_step("Open filter panel", "Filters panel is accessible")

            # Ensure Search button is initially disabled
            search_button = self.page.get_by_role("button", name="Search", exact=True)
            assert search_button.is_disabled(), "Search button should be disabled initially"
            step_logger.add_step("Initial state", "Search button is disabled without required fields")

            # Fill Product Key (find input under label)
            product_key_input = self.page.locator("label:text-is('Product Key')").locator("..").locator(
                "input[matinput]")
            self.log.fill(product_key_input, product_key, "Product Key")
            self.page.keyboard.press("Enter")

            # Fill Product Base Key
            product_base_key_input = self.page.locator("label:text-is('Product Base Key')").locator("..").locator(
                "input[matinput]")
            self.log.fill(product_base_key_input, product_base_key, "Product Base Key")
            self.page.keyboard.press("Enter")

            # vendor search is not available at the moment.
            # # Step 1: Click on the dropdown arrow to open Vendor list
            # vendor_input = self.page.locator("div").filter(has_text=re.compile(r"^\+10$")).nth(2)
            # self.log.click(vendor_input, "Vendor dropdown arrow")
            #
            # search_area = self.page.get_by_role("textbox", name="Search...")
            # self.log.click(search_area, "Search Area")
            #
            # search_area.fill("501")
            # option_checkbox = self.page.get_by_role("checkbox", name="501k Recycling LLC")
            # self.log.check(option_checkbox, "501k Recycling LLC")

            search_button = self.page.get_by_role("button", name="Search", exact=True)
            self.log.click(search_button, "Search Button")

            save_success(reporter, method_name)
            step_logger.add_step("Clear fields", "Clear Parameters button reset all fields")

        except Exception as e:
            step_logger.fail_step(method_name, "Search filter flow failed", str(e))
            raise

    @allure.step("Validate task search filters persist")
    def validate_custom_task_search_persist(self, reporter: DBReporter, step_logger: StepLogger, product_key: str, product_base_key: str):
        method_name = get_method_name()

        try:

            cleaned_product_key = self.clean_chip_value(product_key)
            cleaned_product_base_key = self.clean_chip_value(product_base_key)

            filter_icon = self.page.get_by_role("button").filter(has_text="filter_alt")
            self.log.click(filter_icon, "Filter Icon")

            # Wait for the mat-form-field to be visible
            self.page.wait_for_selector('mat-form-field')

            # Find all chip button labels under mat-chip-grid
            chip_buttons = self.page.locator("mat-form-field mat-chip-grid button.chipButton")
            # Count how many buttons are found
            count = chip_buttons.count()
            chip_buttons_values = []
            for i in range(count):
                text = chip_buttons.nth(i).inner_text().strip().replace('\ncancel', '')
                chip_buttons_values.append(text)

            # Make sure that the product key and product base key are within the chip buttons

            assert cleaned_product_key in chip_buttons_values
            assert cleaned_product_base_key in chip_buttons_values

            self.page.keyboard.press("Escape")
            self.log.log("info", "Pressed Escape to close modal")

            save_success(reporter, method_name)
            step_logger.add_step("Clear fields", "Clear Parameters button reset all fields")
        except Exception as e:
            step_logger.fail_step(method_name, "Search filter flow failed", str(e))
            raise

    def clean_chip_value(self, chip_value: str):
        cleaned_value = chip_value
        if(len(chip_value) >= 7):
            cleaned_value = cleaned_value[:6] + "..."
        return cleaned_value
