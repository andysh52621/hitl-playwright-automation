import logging

import allure

from dao.api_ui_taskId_mapper_dao import TaskIdMapperDAO
from dao.test_execution_db_updater_dao import DBReporter
from db_engine.test_automation_engine import get_test_db_engine
from pages.ui_pages.tm_list_page import TaskManagerListPage
from utils.ado.ado_step_logger import StepLogger
from utils.generic.get_readable_method_name import get_method_name
from utils.generic.post_test_actions_handler import save_success, handle_exception

hitlLogger = logging.getLogger("HitlLogger")


class ProductVendorLookupPage:
    def __init__(self, page):
        from lib.hitl_logger import LoggerPage
        self.page = page
        self.log = LoggerPage(page)
        self.dao = TaskIdMapperDAO(get_test_db_engine())

    @allure.step("Validate error when no schema is associated")
    def validate_missing_search_schema(self, reporter: DBReporter, step_logger: StepLogger):
        method_name = get_method_name()
        try:
            search_button = self.page.get_by_role("button", name="Search")
            self.log.click(search_button, "Search button")

            error_label = self.page.get_by_text("Error: Missing data schema or form schema.")
            error_label.wait_for(state="visible")
            assert error_label.is_visible(), "Expected error message for missing schema"

            save_success(reporter, method_name)
            step_logger.add_step("Missing schema validation", "Error message shown as expected")
        except Exception as e:
            step_logger.fail_step("Missing schema validation", "Error message should appear", str(e))
            raise

    @allure.step("Validate Search modal for vendor lookup")
    def validate_search_modal_behavior(self, reporter: DBReporter, step_logger: StepLogger):
        method_name = get_method_name()
        try:
            actions_btn = self.page.get_by_test_id("task-grid").get_by_role("button", name="Actions").first
            self.log.click(actions_btn, "Actions Button")

            edit_btn = self.page.get_by_role("menuitem", name="Edit")
            self.log.click(edit_btn, "Edit Menu Option")

            search_button = self.page.get_by_role("button", name="Search")
            self.log.click(search_button, "Search button")

            search_btn = self.page.get_by_role("button", name="Search", exact=True)
            submit_btn = self.page.get_by_role("button", name="Submit", exact=True)
            clear_param_btn = self.page.get_by_role("button", name="Clear Parameters", exact=True)

            assert search_btn.is_disabled(), "Vendor lookup: Search should be disabled initially"
            assert submit_btn.is_disabled(), "Vendor lookup: Submit should be disabled initially"
            assert clear_param_btn.is_enabled(), "Vendor lookup: Clear Parameters should be enabled initially"

            self.enter_and_select_vendor_name(reporter, step_logger)

            save_success(reporter, method_name)
            step_logger.add_step("Search modal form validation", "Search button state and field verified")
        except Exception as e:
            step_logger.fail_step("Search modal form validation", "Search button state and field verification failed",
                                  str(e))
            raise

    def get_filter_task(self, test_meta, test_user, reporter: DBReporter,
                        step_logger: StepLogger = None):
        method_name = get_method_name()

        try:
            tasks_to_resolve = self.dao.get_tasks_to_resolve(test_meta, test_user, 1)
            hitlLogger.info(f"🔹 Loaded {len(tasks_to_resolve)} records")

            for row in tasks_to_resolve:
                hitlLogger.info(f"🔹 Resolving task id: {row.TaskId}")
                TaskManagerListPage(self.page).filter_task(str(row.TaskId), reporter, step_logger)

            actions_btn = self.page.get_by_test_id("task-grid").get_by_role("button", name="Actions").first
            self.log.click(actions_btn, "Actions Button")

            edit_btn = self.page.get_by_role("menuitem", name="Edit")
            self.log.click(edit_btn, "Edit Menu Option")

            save_success(reporter, method_name)
            if step_logger:
                step_logger.add_step("Resolve tasks", "All tasks resolved successfully")

        except Exception as exception:
            if step_logger:
                step_logger.fail_step("Resolve tasks", "Task resolution failed !", str(exception))
            handle_exception(self, exception, reporter, method_name)
            raise

    def search_match_to_existing(self, reporter: DBReporter, step_logger: StepLogger = None):
        method_name = get_method_name()
        try:

            save_success(reporter, method_name)
            if step_logger:
                step_logger.add_step("Search for Match", f"Searched for Match To Existing")

        except Exception as exception:
            if step_logger:
                step_logger.fail_step("Search for Match", f"Searched for Match To Existing failed", str(exception))
            handle_exception(self, exception, reporter, method_name)
            raise

    @allure.step("Validate error when no schema is associated")
    def validate_missing_search_schema(self, reporter: DBReporter, step_logger: StepLogger):
        method_name = get_method_name()
        try:
            search_button = self.page.get_by_role("button", name="Search")
            self.log.click(search_button, "Search button")

            error_label = self.page.get_by_text("Error: Missing data schema or form schema.")
            error_label.wait_for(state="visible")
            self.log.highlight_only(error_label, "Error message")

            assert error_label.is_visible(), "Expected error message for missing schema"

            self.close_modal(reporter, step_logger)

            cancel_btn = self.page.get_by_role("button", name="Cancel", exact=True)
            self.log.click(cancel_btn, "Cancel button")

            yes_bttn = self.page.get_by_role("button", name="Yes", exact=True)
            self.log.click(yes_bttn, "Confirm cancel button")

            save_success(reporter, method_name)
            step_logger.add_step("Missing schema validation", "Error message shown as expected")
        except Exception as e:
            step_logger.fail_step("Missing schema validation", "Error message should appear", str(e))
            raise

    @allure.step("Close modal dialog gracefully")
    def close_modal(self, reporter: DBReporter, step_logger: StepLogger):
        method_name = get_method_name()
        try:
            modal = self.page.locator("div[role='dialog'], .modal-content")

            self.page.keyboard.press("Escape")
            self.log.log("info", "Pressed Escape to close modal")

            modal.wait_for(state="detached", timeout=3000)
            save_success(reporter, method_name)
            step_logger.add_step("Close modal", "Modal closed successfully")
        except Exception as e:
            step_logger.fail_step("Close modal", "Failed to close modal", str(e))
            raise

    @allure.step("Type vendor name and select autocomplete suggestion")
    def enter_and_select_vendor_name(self, reporter: DBReporter, step_logger: StepLogger):
        method_name = get_method_name()
        try:

            # Locate the input for Vendor Name
            vendor_input = self.page.get_by_role("combobox", name="Vendor Name*")
            self.log.send_key_strokes(vendor_input, "amerisource", "Vendor Name input")

            # Wait for dropdown options to appear
            suggestion_option = self.page.locator(
                "mat-option span.mdc-list-item__primary-text",
                has_text="Amerisourcebergen Corporation"
            )
            self.log.click_first(suggestion_option, "Amerisourcebergen Corporation suggestion value")

            search_button = self.page.get_by_role("button", name="Search", exact=True)
            self.log.click(search_button, "Search button")

            select_checkbox = self.page.get_by_role("checkbox", name="Press Space to toggle row")
            self.log.check(select_checkbox, "Select checkbox")

            submit_button = self.page.get_by_role("button", name="Submit", exact=True)

            assert not search_button.is_disabled(), "Vendor lookup: Search should be enabled after Vendor Name"
            assert not submit_button.is_disabled(), "Vendor lookup: Submit should be enabled after Vendor Name"

            self.log.click(submit_button, "Submit button")

            save_for_later_button = self.page.get_by_role("button", name="Save for later")
            self.log.click(save_for_later_button, "Save for later button")

            actions_btn = self.page.get_by_test_id("task-grid").get_by_role("button", name="Actions").first
            self.log.click(actions_btn, "Actions Button")

            edit_btn = self.page.get_by_role("menuitem", name="Edit")
            self.log.click(edit_btn, "Edit Menu Option")

            match2existing = self.page.get_by_role("textbox", name="Match To Existing")
            self.log.click(match2existing, "Match to Existing")

            self.log.assert_contains_text(match2existing, "AmerisourceBergen Corp",
                                          "Match to Existing container: AmerisourceBergen Corp")

            save_success(reporter, method_name)
            step_logger.add_step("Enter vendor name", "Selected 'Amerisourcebergen Corporation' from dropdown")

        except Exception as e:
            step_logger.fail_step("Enter vendor name", "Failed to select suggestion", str(e))
            raise
