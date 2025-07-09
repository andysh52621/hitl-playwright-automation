import logging

from dao.test_execution_db_updater_dao import DBReporter
from lib.hitl_logger import LoggerPage
from utils.ado.ado_step_logger import StepLogger
from utils.generic.get_readable_method_name import get_method_name
from utils.generic.post_test_actions_handler import save_success, handle_exception

hitlLogger = logging.getLogger("HitlLogger")


class HomePage:

    def __init__(self, page):
        self.page = page
        self.log = LoggerPage(page)

    def click_navigation_menu(self, reporter: DBReporter, step_logger: StepLogger = None):
        method_name = get_method_name()
        try:
            locator = self.page.locator("#main-nav-menu")
            self.log.click(locator, "Main Navigation Menu")
            save_success(reporter, method_name)
            if step_logger:
                step_logger.add_step("Click navigation menu", "Navigation menu is clicked")
        except Exception as exception:
            if step_logger:
                step_logger.fail_step("Click navigation menu", "Navigation menu is clicked", str(exception))
            handle_exception(self, exception, reporter, method_name)
            raise

    def click_person_icon(self, user_id, reporter: DBReporter, step_logger: StepLogger = None):
        method_name = get_method_name()
        try:
            locator = self.page.get_by_text("person")
            self.log.click(locator, "Person Icon")
            self.highlight_person_menu(user_id, reporter, step_logger)
            save_success(reporter, method_name)
            if step_logger:
                step_logger.add_step("Click person icon", "Person menu is visible")
        except Exception as exception:
            if step_logger:
                step_logger.fail_step("Click person icon", "Person menu is visible", str(exception))
            handle_exception(self, exception, reporter, method_name)
            raise

    def click_task_manager(self, reporter: DBReporter, step_logger: StepLogger = None):
        method_name = get_method_name()
        try:
            locator = self.page.get_by_role("menuitem", name="Task Manager")
            self.log.click(locator, "Task Manager Menu Item")
            save_success(reporter, method_name)
            if step_logger:
                step_logger.add_step("Click Task Manager", "Task Manager menu is opened")
        except Exception as exception:
            if step_logger:
                step_logger.fail_step("Click Task Manager", "Task Manager menu is opened", str(exception))
            handle_exception(self, exception, reporter, method_name)
            raise

    def click_task_manager_home(self, reporter: DBReporter, step_logger: StepLogger = None):
        method_name = get_method_name()
        try:
            locator = self.page.get_by_role("button", name="Home")
            self.log.click(locator, "Task Manager Home")
            save_success(reporter, method_name)
            if step_logger:
                step_logger.add_step("Click Home button", "Dashboard home is loaded")
        except Exception as exception:
            if step_logger:
                step_logger.fail_step("Click Home button", "Dashboard home is loaded", str(exception))
            handle_exception(self, exception, reporter, method_name)
            raise

    def validate_hitl_dashboard(self, username, reporter: DBReporter, step_logger: StepLogger = None):
        method_name = get_method_name()
        try:
            locator = self.page.get_by_role("button", name="Domain")
            self.log.wait_for_visible(locator, "Dashboard Domain Link")
            hitlLogger.info(f"🔹 Dashboard home test passed for user: {username}")
            save_success(reporter, method_name)
            if step_logger:
                step_logger.add_step("Validate HITL dashboard", "Dashboard is visible")
        except Exception as exception:
            if step_logger:
                step_logger.fail_step("Validate HITL dashboard", "Dashboard is visible", str(exception))
            handle_exception(self, exception, reporter, method_name)
            raise

    def select_domain_card(self, domain, entity, reporter: DBReporter, step_logger: StepLogger = None):
        method_name = get_method_name()
        try:
            # Step 1: Find domain card root using domain name
            title = self.page.locator("div[data-testid='card-title']").filter(has_text=domain).first
            domain_card = title.locator("xpath=ancestor::app-card").first
            self.log.highlight_only(domain_card, f"Domain: {domain}")

            # Step 2: Click first mat-select inside the domain card (assumed to be the Entity dropdown)
            entity_dropdown = domain_card.locator("mat-select").first
            self.log.click(entity_dropdown, f"Click Entity Dropdown inside {domain}")

            # Step 3: Select the correct entity option from the overlay panel
            entity_option = self.page.locator(f"//span[normalize-space(text())='{entity}']").first
            self.log.click(entity_option, f"Select Entity Option: {entity}")

            save_success(reporter, method_name)
            if step_logger:
                step_logger.add_step("Select domain and entity", f"{domain} / {entity} selected")

        except Exception as exception:
            if step_logger:
                step_logger.fail_step("Select domain and entity", f"{domain} / {entity} failed", str(exception))
            handle_exception(self, exception, reporter, method_name)
            raise

    def select_domain_to_add_entity(self, domain, entity, reporter: DBReporter, step_logger: StepLogger = None):
        method_name = get_method_name()
        try:
            locator = self.page.locator("div[data-testid='card-title']").filter(has_text=domain).first
            self.log.highlight_only(locator, f"Domain: {domain}")

            entity_locator = locator.locator("xpath=ancestor::app-card").locator("mat-select").first
            self.log.click(entity_locator, f"Entity Dropdown for Domain: {domain}")

            # ✅ Updated locator targeting <b> element inside mat-option
            overlay_option = self.page.locator(
                f"//div[contains(@class, 'cdk-overlay-pane')]//mat-option//b[normalize-space(text())='{entity}']"
            )
            overlay_option.wait_for(state="visible", timeout=10000)
            self.log.click(overlay_option, f"Select Entity Option: {entity}")

            save_success(reporter, method_name)
            if step_logger:
                step_logger.add_step("Select domain for entity", f"{domain} / {entity} selected for entity creation")

        except Exception as exception:
            if step_logger:
                step_logger.fail_step("Select domain for entity", f"{domain} / {entity} selected", str(exception))
            handle_exception(self, exception, reporter, method_name)
            raise

    def highlight_person_menu(self, user_id, reporter: DBReporter, step_logger: StepLogger = None):
        method_name = get_method_name()
        try:
            self.log.highlight_only(self.page.get_by_text("person"), "Person Icon")
            self.log.highlight_only(self.page.get_by_text("Logged In As: "), "Logged In As:" + str(user_id))
            self.log.highlight_only(self.page.get_by_text('User Profile'), "user profile")
            self.log.highlight_only(self.page.get_by_text("Logout"), "Logout")
            save_success(reporter, method_name)
            if step_logger:
                step_logger.add_step("Highlight person menu", "User profile and logout options highlighted")

        except Exception as exception:
            if step_logger:
                step_logger.fail_step("Highlight person menu", "User profile and logout options highlighted",
                                      str(exception))
            handle_exception(self, exception, reporter, method_name)
            raise

    def edit_domain(self, domain, reporter: DBReporter, step_logger: StepLogger = None):
        method_name = get_method_name()
        try:
            title = self.page.locator("div[data-testid='card-title']").filter(has_text=domain).first
            self.log.highlight_only(title, f"Domain: {domain}")

            domain_card = title.locator("xpath=ancestor::app-card").first
            edit_icon = domain_card.locator("button:has(mat-icon:has-text('edit'))").first

            self.log.click(edit_icon, "Edit Domain Icon")

            save_success(reporter, method_name)
            if step_logger:
                step_logger.add_step("Edit domain", f"Edit clicked for domain: {domain}")

        except Exception as exception:
            if step_logger:
                step_logger.fail_step("Edit domain", f"Failed to edit domain: {domain}", str(exception))
            handle_exception(self, exception, reporter, method_name)
            raise

