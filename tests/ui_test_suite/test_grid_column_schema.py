
import pytest
import allure

from pages.ui_pages.tm_list_page import TaskManagerListPage
from pages.ui_pages.tm_schema_page import SchemaPage
from tests.core_test_suite.shared_tests import login_to_dashboard, navigate_to_hitl_dashboard, select_domain_card
from utils.ado.ado_decorators import ado_ui_testcase
from utils.ado.ado_step_logger import StepLogger
from dao.test_execution_db_updater_dao import DBReporter


@pytest.mark.regression
@pytest.mark.ui
@ado_ui_testcase
def test_grid_column_schema(page, test_user, reporter, ado_runner, request):
    meta = request.node.meta
    steps = request.node.steps
    test_data = meta.get("test_data", {})

    # Step 1: Login and navigate to dashboard
    login_to_dashboard(page, test_user, reporter, steps)
    navigate_to_hitl_dashboard(page, test_user, reporter, steps)
    select_domain_card(page, meta, reporter, steps)

    try:
        # Step 2: Edit and submit Grid Schema
        set_grid_schema(page, test_data, reporter, steps)

        # Step 3: Validate grid schema
        validate_grid_schema(page, test_data, steps)

    finally:
        # Step 4: Restore original grid schema
        restore_grid_schema(page, test_data, reporter, steps)


@allure.step("Set Grid Schema")
def set_grid_schema(page, test_data, reporter: DBReporter, step_logger: StepLogger):
    schema_page = SchemaPage(page)
    grid_schema = test_data.get("test", {}).get("grid_schema", {})
    schema_page.edit_grid_schema(grid_schema, reporter, step_logger)


@allure.step("Validate Grid Schema")
def validate_grid_schema(page, test_data, step_logger: StepLogger):
    task_manager_page = TaskManagerListPage(page)
    actual_columns = task_manager_page.get_displayed_columns()
    expected_columns = test_data.get("test", {}).get("grid_schema", {}).get("columns", [])

    task_manager_page.verify_column_mapping(expected_columns, actual_columns, step_logger)
    task_manager_page.verify_column_visibility(expected_columns, actual_columns, step_logger)
    task_manager_page.verify_column_ordering(expected_columns, actual_columns, step_logger)
    task_manager_page.verify_column_labels(expected_columns, actual_columns, step_logger)
    # task_manager_page.verify_data_integrity(expected_columns, task_manager_page.get_sample_data(), step_logger)


@allure.step("Restore Original Grid Schema")
def restore_grid_schema(page, test_data, reporter: DBReporter, step_logger: StepLogger):
    schema_page = SchemaPage(page)
    restore_schema = test_data.get("test", {}).get("restore_grid_schema", {})
    if restore_schema:
        schema_page.edit_grid_schema(restore_schema, reporter, step_logger)
