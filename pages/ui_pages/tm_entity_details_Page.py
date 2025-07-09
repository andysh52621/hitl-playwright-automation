import logging
import re


from playwright.sync_api import Page

from dao.test_execution_db_updater_dao import DBReporter
from lib.hitl_logger import LoggerPage
from pages.core_pages.home_page import HomePage
from utils.ado.ado_step_logger import StepLogger
from utils.generic.get_readable_method_name import get_method_name
from utils.generic.post_test_actions_handler import save_success, handle_exception

hitlLogger = logging.getLogger("HitlLogger")


class EntityDetailsPage:
    def __init__(self, page: Page):
        self.page = page
        self.home_page = HomePage(page)
        self.log = LoggerPage(page)

    def select_domain_add_entity(self, domain, reporter: DBReporter, step_logger: StepLogger = None):
        method_name = get_method_name()
        try:
            self.home_page.select_domain_to_add_entity(domain, "Add Entity", reporter, step_logger)
            save_success(reporter, method_name)
            if step_logger:
                step_logger.add_step("Select domain to add entity", f"Domain '{domain}' selected for entity creation")
        except Exception as exception:
            if step_logger:
                step_logger.fail_step("Select domain to add entity", f"Domain '{domain}' selected for entity creation",
                                      str(exception))
            handle_exception(self, exception, reporter, method_name)
            raise

    def create_entity(self, entity, reporter: DBReporter, step_logger: StepLogger = None):
        method_name = get_method_name()
        try:
            entity_name_locator = self.page.get_by_role("textbox", name="Entity Name")
            self.log.fill(entity_name_locator, entity, "Entity Name")

            display_name_locator = self.page.get_by_role("textbox", name="Display Name")
            self.log.fill(display_name_locator, "Auto Test Entity Name", "Display Name")

            description_locator = self.page.get_by_text("Description")
            self.log.fill(description_locator, "Auto Test Description", "Description")

            email_locator = self.page.get_by_role("textbox", name="Contact Email(s)")
            self.log.fill(email_locator, "andy.sharma@vizientinc.com", "Contact Email(s)")

            notification_flag_locator = self.page.get_by_label("Notification Flag").get_by_text("False")
            self.log.click(notification_flag_locator, "Notification Flag")

            notification_menu_locator = self.page.get_by_text("True")
            self.log.click(notification_menu_locator, "Notification True")

            navigation_flag_locator = self.page.get_by_label("Navigation Flag").get_by_text("False")
            self.log.click(navigation_flag_locator, "Navigation Flag")

            navigation_menu_locator = self.page.get_by_role("option", name="False")
            self.log.click(navigation_menu_locator, "Navigation False")

            global_client_id_locator = self.page.get_by_text("Global Client Id")
            self.log.fill(global_client_id_locator, "Gb-987045-UI", "Global Client Id")

            global_client_secret_locator = self.page.get_by_text("Global Client Secret")
            self.log.fill(global_client_secret_locator, "e35j5-o7rj-9jwe-gb44", "Global Client Secret")

            submit_button_locator = self.page.get_by_role("button", name="Submit")
            self.log.click(submit_button_locator, "Submit Button")

            save_success(reporter, method_name)
            if step_logger:
                step_logger.add_step("Create entity", "Entity form submitted")
        except Exception as exception:
            if step_logger:
                step_logger.fail_step("Create entity", "Entity form submitted", str(exception))
            handle_exception(self, exception, reporter, method_name)
            raise

    def disable_entity(self, reporter: DBReporter, step_logger: StepLogger = None):
        method_name = get_method_name()
        try:
            actions_filter_locator = self.page.locator("div.grid-header button:has-text('Actions')").first
            actions_filter_locator.wait_for(state="visible", timeout=10000)
            self.log.click(actions_filter_locator, "Actions filter")

            edit_schema_locator = self.page.get_by_role("menuitem", name="Edit Schema")
            self.log.click(edit_schema_locator, "Edit Schema")

            # insert logic here
            entity_is_active_locator = self.page.get_by_text("Entity is Active")
            self.log.click(entity_is_active_locator, "Entity is Active")

            submit_button_locator = self.page.get_by_role("button", name="Submit")
            self.log.click(submit_button_locator, "Submit Button")

            save_success(reporter, method_name)
            if step_logger:
                step_logger.add_step("Disable entity", "Entity disabled")
        except Exception as exception:
            if step_logger:
                step_logger.fail_step("Disable entity", "Entity disabled", str(exception))
            handle_exception(self, exception, reporter, method_name)
            raise

    def set_navigation_flag(self, meta, flag_value: bool, reporter: DBReporter, step_logger: StepLogger = None):

        method_name = get_method_name()
        try:
            # Step 1: Open Actions → Edit Schema
            actions_button = self.page.locator("div.grid-header button:has-text('Actions')").first
            self.log.click(actions_button, "Open Actions menu")

            edit_schema_option = self.page.get_by_role("menuitem", name="Edit Schema")
            self.log.click(edit_schema_option, "Edit Schema")

            # Step 2: Open dropdown and select 'True'
            nav_flag_dropdown = self.page.get_by_role("combobox", name="Navigation Flag")
            self.log.click(nav_flag_dropdown, "Navigation Flag Dropdown")

            option_text = "True" if flag_value else "False"
            dropdown_option = self.page.get_by_role("option", name=option_text)
            self.log.click(dropdown_option, f"Select '{option_text}' for Navigation Flag")

            # Step 3: Submit changes
            submit_button = self.page.get_by_role("button", name="Submit")
            self.log.click(submit_button, "Submit Button")

            save_success(reporter, method_name)
            if step_logger:
                step_logger.add_step("Set Navigation Flag", "Navigation Flag set to True and submitted")

        except Exception as e:
            if step_logger:
                step_logger.fail_step("Set Navigation Flag", "Failed to set flag", str(e))
            handle_exception(self, e, reporter, method_name)
            raise

    def toggle_task_search(self, enable_search: bool, reporter: DBReporter, step_logger: StepLogger = None):
        method_name = get_method_name()
        try:
            # Step 1: Open Actions menu
            actions_filter_locator = self.page.locator("div.grid-header button:has-text('Actions')").first
            actions_filter_locator.wait_for(state="visible", timeout=10000)
            self.log.click(actions_filter_locator, "Actions filter")

            # Step 2: Click Edit Schema
            edit_schema_locator = self.page.get_by_role("menuitem", name="Edit Schema")
            self.log.click(edit_schema_locator, "Edit Schema")

            # Step 3: Locate the toggle switch by its aria-label
            toggle_button = self.page.get_by_role("switch", name=re.compile(r"Task Search is (Enabled|Disabled)", re.IGNORECASE))
            toggle_button.wait_for(state="visible", timeout=5000)

            # Step 4: Read current toggle state via aria-checked
            current_state = toggle_button.get_attribute("aria-checked") == "true"
            hitlLogger.info(f"Current toggle state: {current_state}")

            # Step 5: Toggle if needed
            if current_state != enable_search:
                self.log.click(toggle_button, f"{'Enable' if enable_search else 'Disable'} Task Search toggle")
            else:
                hitlLogger.info("Toggle already in desired state.")

            # Step 6: Submit changes
            submit_button_locator = self.page.get_by_role("button", name="Submit")
            self.log.click(submit_button_locator, "Submit Button")

            # Step 7: Success logging
            save_success(reporter, method_name)
            if step_logger:
                step_logger.add_step("Toggle Task Search", f"Task Search {'enabled' if enable_search else 'disabled'}")

        except Exception as exception:
            if step_logger:
                step_logger.fail_step("Toggle Task Search", "Failed to toggle search", str(exception))
            handle_exception(self, exception, reporter, method_name)
            raise



