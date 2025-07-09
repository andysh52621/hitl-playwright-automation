import inspect
import json
import logging
import re

from playwright.sync_api import Page

from dao.test_execution_db_updater_dao import DBReporter
from lib.hitl_logger import LoggerPage
from utils.ado.ado_step_logger import StepLogger
from utils.generic.get_readable_method_name import get_method_name
from utils.generic.post_test_actions_handler import save_success, handle_exception

hitlLogger = logging.getLogger("HitlLogger")


class SchemaPage:
    def __init__(self, page: Page):
        self.page = page
        self.log = LoggerPage(page)

    def edit_action_schema(self, action_schema, reporter: DBReporter, step_logger: StepLogger = None):
        method_name = get_method_name()
        try:
            actions_filter_locator = self.page.locator("div").filter(
                has_text=re.compile(r"^Actionsfilter_alt$")).get_by_role("button").first
            self.log.click(actions_filter_locator, "Actions filter")

            edit_schema_locator = self.page.get_by_role("menuitem", name="Edit Schema")
            self.log.click(edit_schema_locator, "Edit Schema")

            action_schema_locator = self.page.get_by_text("Action Schema")
            self.log.click(action_schema_locator, "Action Schema")

            ace_content_locator = self.page.locator(".ace_content")
            self.log.highlight_only(ace_content_locator, "Ace Content")

            action_schema_str = json.dumps(action_schema, indent=2)

            self.page.evaluate(f'''
                () => {{
                    const editor = ace.edit(document.querySelector(".ace_editor"));
                    editor.setValue({json.dumps(action_schema_str)}, -1);
                }}
            ''')

            submit_button_locator = self.page.get_by_role("button", name="Submit")
            self.log.click(submit_button_locator, "Submit")

            save_success(reporter, method_name)
            if step_logger:
                step_logger.add_step("Edit action schema", f"action schema edited.")
        except Exception as exception:
            if step_logger:
                step_logger.fail_step("Edit action schema", f"action schema edited failed.",
                                      str(exception))
            handle_exception(self, exception, reporter, method_name)
            raise

    def edit_form_schema(self, form_schema, reporter: DBReporter, step_logger: StepLogger = None):
        method_name = get_method_name()
        try:
            form_schema_str = json.dumps(form_schema, indent=2)

            actions_filter_locator = self.page.locator("div").filter(
                has_text=re.compile(r"^Actionsfilter_alt$")
            ).get_by_role("button").first

            self.log.click(actions_filter_locator, "Actions filter")

            edit_schema_locator = self.page.get_by_role("menuitem", name="Edit Schema")
            self.log.click(edit_schema_locator, "Edit Schema")

            form_schema_locator = self.page.get_by_text("Form Schema")
            self.log.click(form_schema_locator, "Form Schema")

            ace_content_locator = self.page.locator(".ace_content")
            self.log.highlight_only(ace_content_locator, "Ace Content")

            self.page.evaluate(f'''
                () => {{
                    const editor = ace.edit(document.querySelector(".ace_editor"));
                    editor.setValue({json.dumps(form_schema_str)}, -1);
                }}
            ''')

            submit_button_locator = self.page.get_by_role("button", name="Submit")
            self.log.click(submit_button_locator, "Submit")

            save_success(reporter, method_name)
            if step_logger:
                step_logger.add_step("Edit form schema", f"form schema edited.")
        except Exception as exception:
            if step_logger:
                step_logger.fail_step("Edit form schema", f"form schema edited failed.",
                                      str(exception))
            handle_exception(self, exception, reporter, method_name)
            raise

    def edit_search_schema(self, search_schema, reporter: DBReporter, step_logger: StepLogger = None):
        method_name = get_method_name()
        try:
            actions_filter_locator = self.page.locator("div").filter(
                has_text=re.compile(r"^Actionsfilter_alt$")).get_by_role("button").first
            self.log.click(actions_filter_locator, "Actions filter")

            edit_schema_locator = self.page.get_by_role("menuitem", name="Edit Schema")
            self.log.click(edit_schema_locator, "Edit Schema")

            search_schema_locator = self.page.get_by_text("Search Schema")
            self.log.click(search_schema_locator, "Search Schema")

            # ace_content_locator = self.page.locator(".ace_content")
            # self.log.highlight_only(ace_content_locator, "Ace Content")

            search_schema_str = json.dumps(search_schema, indent=2)

            self.page.evaluate(f'''
                () => {{
                    const editor = ace.edit(document.querySelector(".ace_editor"));
                    editor.setValue({json.dumps(search_schema_str)}, -1);
                }}
            ''')

            submit_button_locator = self.page.get_by_role("button", name="Submit")
            self.log.click(submit_button_locator, "Submit")

            save_success(reporter, method_name)
            if step_logger:
                step_logger.add_step("Edit search schema", f"search schema emptied.")
        except Exception as exception:
            if step_logger:
                step_logger.fail_step("Edit search schema", f"action schema emptied failed.",
                                      str(exception))
            handle_exception(self, exception, reporter, method_name)
            raise

    def edit_grid_schema(self, grid_schema, reporter: DBReporter, step_logger: StepLogger = None):
        """Edits the grid schema via the UI by pasting into the Ace editor and submitting."""
        method_name = inspect.currentframe().f_code.co_name
        try:
            actions_filter_locator = self.page.locator("div").filter(
                has_text=re.compile(r"^Actionsfilter_alt$")
            ).get_by_role("button").first
            self.log.click(actions_filter_locator, "Actions filter")

            edit_schema_locator = self.page.get_by_role("menuitem", name="Edit Schema")
            self.log.click(edit_schema_locator, "Edit Schema")

            grid_schema_locator = self.page.get_by_text("Grid Schema")
            self.log.click(grid_schema_locator, "Grid Schema")

            ace_content_locator = self.page.locator(".ace_content")
            self.log.highlight_only(ace_content_locator, "Ace Content")

            grid_schema_str = json.dumps(grid_schema, indent=2)

            self.page.evaluate(f'''
                () => {{
                    const editor = ace.edit(document.querySelector(".ace_editor"));
                    editor.setValue({json.dumps(grid_schema_str)}, -1);
                }}
            ''')

            submit_button_locator = self.page.get_by_role("button", name="Submit")
            self.log.click(submit_button_locator, "Submit")

            save_success(reporter, method_name)
            if step_logger:
                step_logger.add_step("Edit grid schema", "grid schema edited.")
        except Exception as exception:
            if step_logger:
                step_logger.fail_step("Edit grid schema", "grid schema edit failed.", str(exception))
            handle_exception(self, exception, reporter, method_name)
            raise

    def edit_data_schema(self, data_schema, reporter: DBReporter, step_logger: StepLogger = None):
        """Attempts to edit the data schema via the UI. If schema editing is disabled, verifies the warning."""
        method_name = inspect.currentframe().f_code.co_name
        try:

            actions_filter_locator = self.page.locator("div.grid-header button:has-text('Actions')").first
            actions_filter_locator.wait_for(state="visible", timeout=10000)
            self.log.click(actions_filter_locator, "Actions filter")

            edit_schema_locator = self.page.get_by_role("menuitem", name="Edit Schema")
            self.log.click(edit_schema_locator, "Edit Schema")

            # Check for warning message first
            warning_locator = self.page.locator(
                "text=You cannot edit the Data Schema while tasks are associated with this entity.")
            if warning_locator.is_visible(timeout=3000):
                self.log.info("Data Schema editing is disabled due to associated tasks.")
                if step_logger:
                    step_logger.add_step(
                        "Verify Data schema restriction",
                        "Data Schema edit restriction message is displayed as expected."
                    )
                save_success(reporter, method_name)
                return  # Exit early as no edit is expected

            # Proceed to grid schema if editing is allowed
            data_schema_locator = self.page.get_by_text("Data Schema")
            self.log.click(data_schema_locator, "Data Schema")

            ace_content_locator = self.page.locator(".ace_content")
            self.log.highlight_only(ace_content_locator, "Ace Content")

            grid_schema_str = json.dumps(data_schema, indent=2)

            self.page.evaluate(f'''
                () => {{
                    const editor = ace.edit(document.querySelector(".ace_editor"));
                    editor.setValue({json.dumps(grid_schema_str)}, -1);
                }}
            ''')

            submit_button_locator = self.page.get_by_role("button", name="Submit")
            self.log.click(submit_button_locator, "Submit")

            save_success(reporter, method_name)
            if step_logger:
                step_logger.add_step("Edit data schema", "Data schema edited successfully.")
        except Exception as exception:
            if step_logger:
                step_logger.fail_step("Edit data schema", "Data schema edit failed.", str(exception))
            handle_exception(self, exception, reporter, method_name)
            raise
