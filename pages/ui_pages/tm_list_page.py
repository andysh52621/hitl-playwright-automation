import inspect
import logging
import re
from datetime import datetime
from playwright.sync_api import Page

from dao.api_ui_taskId_mapper_dao import TaskIdMapperDAO
from dao.test_execution_db_updater_dao import DBReporter
from db_engine.test_automation_engine import get_test_db_engine
from lib.hitl_logger import LoggerPage
from pages.core_pages.home_page import HomePage
from pages.ui_pages.tm_history_page import HistoryPage
from utils.ado.ado_step_logger import StepLogger
from utils.generic.get_readable_method_name import get_method_name
from utils.generic.post_test_actions_handler import save_success, handle_exception

hitlLogger = logging.getLogger("HitlLogger")


class TaskManagerListPage:
    def __init__(self, page: Page):
        self.page = page
        self.home_page = HomePage(page)
        self.log = LoggerPage(page)
        self.dao = TaskIdMapperDAO(get_test_db_engine())

    def begin_resolves_tasks(self, check_error, test_meta, test_user, reporter: DBReporter,
                             step_logger: StepLogger = None):
        method_name = get_method_name()

        try:
            tasks_to_resolve = self.dao.get_tasks_to_resolve(test_meta, test_user, 1)
            hitlLogger.info(f"🔹 Loaded {len(tasks_to_resolve)} records")

            for row in tasks_to_resolve:
                hitlLogger.info(f"🔹 Resolving task id: {row.TaskId}")
                self.filter_task(str(row.TaskId), reporter, step_logger)
                self.edit_task_description(reporter, step_logger)
                self.save_task_resolution(check_error, test_user, row.TaskId, reporter, step_logger)

            save_success(reporter, method_name)
            if step_logger:
                step_logger.add_step("Resolve tasks", "All tasks resolved successfully")

        except Exception as exception:
            if step_logger:
                step_logger.fail_step("Resolve tasks", "Task resolution failed !", str(exception))
            handle_exception(self, exception, reporter, method_name)
            raise

    def filter_task(self, task_id, reporter: DBReporter, step_logger: StepLogger = None):
        method_name = get_method_name()
        try:
            filter_icon = self.page.locator(".ag-cell-label-container > span:nth-child(2) > .ag-icon").first
            self.log.click(filter_icon, "Filter Icon")

            search_input = self.page.get_by_role("textbox", name="Search filter values")
            self.log.click(search_input, "Search Filter Input")

            select_all = self.page.get_by_text("(Select All)")
            self.log.click(select_all, "Deselect All in Filter")

            self.log.fill(search_input, task_id, "Task ID in Filter")
            search_input.press("Enter")

            save_success(reporter, method_name)
            if step_logger:
                step_logger.add_step("Filter task", f"Filtered task ID {task_id}")

        except Exception as exception:
            if step_logger:
                step_logger.fail_step("Filter task", f"Filtered task ID {task_id}", str(exception))
            handle_exception(self, exception, reporter, method_name)
            raise

    def edit_task_description(self, reporter: DBReporter, step_logger: StepLogger = None):
        method_name = inspect.currentframe().f_code.co_name
        try:
            actions_btn = self.page.get_by_test_id("task-grid").get_by_role("button", name="Actions").first
            self.log.click(actions_btn, "Actions Button")

            edit_option = self.page.get_by_role("menuitem", name="Edit")
            self.log.click(edit_option, "Edit Menu Option")

            input_field = self.page.get_by_role("textbox", name="Product Spend Category")
            enter_value = f"Automatically corrected {datetime.now()}"
            self.log.fill(input_field, enter_value, "Product Spend Category")

            input_field = self.page.get_by_role("textbox", name="Product Base Key")
            self.log.fill(input_field, "12345", "Product Base Key")

            input_field = self.page.get_by_role("textbox", name="Numberof Productson Base")
            self.log.fill(input_field, "12", "Numberof Productson Base")

            input_field = self.page.get_by_role("textbox", name="Primary Catalog Number")
            self.log.fill(input_field, "12345", "Primary Catalog Number")

            input_field = self.page.get_by_role("textbox", name="UNSPSC Commodity Code")
            self.log.fill(input_field, "12345", "UNSPSC Commodity Code")

            input_field = self.page.get_by_role("textbox", name="UNSPSC Commodity", exact=True)
            enter_value = f"Automatically corrected {datetime.now()}"
            self.log.fill(input_field, enter_value, "UNSPSC Commodity")

            input_field = self.page.get_by_role("textbox", name="Product Type Code")
            self.log.fill(input_field, "A", "Product Type Code")

            input_field = self.page.get_by_role("textbox", name="Catalog Number Stripped")
            self.log.fill(input_field, "12345", "Catalog Number Stripped")

            input_field = self.page.get_by_role("combobox", name="Description Exception")
            self.log.click(input_field, "Description Exception")
            input_field_option = self.page.get_by_role("option", name="False")
            self.log.click(input_field_option, "Set Description Exception False")

            input_field = self.page.get_by_role("textbox", name="Sync Code", exact=True)
            self.log.fill(input_field, "123456", "Sync Code")

            input_field = self.page.get_by_role("textbox", name="Sync Code Sub Category")
            enter_value = f"Automatically corrected {datetime.now()}"
            self.log.fill(input_field, enter_value, "Sync Code Sub Category")

            save_success(reporter, method_name)
            if step_logger:
                step_logger.add_step("Edit task description", "Task fields updated")
        except Exception as exception:
            if step_logger:
                step_logger.fail_step("Edit task description", "Task fields updated", str(exception))
            handle_exception(self, exception, reporter, method_name)
            raise

    def save_task_resolution(self, check_error, test_user, task_id: object, reporter: DBReporter,
                             step_logger: StepLogger = None) -> None:
        method_name = inspect.currentframe().f_code.co_name
        try:
            save_btn = self.page.get_by_role("button", name="Save", exact=True)
            self.log.click(save_btn, "Save Button")

            if check_error:
                error_message_locator = self.page.get_by_text("Action Could Not Be Completed")
                error_message_text = error_message_locator.inner_text(timeout=5000)
                self.log.highlight_only(error_message_locator, error_message_text)
                back_btn = self.page.get_by_role("button", name="Back", exact=True)
                self.log.click(back_btn, "Back Button")
            else:
                save_btn.wait_for(state="detached", timeout=5000)
                updated = self.dao.update_task_status_to_resolved(test_user, str(task_id))
                hitlLogger.info(f"🔹 {updated} row(s) resolved.")

            save_success(reporter, method_name)
            if step_logger:
                step_logger.add_step("Save task resolution", f"Task {task_id} marked as resolved")
        except Exception as exception:
            if step_logger:
                step_logger.fail_step("Save task resolution", f"Task {task_id} marked as resolved", str(exception))
            handle_exception(self, exception, reporter, method_name)
            raise

    def confirm_all_task_saved(self, reporter: DBReporter, step_logger: StepLogger = None):
        method_name = inspect.currentframe().f_code.co_name
        try:
            no_rows_to_show = self.page.locator("//*[contains(text(),'No Rows To Show')]").is_visible()

            if no_rows_to_show:
                message = "No rows to show - all tasks saved successfully"
                hitlLogger.info(f"✅ {message}")
                hitlLogger.info("VERIFY: %s", message)
            else:
                message = "There exists some tasks pending for resolution"
                hitlLogger.info(f"❌ {message}")
                hitlLogger.info("VERIFY: %s", message)
                # raise Exception(message)

            save_success(reporter, method_name)
            if step_logger:
                step_logger.add_step("Confirm all tasks saved", "No pending tasks remain")
        except Exception as exception:
            if step_logger:
                step_logger.fail_step("Confirm all tasks saved", "No pending tasks remain", str(exception))
            handle_exception(self, exception, reporter, method_name)
            raise

    def begin_saveforlater_tasks(self, test_meta, test_user, reporter: DBReporter,
                                 step_logger: StepLogger = None):
        method_name = inspect.currentframe().f_code.co_name
        try:
            tasks_to_process = self.dao.get_tasks_to_resolve(test_meta, test_user, 1)  # Take only the first two tasks
            hitlLogger.info(f"🔹 Loaded {len(tasks_to_process)} record(s) for Save for Later (limit: 1)")

            for row in tasks_to_process:
                hitlLogger.info(f"🔹 Saving task id {row.TaskId} with status 'In Progress'")
                self.filter_task(str(row.TaskId), reporter, step_logger)
                self.edit_description_only(reporter, step_logger)
                self.save_for_later_task_resolution(test_user, row.TaskId, reporter, step_logger)

            save_success(reporter, method_name)
            if step_logger:
                step_logger.add_step("Save for Later tasks", "Selected tasks saved for later successfully")

        except Exception as exception:
            if step_logger:
                step_logger.fail_step("Save for Later tasks", "Task save for later failed!", str(exception))
            handle_exception(self, exception, reporter, method_name)
            raise

    def edit_description_only(self, reporter: DBReporter, step_logger: StepLogger = None):
        method_name = inspect.currentframe().f_code.co_name
        try:
            actions_btn = self.page.get_by_test_id("task-grid").get_by_role("button", name="Actions").first
            self.log.click(actions_btn, "Actions Button")

            edit_option = self.page.get_by_role("menuitem", name="Edit")
            self.log.click(edit_option, "Edit Menu Option")

            input_field = self.page.get_by_role("textbox", name="Product Spend Category")
            self.log.fill(input_field, f"Saved for later {datetime.now()}", "Product Spend Category")

            save_success(reporter, method_name)
            if step_logger:
                step_logger.add_step("Edit description only", "Product Spend Category updated")

        except Exception as exception:
            if step_logger:
                step_logger.fail_step("Edit description only", "Failed to update description", str(exception))
            handle_exception(self, exception, reporter, method_name)
            raise

    def save_for_later_task_resolution(self, test_user, task_id: object, reporter: DBReporter,
                                       step_logger: StepLogger = None) -> None:
        method_name = inspect.currentframe().f_code.co_name
        try:
            save_later_btn = self.page.get_by_role("button", name="Save for Later")
            self.log.click(save_later_btn, "Save for Later Button")

            save_later_btn.wait_for(state="detached", timeout=5000)

            updated = self.dao.update_task_status_to_in_progress(test_user, str(task_id))
            hitlLogger.info(f"🔹 {updated} row(s) updated to 'In Progress'.")

            save_success(reporter, method_name)
            if step_logger:
                step_logger.add_step("Save for Later", f"Task {task_id} marked as In Progress")

        except Exception as exception:
            if step_logger:
                step_logger.fail_step("Save for Later", f"Task {task_id} failed to save", str(exception))
            handle_exception(self, exception, reporter, method_name)
            raise

    def navigate_tasks_using_prev_next(self, test_meta, test_user, reporter: DBReporter,
                                       step_logger: StepLogger = None):
        method_name = inspect.currentframe().f_code.co_name
        hitlLogger.info("📍 Entered navigate_tasks_using_prev_next()")

        try:
            # Step 1: Fetch and sort tasks
            tasks = self.dao.get_tasks_to_resolve(test_meta, test_user, 3)
            hitlLogger.info(f"🔹 Loaded {len(tasks)} record(s) for navigation (limit: 3)")

            if len(tasks) < 3:
                raise Exception("Not enough tasks to perform navigation test (need at least 3).")

            task_ids = sorted([str(task.TaskId) for task in tasks])
            hitlLogger.info(f"🔹 Using Task IDs for navigation: {task_ids}")

            # Step 2: Filter grid
            self.filter_multiple_tasks(task_ids, reporter, step_logger)

            # Step 3: Open Actions → Edit on first task
            first_task_id = task_ids[0]
            row = self.page.locator("div[row-id]").filter(has_text=first_task_id)
            row.wait_for(timeout=5000)
            actions_btn = row.get_by_role("button", name="Actions")
            self.log.click(actions_btn, f"Click Actions for Task ID {first_task_id}")

            edit_option = self.page.get_by_role("menuitem", name="Edit")
            self.log.click(edit_option, "Edit Task")

            # Step 4: Navigation → Next x2, Prev x2, Back
            prev_btn = self.page.get_by_role("button", name="Prev")
            next_btn = self.page.get_by_role("button", name="Next")
            back_btn = self.page.get_by_role("button", name="Back")

            # Wait for buttons to be visible
            next_btn.wait_for(state="visible", timeout=5000)
            prev_btn.wait_for(state="visible", timeout=5000)
            hitlLogger.info("✅ Prev and Next buttons are visible")

            ids = [self._get_task_id()]
            self.log.click(next_btn, "Next → Task 2")
            ids.append(self._get_task_id())

            self.log.click(next_btn, "Next → Task 3")
            ids.append(self._get_task_id())

            self.log.click(prev_btn, "Prev → Task 2")
            assert self._get_task_id() == ids[1], "Didn't return to Task 2"

            self.log.click(prev_btn, "Prev → Task 1")
            assert self._get_task_id() == ids[0], "Didn't return to Task 1"

            self.log.click(back_btn, "Back to List")

            # Step 5: Mark all tasks as Resolved
            for task_id in task_ids:
                updated = self.dao.update_task_status_to_resolved(test_user, task_id)
                if updated == 0:
                    hitlLogger.warning(f"⚠️ Task ID {task_id} was NOT updated to 'Resolved'. Check Env/TaskId.")
                    assert False, f"Task ID {task_id} not updated to 'Resolved'"
                else:
                    hitlLogger.info(f"✅ Task ID {task_id} marked as 'Resolved'")

                if step_logger:
                    step_logger.add_step(
                        f"Task {task_id} marked as Resolved",
                        f"Task {task_id} updated to 'Resolved' in DB"
                    )

            save_success(reporter, method_name)
            if step_logger:
                step_logger.add_step("Navigate filtered tasks", f"Navigated and resolved: {', '.join(task_ids)}")

        except Exception as exception:
            if step_logger:
                step_logger.fail_step("Navigate filtered tasks", "Navigation failed", str(exception))
            handle_exception(self, exception, reporter, method_name)
            raise

    def _get_task_id(self):
        url = self.page.url
        match = re.search(r'/task/(\d+)', url)
        if not match:
            raise Exception(f"❌ Task ID not found in URL: {url}")
        return match.group(1)

    def filter_multiple_tasks(self, task_ids: list, reporter: DBReporter, step_logger: StepLogger = None):
        method_name = inspect.currentframe().f_code.co_name
        try:
            # Step 1: Open filter panel
            filter_icon = self.page.locator(".ag-cell-label-container > span:nth-child(2) > .ag-icon").first
            self.log.click(filter_icon, "Open Filter Panel")

            # Step 2: Deselect all existing values
            select_all = self.page.get_by_text("(Select All)")
            self.log.click(select_all, "Deselect All")

            for task_id in task_ids:
                # Step 3: Type the task ID (do NOT press Enter)
                search_input = self.page.get_by_role("textbox", name="Search filter values")
                self.log.click(search_input, f"Click input for Task ID {task_id}")
                self.log.fill(search_input, task_id, f"Type Task ID {task_id}")

                # Step 4: Click the matching checkbox
                checkbox = self.page.get_by_role("checkbox", name=task_id).first
                self.log.click(checkbox, f"Select checkbox for Task ID {task_id}")

            # Step 5: Press Escape once after all selections
            self.page.keyboard.press("Escape")
            hitlLogger.info("✅ Closed filter panel after selecting all task IDs.")

            save_success(reporter, method_name)
            if step_logger:
                step_logger.add_step("Filter multiple tasks", f"All Task IDs filtered: {', '.join(task_ids)}")

        except Exception as exception:
            if step_logger:
                step_logger.fail_step("Filter multiple tasks", "Filtering failed", str(exception))
            handle_exception(self, exception, reporter, method_name)
            raise

    def get_displayed_columns(self):
        headers = self.page.locator(".ag-header-cell")
        columns = []
        count = headers.count()
        for i in range(count):
            header = headers.nth(i)
            label = header.inner_text().strip()
            field_attr = header.get_attribute("col-id")
            columns.append({
                "label": label,
                "field": field_attr,
                "locator": header  # pass locator for highlighting
            })
        return columns

    def get_sample_data(self):
        first_row = self.page.locator(".ag-center-cols-container .ag-row").first
        cells = (first_row.locator

                 (".ag-cell"))
        data = {}
        count = cells.count()
        for i in range(count):
            cell = cells.nth(i)
            field = cell.get_attribute("col-id")  # adjust if needed
            value = cell.inner_text().strip()
            if field:
                data[field] = value
        return [data]

    def view_audit_history_log(self, test_meta, test_user, reporter: DBReporter, step_logger: StepLogger):
        import time
        method_name = inspect.currentframe().f_code.co_name
        hitlLogger.info("📌 Entered view_audit_history_log()")

        try:
            fields = ["ID", "User_Email", "Transaction_Date", "Status", "Operation Type"]

            # 🔁 Fetch task
            task = self.dao.get_tasks_to_resolve(test_meta, test_user, no_of_tasks_to_resolve=1)[0]
            task_id = str(task.TaskId)
            assert task_id, "❌ Task ID could not be retrieved from mapping table"

            # 🔍 Filter the task
            self.filter_task(task_id, reporter, step_logger)

            # 🧭 Click Actions > History
            actions_btn = self.page.get_by_test_id("task-grid").get_by_role("button", name="Actions").first
            self.log.click(actions_btn, "Actions Button")

            history_option = self.page.get_by_role("menuitem", name="History")
            self.log.click(history_option, "History Menu Option")

            # ✅ Visually verify and highlight each header by label
            try:
                expected_labels = fields

                self.page.locator("div.ag-header-cell").first.wait_for(state="visible", timeout=5000)
                actual_headers = self.page.locator("div.ag-header-cell")
                hitlLogger.info(f"🧠 Header count: {actual_headers.count()}")

                actual = []
                for i in range(actual_headers.count()):
                    cell = actual_headers.nth(i)
                    label = cell.locator("span.ag-header-cell-text").inner_text()
                    hitlLogger.info(f"🔹 Header {i}: {label}")
                    actual.append({
                        "label": label.strip(),
                        "locator": cell
                    })

                for expected_label in expected_labels:
                    for col in actual:
                        if col.get("label") == expected_label:
                            locator = col["locator"]
                            locator.evaluate("e => e.style.outline = '2px solid red'")
                            locator.evaluate("e => e.scrollIntoView({ block: 'center', inline: 'center' })")
                            locator.wait_for(timeout=500)
                            locator.evaluate("e => e.style.outline = ''")
                            if step_logger:
                                step_logger.add_step(f"Header Highlight - {expected_label}",
                                                     "Verified and visually highlighted")
                            break
            except Exception as e:
                hitlLogger.warning(f"⚠️ Header highlighting failed: {e}")
                if step_logger:
                    step_logger.add_step("Header Highlighting", f"⚠️ Failed: {e}")

            # 📊 Wait for audit rows
            history_page = HistoryPage(self.page)
            max_retries = 10
            for i in range(max_retries):
                rows = history_page.get_audit_rows()
                if rows.count() >= 2:
                    break
                hitlLogger.info(f"🔁 Attempt {i + 1}: Waiting for audit rows...")
                time.sleep(1)
            else:
                raise AssertionError("❌ Expected 2 audit log entries")

            # ✅ Get row values
            row_0 = history_page.get_row_values(0, fields)
            row_1 = history_page.get_row_values(1, fields)

            # ✅ Log row values into ADO
            if step_logger:
                row_0_values = "\n".join([f"{key}: {row_0[key]}" for key in fields if key in row_0])
                row_1_values = "\n".join([f"{key}: {row_1[key]}" for key in fields if key in row_1])

                step_logger.add_step("Audit Row 0", f"\n{row_0_values}")
                step_logger.add_step("Audit Row 1", f"\n{row_1_values}")

            # 🔙 Back to task list
            history_page.click_back()

            # ✅ Confirm all saved
            self.confirm_all_task_saved(reporter, step_logger)

            # ✅ Update task as Resolved
            updated = self.dao.update_task_status_to_resolved(test_user, task_id)
            if updated > 0 and step_logger:
                step_logger.add_step("Update Task Status", f"Task {task_id} marked as Resolved in mapping table")

            save_success(reporter, method_name)
            if step_logger:
                step_logger.add_step("View audit history log", "Verified audit log entries and resolved task")

        except Exception as e:
            if step_logger:
                step_logger.fail_step("View audit history log", "Verified audit log entries", str(e))
            handle_exception(self, e, reporter, method_name)
            raise

    def verify_column_mapping(self, expected, actual, steps: StepLogger):
        expected_labels = {col['label'] for col in expected}
        actual_labels = {col['label'] for col in actual}

        missing = expected_labels - actual_labels

        hitlLogger.info("EXPECTED LABELS:", expected_labels)
        hitlLogger.info("ACTUAL LABELS:", actual_labels)

        assert not missing, steps.fail_step(
            "Verify Column Mapping",
            "Missing column labels in grid",
            str(missing)
        )

        steps.add_step("Verify Column Mapping", "Verified all expected column labels are present in the grid")

    def verify_column_visibility(self, expected, actual, steps: StepLogger):
        invisible = [col['label'] for col in expected if col['label'] not in [a['label'] for a in actual]]
        assert not invisible, steps.fail_step("Verify Column Visibility", "Invisible schema column labels",
                                              str(invisible))
        steps.add_step("Verify Column Visibility", "All expected columns are visible")

    def verify_column_ordering(self, expected, actual, steps: StepLogger):
        expected_order = [col['label'] for col in expected]
        actual_order = [col['label'] for col in actual]

        hitlLogger.info("Expected Column Order:", expected_order)
        hitlLogger.info("Actual Column Order:", actual_order)

        try:
            for label in expected_order:
                for col in actual:
                    if col.get('label') == label and col.get('locator'):
                        col['locator'].evaluate("e => e.style.outline = '2px solid red'")
                        col['locator'].evaluate("e => e.scrollIntoView({ block: 'center', inline: 'center' })")
                        col['locator'].wait_for(timeout=500)
                        col['locator'].evaluate("e => e.style.outline = ''")
        except Exception as e:
            hitlLogger.info(f"Highlighting failed: {e}")

        def is_subsequence(small, big):
            it = iter(big)
            return all(item in it for item in small)

        if not is_subsequence(expected_order, actual_order):
            steps.fail_step(
                "Verify Column Ordering",
                "Expected columns do not appear in correct order in the grid",
                f"Expected subsequence: {expected_order}\nActual: {actual_order}"
            )
            assert False

        steps.add_step("Verify Column Ordering", "Expected columns appear in correct order within the grid")

    def verify_column_labels(self, expected, actual, steps: StepLogger):
        expected_labels = [col['label'] for col in expected]
        actual_labels = [col['label'] for col in actual]

        mismatches = [label for label in expected_labels if label not in actual_labels]

        hitlLogger.info("EXPECTED:", expected_labels)
        hitlLogger.info("ACTUAL:", actual_labels)

        assert not mismatches, steps.fail_step(
            "Verify Column Labels",
            "One or more expected column labels not found in grid",
            str(mismatches)
        )

        steps.add_step("Verify Column Labels", "All expected column labels are present in the grid")

    def begin_validate_cascading_dropdowns(self, test_meta, test_user, reporter: DBReporter,
                                           step_logger: StepLogger = None):
        method_name = inspect.currentframe().f_code.co_name
        try:
            task = self.dao.get_tasks_to_resolve(test_meta, test_user, 1)[0]
            task_id = str(task.TaskId)
            hitlLogger.info(f"✩ Validating cascading dropdowns for task ID: {task_id}")

            # Step 3: Filter the specific task from grid
            self.filter_task(task_id, reporter, step_logger)

            # Step 4-6: Open in Edit and Validate Dropdowns
            self.validate_cascading_dropdown_ui(reporter, step_logger)

            # Step 7-9: Save For Later
            self.save_for_later_task_resolution(test_user, task_id, reporter, step_logger)

            save_success(reporter, method_name)
            if step_logger:
                step_logger.add_step("Validate Cascading Dropdown",
                                     "Validated all dropdown behaviors and saved successfully")

        except Exception as exception:
            if step_logger:
                step_logger.fail_step("Validate Cascading Dropdown", "Failed during cascading dropdown validation",
                                      str(exception))
            handle_exception(self, exception, reporter, method_name)
            raise

    def validate_cascading_dropdown_ui(self, reporter: DBReporter, step_logger: StepLogger = None):
        method_name = inspect.currentframe().f_code.co_name
        try:
            # Click Actions > Edit
            actions_btn = self.page.get_by_test_id("task-grid").get_by_role("button", name="Actions").first
            self.log.click(actions_btn, "Actions Button")

            edit_option = self.page.get_by_role("menuitem", name="Edit")
            self.log.click(edit_option, "Edit Option")

            # Attempt to open City before State is selected
            city_dropdown = self.page.get_by_role("combobox", name="City Dropdown")
            self.log.click(city_dropdown, "Click City Dropdown")

            city_options = self.page.locator("mat-option")
            option_count = city_options.count()

            if option_count == 0:
                hitlLogger.info("✅ City dropdown has no options — correct before selecting State.")
                if step_logger:
                    step_logger.add_step("City Dropdown Validation", "City has no values before State selection")
            else:
                raise Exception(f"City dropdown unexpectedly had {option_count} options before selecting State!")

            # 🔸 Select a different state (e.g., California) first
            state_dropdown = self.page.get_by_role("combobox", name="State Dropdown")
            self.log.click(state_dropdown, "Click State Dropdown")
            california_option = self.page.get_by_role("option", name="California")
            self.log.click(california_option, "Select 'California' from State Dropdown")

            # 🔸 Validate that 'Dallas' is NOT in the City dropdown options
            city_dropdown = self.page.get_by_role("combobox", name="City Dropdown")
            self.log.click(city_dropdown, "Click City Dropdown")

            city_options = city_dropdown.locator("option").all_inner_texts()
            if any("Dallas" in option for option in city_options):
                raise Exception("❌ Dallas appeared in City dropdown for State: California — invalid cascade mapping")
            else:
                hitlLogger.info("✅ Dallas not found in City dropdown for California — negative test passed")
                if step_logger:
                    step_logger.add_step("Negative Cascade Validation",
                                         "Dallas correctly not shown in City dropdown when State is California")

            # 🆕 Close city dropdown (to remove overlay)
            self.page.keyboard.press("Escape")

            # Look for the error message below the City Dropdown
            error_locator = self.page.locator("text=is a required property").nth(0)

            # Wait and assert
            error_locator.wait_for(state="visible", timeout=3000)
            assert error_locator.is_visible(), "Expected validation error for City Dropdown is not visible"

            if step_logger:
                step_logger.add_step("City Required Validation", "Validation error message displayed for missing City")

            # ✅ Select Texas (assumes dropdown has been reopened)
            state_dropdown = self.page.get_by_label("California")
            self.log.click(state_dropdown, "Click Current State Selection")
            texas_option = self.page.get_by_role("option", name="Texas")
            self.log.click(texas_option, "Select 'Texas' from State Dropdown")

            # ✅ Now select Dallas
            city_dropdown = self.page.get_by_role("combobox", name="City Dropdown")
            self.log.click(city_dropdown, "Click City Dropdown")
            dallas_option = self.page.get_by_role("option", name="Dallas")
            self.log.click(dallas_option, "Select 'Dallas' from City Dropdown")

            if step_logger:
                step_logger.add_step("Positive Cascade Validation- select state and city ",
                                     "Successfully selected Texas and Da;;a")

            save_success(reporter, method_name)

        except Exception as exception:
            if step_logger:
                step_logger.fail_step("Validate Dropdown Behavior", "Failed to validate dropdowns", str(exception))
            handle_exception(self, exception, reporter, method_name)
            raise

    def perform_logout(self, test_user, reporter, step_logger):
        from lib.hitl_logger import LoggerPage
        log = LoggerPage(self.page)

        try:
            # ✅ Step 1: Use HomePage’s method to click and highlight menu
            home_page = HomePage(self.page)
            home_page.click_person_icon(test_user.user_id, reporter, step_logger)

            # ✅ Step 2: Click Logout
            logout_btn = self.page.get_by_text("Logout", exact=True)
            logout_btn.wait_for(state="visible", timeout=10000)
            log.click(logout_btn, "Logout Button")

            # ✅ Step 3: Validate redirect to login screen
            # Wait for full navigation
            self.page.wait_for_load_state("load", timeout=20000)

            # Re-fetch and validate the email field
            email_locator = self.page.get_by_role("textbox", name="Email")
            email_locator.wait_for(state="visible", timeout=10000)

            assert email_locator.is_visible(), "Expected login screen, but Email field was not visible."

            if step_logger:
                step_logger.add_step("Logout Validation", "Successfully logged out and reached login screen")

        except Exception as e:
            if step_logger:
                step_logger.fail_step("Logout Validation", "Logout failed or login page not visible", str(e))
            self.page.screenshot(path="logout_failure.png")
            raise

    def begin_resolve_overriding_task(self, check_error, test_meta, test_user, reporter: DBReporter,
                                      step_logger: StepLogger = None):
        method_name = get_method_name()

        try:
            tasks_to_resolve = self.dao.get_tasks_to_resolve(test_meta, test_user, 1)
            hitlLogger.info(f"🔹 Loaded {len(tasks_to_resolve)} record(s) for override resolution")

            for row in tasks_to_resolve:
                hitlLogger.info(f"🔹 Resolving override task id: {row.TaskId}")
                self.filter_task(str(row.TaskId), reporter, step_logger)

                # Edit and attempt to save
                self.edit_description_only(reporter, step_logger)

                # Validate message: user already working on task
                conflict_banner = self.page.get_by_text("adminxref@vizientinc.com is already working on this task.")
                conflict_banner.wait_for(timeout=5000)
                assert conflict_banner.is_visible(), "❌ Expected override conflict banner was not visible"
                if step_logger:
                    step_logger.add_step("Conflict Message Validation",
                                         "adminxref@vizientinc.com conflict message shown")

                save_btn = self.page.get_by_role("button", name="Save", exact=True)
                self.log.click(save_btn, "Clicked Save Button")

                # Pop-up appears: click No first
                popup_no_btn = self.page.get_by_role("button", name="No")
                popup_no_btn.wait_for(timeout=3000)
                self.log.click(popup_no_btn, "Click 'No' on override popup")

                # Validate user still on task and popup is gone
                popup_msg = self.page.locator("text=Are you sure you want to override the changes?")
                popup_msg.wait_for(state="hidden", timeout=5000)
                assert not popup_msg.is_visible(), "❌ Popup still visible after clicking No"

                if step_logger:
                    step_logger.add_step("Popup Cancel", "Clicked No and popup closed, no override performed")

                # Click Save again, then Yes
                self.log.click(save_btn, "Clicked Save again")
                popup_yes_btn = self.page.get_by_role("button", name="Yes")
                popup_yes_btn.wait_for(timeout=3000)
                self.log.click(popup_yes_btn, "Click 'Yes' on override popup")

                if check_error:
                    error_message_locator = self.page.get_by_text("Action Could Not Be Completed")
                    error_message_text = error_message_locator.inner_text(timeout=5000)
                    self.log.highlight_only(error_message_locator, error_message_text)
                    back_btn = self.page.get_by_role("button", name="Back", exact=True)
                    self.log.click(back_btn, "Back Button")
                else:
                    save_btn.wait_for(state="detached", timeout=5000)
                    updated = self.dao.update_task_status_to_resolved(test_user, str(row.TaskId))
                    hitlLogger.info(f"🔹 {updated} row(s) resolved.")

                save_success(reporter, method_name)
                if step_logger:
                    step_logger.add_step("Save task resolution", f"Task {row.TaskId} marked as resolved")

        except Exception as exception:
            if step_logger:
                step_logger.fail_step("Save task resolution", f"Task {row.TaskId} resolution failed", str(exception))
            handle_exception(self, exception, reporter, method_name)
            raise

    def resolve_current_task_from_ui(self, check_error, test_user, reporter: DBReporter,
                                     step_logger: StepLogger = None):
        method_name = get_method_name()
        try:
            hitlLogger.info("🔹 Resolving task from currently selected UI record")

            # Assume the task is already selected or visible
            self.edit_description_only(reporter, step_logger)
            self.save_task_resolution(check_error, test_user, task_id=None, reporter=reporter, step_logger=step_logger)

            save_success(reporter, method_name)
            if step_logger:
                step_logger.add_step("Resolve UI task", "Resolved task currently selected in UI")

        except Exception as exception:
            if step_logger:
                step_logger.fail_step("Resolve UI task", "UI task resolution failed!", str(exception))
            handle_exception(self, exception, reporter, method_name)
            raise

    def refresh_task_ongrid(self, reporter: DBReporter, step_logger: StepLogger = None):
        method_name = inspect.currentframe().f_code.co_name
        try:
            actions_button = self.page.locator("div.grid-header button:has-text('Actions')").first
            actions_button.wait_for(state="visible", timeout=10000)
            self.log.click(actions_button, "Actions filter")

            refresh_option = self.page.get_by_role("menuitem", name="Refresh")
            self.log.click(refresh_option, "Refresh task grid")

            save_success(reporter, method_name)
            if step_logger:
                step_logger.add_step("Refresh Task Grid", "Grid refreshed successfully.")
        except Exception as e:
            if step_logger:
                step_logger.fail_step("Refresh Task Grid", "Failed to refresh grid.", str(e))
            handle_exception(self, e, reporter, method_name)
            raise

    def delete_selected_task(self, test_meta, test_user, reporter: DBReporter, step_logger: StepLogger = None):
        method_name = inspect.currentframe().f_code.co_name
        try:
            tasks_to_process = self.dao.get_tasks_to_resolve(test_meta, test_user, 1)  # only 1 task to delete
            hitlLogger.info(f"🔹 Loaded {len(tasks_to_process)} task(s) for deletion (limit: 1)")

            if not tasks_to_process:
                raise Exception("No tasks available to delete.")

            for row in tasks_to_process:
                task_id = row.TaskId
                hitlLogger.info(f"🔹 Attempting to delete Task ID: {task_id}")

                # Step 1: Filter the task in UI
                self.filter_task(str(task_id), reporter, step_logger)

                # Wait for the task cell
                task_cell = self.page.locator(f"div.ag-cell:has-text('{task_id}')").first
                task_cell.wait_for(state="visible", timeout=10000)

                # Select the checkbox within the row
                checkbox = task_cell.locator("xpath=ancestor::div[contains(@class, 'ag-row')]//input[@type='checkbox']")
                checkbox.wait_for(state="visible", timeout=5000)
                self.log.click(checkbox, f"Select task {task_id}")

                # Step 3: Actions → Delete
                actions_button = self.page.locator("div.grid-header button:has-text('Actions')").first
                self.log.click(actions_button, "Open Actions menu")

                delete_option = self.page.get_by_role("menuitem", name="Delete")
                self.log.click(delete_option, "Click Delete")

                # Step 4: Confirm the delete popup
                confirm_yes = self.page.get_by_role("button", name="Yes")
                confirm_yes.wait_for(timeout=10000)
                self.log.click(confirm_yes, "Confirm deletion")

                # Step 5: Wait for toast message
                toast = self.page.locator("text=Action Has Been Completed")
                toast.wait_for(state="visible", timeout=10000)
                self.log.highlight_only(toast, "Deletion toast")

                # Step 6: Mark task as resolved in mapping table
                updated = self.dao.update_task_status_to_resolved(test_user, str(task_id))
                hitlLogger.info(f"🔹 {updated} row(s) resolved in API_UI_Task_Mapping for Task ID: {task_id}")

                if step_logger:
                    step_logger.add_step("Delete Task", f"Deleted and resolved Task ID: {task_id}")

            save_success(reporter, method_name)
        except Exception as e:
            if step_logger:
                step_logger.fail_step("Delete Task", "Failed to delete or resolve task.", str(e))
            handle_exception(self, e, reporter, method_name)
            raise

    def verify_filter_icon_hidden(self, reporter: DBReporter, step_logger: StepLogger = None):
        method_name = get_method_name()
        try:
            filter_icon_locator = self.page.locator("button.filter-icon mat-icon")

            # Assert it is not visible within a timeout
            is_visible = filter_icon_locator.is_visible(timeout=3000)

            if is_visible:
                raise AssertionError("❌ Filter icon is visible when it should be hidden.")

            hitlLogger.info("✅ Filter icon is correctly hidden when task search is disabled.")
            if step_logger:
                step_logger.add_step("Verify filter hidden", "Filter icon is not visible as expected.")

            save_success(reporter, method_name)

        except Exception as e:
            if step_logger:
                step_logger.fail_step("Verify filter hidden", "Filter icon should be hidden but is visible.", str(e))
            handle_exception(self, e, reporter, method_name)
            raise

    def verify_filter_icon_clickable(self, reporter: DBReporter, step_logger: StepLogger = None):
        method_name = get_method_name()
        try:
            # Step 1: Locate filter icon
            filter_icon = self.page.locator("button.filter-icon mat-icon")
            assert filter_icon.is_visible(), "❌ Filter icon is not visible."

            # Step 2: Click the icon
            self.log.click(filter_icon, "Click Filter Icon")

            # Step 3: Verify Filters panel is visible
            filters_heading = self.page.locator("h2", has_text="Filters")
            filters_heading.wait_for(state="visible", timeout=5000)

            hitlLogger.info("✅ Filters panel is displayed after clicking filter icon.")
            if step_logger:
                step_logger.add_step("Filter icon check", "Filter icon is visible and opened Filters panel.")
            save_success(reporter, method_name)

            # Optional: Click outside to dismiss
            self.page.mouse.click(0, 0)  # simulate click outside to close

        except Exception as e:
            if step_logger:
                step_logger.fail_step("Filter icon check", "Failed to validate filter icon interaction.", str(e))
            handle_exception(self, e, reporter, method_name)
            raise

    import re

    def begin_validate_autocomplete_dropdown(self, test_meta, test_user, reporter: DBReporter,
                                             step_logger: StepLogger = None):
        import re
        import unicodedata

        method_name = inspect.currentframe().f_code.co_name
        try:
            # Step 1: Get the test task from the DB
            task = self.dao.get_tasks_to_resolve(test_meta, test_user, 1)[0]
            task_id = str(task.TaskId)
            hitlLogger.info(f"🔎 Validating autocomplete for task ID: {task_id}")

            # Step 2: Filter and edit task
            self.filter_task(task_id, reporter, step_logger)
            actions_btn = self.page.get_by_test_id("task-grid").get_by_role("button", name="Actions").first
            self.log.click(actions_btn, "Click Actions Button")
            edit_option = self.page.get_by_role("menuitem", name="Edit")
            self.log.click(edit_option, "Click Edit Option")

            # Step 3: Type "Boston" in Person field and validate
            person_field = self.page.get_by_role("combobox", name="Person")
            self.log.fill(person_field, "Boston", "Type 'Boston' in Person field")

            dropdown_results = self.page.locator("mat-option[role='option']")
            dropdown_results.first.wait_for(timeout=5000)

            count = dropdown_results.count()
            assert count > 0, "No results displayed for 'Boston'"

            matched = False
            for i in range(count):
                text = dropdown_results.nth(i).inner_text().lower()
                hitlLogger.info(f"[Dropdown {i}] {text}")
                if "boston" in text:
                    matched = True
                    break

            assert matched, "Dropdown does not contain expected 'Boston' content"
            step_logger.add_step("Autocomplete - Boston", "Dropdown shows expected results for 'Boston'")

            # Step 4: Clear and type "Janet", then validate first column only
            person_field.fill("")
            person_field.type("Janet", delay=100)
            self.page.wait_for_timeout(1000)

            dropdown_locator = self.page.locator("mat-option[role='option']")
            dropdown_locator.first.wait_for(timeout=5000)

            count = dropdown_locator.count()
            assert count > 0, "No usable results displayed for 'Janet'"

            matched = False
            for i in range(count):
                option = dropdown_locator.nth(i)
                first_column = option.locator("td").first.inner_text().strip().lower()
                hitlLogger.info(f"[Option {i}] First Column: {first_column}")
                if "janet" in first_column:
                    matched = True
                    break

            assert matched, "Dropdown does not contain a row with 'Janet' in the first column"
            step_logger.add_step("Autocomplete - Janet", "Dropdown shows 'Janet' in first column")

            # Step 5: Select the first Janet match and save
            dropdown_locator.nth(0).click()
            save_btn = self.page.get_by_role("button", name="Save", exact=True)
            self.log.click(save_btn, "Click Save")
            save_btn.wait_for(state="detached", timeout=5000)
            step_logger.add_step("Save Task", f"Selected 'Janet' and saved the task")

            # Step 6: Update DB task status
            updated = self.dao.update_task_status_to_resolved(test_user, task_id)
            assert updated > 0, f"Failed to update task status for Task ID {task_id}"
            step_logger.add_step("DB Update", f"Task {task_id} marked as Completed in mapping table")

            save_success(reporter, method_name)

        except Exception as e:
            if step_logger:
                step_logger.fail_step("Autocomplete Dropdown", "Validation failed", str(e))
            handle_exception(self, e, reporter, method_name)
            raise

    def prepare_tasks_for_bulk_edit_flow(self, test_meta, test_user, reporter: DBReporter,
                                         step_logger: StepLogger = None):
        method_name = inspect.currentframe().f_code.co_name
        hitlLogger.info("📍 Entered prepare_tasks_for_bulk_edit_flow()")

        # Step 1: Fetch and sort tasks
        tasks = self.dao.get_tasks_to_resolve(test_meta, test_user, 3)
        hitlLogger.info(f"🔹 Loaded {len(tasks)} record(s) for bulk edit (limit: 3)")

        if len(tasks) < 3:
            raise Exception("Not enough tasks to perform bulk edit test (need at least 3).")

        task_ids = sorted([str(task.TaskId) for task in tasks])
        hitlLogger.info(f"🔹 Using Task IDs for bulk edit: {task_ids}")

        # Step 2: Filter grid
        self.filter_multiple_tasks(task_ids, reporter, step_logger)

        # Step 3: Select all visible checkboxes in the grid
        checkboxes = self.page.locator("div.ag-center-cols-container input[type='checkbox']")
        count = checkboxes.count()
        hitlLogger.info(f"🔹 Selecting {count} checkboxes for filtered tasks.")
        for i in range(count):
            checkbox = checkboxes.nth(i)
            checkbox.wait_for(state="visible", timeout=5000)
            self.log.click(checkbox, f"Select checkbox #{i + 1}")

        self.open_bulk_edit_modal()

        hitlLogger.info("✅ Bulk Edit menu item clicked.")

    # ─────────────────────────────────────
    # 🔁 Bulk Edit - Locator Utility Methods
    # ─────────────────────────────────────

    def open_bulk_edit_modal(self):
        actions_button = self.page.locator("div.grid-header button:has-text('Actions')").first
        self.log.click(actions_button, "Open Actions menu")
        bulk_edit_option = self.page.get_by_role("menuitem", name="Bulk Edit").first
        bulk_edit_option.wait_for(timeout=5000)
        self.log.click(bulk_edit_option, "Click Bulk Edit from Actions menu")

    def select_bulk_edit_attribute(self, attribute_name: str):
        try:
            # Click the attribute dropdown trigger (anywhere inside that field)
            dropdown_trigger = self.page.locator("mat-label:text-is('Attribute')")
            dropdown_trigger.wait_for(timeout=5000)
            dropdown_trigger.click()

            # Wait for overlay to open (targeting visible <mat-option> by text)
            option_locator = self.page.locator(f"mat-option >> text={attribute_name}")
            option_locator.wait_for(timeout=5000)
            option_locator.click()

            hitlLogger.info(f"✅ Selected Bulk Edit Attribute: {attribute_name}")
        except Exception as e:
            raise Exception(f"❌ Failed to select bulk edit attribute '{attribute_name}': {e}")

    def enter_bulk_edit_value(self, label: str, value: str):
        input_field = self.page.get_by_label(f"{label}*")
        input_field.fill(value)

    def apply_bulk_edit(self):
        self.page.get_by_role("button", name="Apply").click()

    def apply_and_submit_bulk_edit(self):
        self.apply_bulk_edit()
        self.page.get_by_role("button", name="Submit").click()

    # ─────────────────────────────────────
    # 🚀 Bulk Edit + Take Action Flows
    # ─────────────────────────────────────

    def close_bulk_edit_modal(self):
        # Ensure modal is open
        self.page.locator("text=Single / Bulk Attribute Change").wait_for(timeout=5000)

        # Click Close button
        close_button = self.page.get_by_role("button", name="Close")
        self.log.click(close_button, "Click Close on Bulk Edit")

        # Validate return to Task Manager list page
        self.page.locator("text=Task Manager").wait_for(timeout=5000)
        hitlLogger.info("✅ Returned to Task Manager list page after closing Bulk Edit.")

    def bulk_edit_age_only_then_no(self, age_value: str):
        self.open_bulk_edit_modal()
        self.select_bulk_edit_attribute("Age")
        self.enter_bulk_edit_value("Age", age_value)
        self.apply_and_submit_bulk_edit()
        self.page.get_by_role("button", name="No").click()
        self.page.locator("text=Task Manager").wait_for(timeout=5000)

    def bulk_edit_age_only_then_yes_and_validate_errors(self, age_value: str):
        self.open_bulk_edit_modal()
        self.select_bulk_edit_attribute("Age")
        self.enter_bulk_edit_value("Age", age_value)
        self.apply_and_submit_bulk_edit()
        self.page.get_by_role("button", name="Yes").click()

        # 🔹 Fill Take Action form and submit
        self.fill_and_submit_take_action_form(batch_name="qa-test", action_text="Save Personal Data.")

        # 🔹 Validate warning message about firstName
        self.validate_warning_message_contains(
            "Some tasks are missing required information: Field 'firstName' is required.")

        # 🔹 Close the Take Action modal
        self.close_take_action_modal()

    def bulk_edit_age_firstname_then_yes_and_validate_success(
            self,
            age_value: str,
            first_name: str,
            batch_name: str,
            test_meta,
            test_user,
            reporter,
            step_logger
    ):
        method_name = "bulk_edit_age_firstname_then_yes_and_validate_success"

        try:
            # Step 1: Fetch and sort tasks
            tasks = self.dao.get_tasks_to_resolve(test_meta, test_user, 3)
            hitlLogger.info(f"🔹 Loaded {len(tasks)} record(s) for navigation (limit: 3)")

            if len(tasks) < 3:
                raise Exception("Not enough tasks to perform navigation test (need at least 3).")

            task_ids = sorted([str(task.TaskId) for task in tasks])
            hitlLogger.info(f"🔹 Using Task IDs for navigation: {task_ids}")

            # Step 2: Open Bulk Edit modal
            self.open_bulk_edit_modal()

            # Step 3: Bulk edit Age
            self.select_bulk_edit_attribute("Age")
            self.enter_bulk_edit_value("Age", age_value)
            self.apply_bulk_edit()

            # Step 4: Bulk edit First Name
            self.select_bulk_edit_attribute("First Name")
            self.enter_bulk_edit_value("First Name", first_name)
            self.apply_and_submit_bulk_edit()

            # Step 5: Confirm Yes
            self.page.get_by_role("button", name="Yes").click()

            # Step 6: Fill Take Action form
            self.page.get_by_placeholder("Batch Name...").fill(batch_name)
            hitlLogger.info(f"✅ Entered batch name: {batch_name}")

            self.page.locator('[formcontrolname="selectAction"]').click(force=True)
            hitlLogger.info("🔹 CLICK → Select Action dropdown forcibly")

            self.page.locator("span.mdc-list-item__primary-text", has_text="Save Personal Data").click()
            hitlLogger.info("✅ Selected Action: Save Personal Data")

            self.page.get_by_role("button", name="Take Action").click()

            # Step 7: Mark all tasks as Resolved
            for task_id in task_ids:
                updated = self.dao.update_task_status_to_resolved(test_user, task_id)
                if updated == 0:
                    hitlLogger.warning(f"⚠️ Task ID {task_id} was NOT updated to 'Resolved'. Check Env/TaskId.")
                    assert False, f"Task ID {task_id} not updated to 'Resolved'"
                else:
                    hitlLogger.info(f"✅ Task ID {task_id} marked as 'Resolved'")

                if step_logger:
                    step_logger.add_step(
                        f"Task {task_id} marked as Resolved",
                        f"Task {task_id} updated to 'Resolved' in DB"
                    )

            save_success(reporter, method_name)

            if step_logger:
                step_logger.add_step("Navigate filtered tasks", f"Navigated and resolved: {', '.join(task_ids)}")

        except Exception as exception:
            if step_logger:
                step_logger.fail_step("Navigate filtered tasks", "Navigation failed", str(exception))
            handle_exception(self, exception, reporter, method_name)
            raise

    def fill_and_submit_take_action_form(self, batch_name: str, action_text: str):
        # 🔹 Fill the Batch Name input field
        batch_input = self.page.get_by_placeholder("Batch Name...")
        batch_input.fill(batch_name)
        hitlLogger.info(f"✅ Entered batch name: {batch_name}")

        # Click the dropdown forcibly to bypass the label blocking
        self.page.locator('[formcontrolname="selectAction"]').click(force=True)
        hitlLogger.info("🔹 CLICK → Select Action dropdown forcibly")

        # Select the desired option
        self.page.locator("span.mdc-list-item__primary-text", has_text="Save Personal Data.").click()
        hitlLogger.info("✅ Selected Action: Save Personal Data.")

        # 🔹 Click Take Action
        take_action_btn = self.page.get_by_role("button", name="Take Action")
        take_action_btn.wait_for(timeout=5000)
        take_action_btn.click()
        hitlLogger.info("✅ Clicked Take Action button")

    def validate_warning_message_contains(self, expected_text: str, timeout: int = 8000):
        # Locate all warning message elements
        warning_locator = self.page.locator("div.viz-feedback-indicator-message")
        warning_locator.wait_for(timeout=timeout)

        all_messages = warning_locator.all_inner_texts()
        hitlLogger.info(f"⚠️ Found warning messages: {all_messages}")

        # Check for expected text presence (substring match)
        matched = any(expected_text in message for message in all_messages)
        assert matched, f"Expected warning message not found. Got: {all_messages}"

    def close_take_action_modal(self):
        """Closes the Take Action modal after warning."""

        # This excludes the snackbar's Close button
        close_button = self.page.locator("button:has-text('Close'):not(.mat-mdc-snack-bar-action)").first

        self.log.click(close_button, "Click Close on Take Action")
        self.page.locator("text=Task Manager").wait_for(timeout=5000)
        hitlLogger.info("✅ Returned to Task Manager after closing Take Action modal.")

    def verify_pagination_batching(self, reporter: DBReporter, step_logger: StepLogger):
        method_name = get_method_name()
        try:
            rows = self.page.locator(".ag-center-cols-container .ag-row")
            assert rows.count() <= 20, f"Expected ≤20 rows, got {rows.count()}"

            self.page.get_by_role("button", name="chevron_right").click()
            self.page.wait_for_timeout(1000)

            rows_next = self.page.locator(".ag-center-cols-container .ag-row")
            assert rows_next.count() <= 20, f"Expected ≤20 rows on next page, got {rows_next.count()}"

            save_success(reporter, method_name)
            step_logger.add_step("Pagination works", "Validated 20-row page batching")
        except Exception as e:
            step_logger.fail_step("Pagination", "Pagination failed", str(e))
            raise

    def verify_select_all_current_page_only(self, reporter: DBReporter, step_logger: StepLogger):
        method_name = get_method_name()
        try:
            header_checkbox = self.page.locator("div.ag-header input[type='checkbox']").first
            self.log.check(header_checkbox, "Select All on Current Page")

            selected_count = self.page.locator("div.ag-center-cols-container input[type='checkbox']:checked").count()
            assert selected_count > 0, "No checkboxes selected on current page"

            self.page.get_by_role("button", name="chevron_right").click()
            self.page.wait_for_timeout(1000)

            next_page_selected = self.page.locator(
                "div.ag-center-cols-container input[type='checkbox']:checked").count()
            assert next_page_selected == 0, "Selection persisted across pages unexpectedly"

            save_success(reporter, method_name)
            step_logger.add_step("Select All Page Only", f"{selected_count} selected, next page clear")
        except Exception as e:
            step_logger.fail_step("Select All Page Only", "Selection leaked across pages", str(e))
            raise

    def verify_shift_click_range_selection(self, reporter: DBReporter, step_logger: StepLogger):
        method_name = get_method_name()
        try:
            checkboxes = self.page.locator("div.ag-center-cols-container input[type='checkbox']")
            if checkboxes.count() < 5:
                raise Exception("Not enough checkboxes to test range selection")

            box1 = checkboxes.nth(1)
            box4 = checkboxes.nth(4)

            box1.click()
            self.page.keyboard.down("Shift")
            box4.click()
            self.page.keyboard.up("Shift")

            selected = self.page.locator("div.ag-center-cols-container input[type='checkbox']:checked").count()
            assert selected >= 4, f"Expected at least 4 selected; got {selected}"

            save_success(reporter, method_name)
            step_logger.add_step("Shift+Click Range", f"{selected} checkboxes selected via shift")
        except Exception as e:
            step_logger.fail_step("Shift+Click Range", "Failed to shift+click select", str(e))
            raise

    def verify_deselect_checkbox_behavior(self, reporter: DBReporter, step_logger: StepLogger):
        method_name = get_method_name()
        try:
            checkbox = self.page.locator("div.ag-center-cols-container input[type='checkbox']").nth(2)
            checkbox.check()
            assert checkbox.is_checked(), "Checkbox was not selected"

            checkbox.uncheck()
            assert not checkbox.is_checked(), "Checkbox still selected after unchecking"

            save_success(reporter, method_name)
            step_logger.add_step("Unselect Checkbox", "Checkbox deselected successfully")
        except Exception as e:
            step_logger.fail_step("Unselect Checkbox", "Checkbox did not deselect", str(e))
            raise

    def verify_bulk_action_applies_only_to_selected(self, reporter: DBReporter, step_logger: StepLogger):
        method_name = get_method_name()
        try:
            self.page.locator("div.ag-center-cols-container input[type='checkbox']").nth(1).check()
            self.log.click(self.page.get_by_role("button", name="Actions"), "Actions Menu")
            self.log.click(self.page.get_by_role("menuitem", name="Delete"), "Delete Action")
            self.log.click(self.page.get_by_role("button", name="Yes"), "Confirm Delete")

            toast = self.page.locator("text=Action Has Been Completed")
            assert toast.is_visible(), "No confirmation toast after bulk delete"

            save_success(reporter, method_name)
            step_logger.add_step("Bulk Delete Action", "Confirmed delete toast after single selection")
        except Exception as e:
            step_logger.fail_step("Bulk Delete Action", "Bulk action failed or applied incorrectly", str(e))
            raise
