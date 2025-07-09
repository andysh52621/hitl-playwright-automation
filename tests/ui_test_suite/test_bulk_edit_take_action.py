import allure
import pytest

from dao.test_execution_db_updater_dao import DBReporter
from pages.ui_pages.tm_list_page import TaskManagerListPage
from tests.core_test_suite.create_adhoc_product_tasks import create_adhoc_product_tasks
from tests.core_test_suite.shared_tests import login_to_dashboard, navigate_to_hitl_dashboard, select_domain_card
from utils.ado.ado_decorators import ado_ui_testcase
from utils.ado.ado_step_logger import StepLogger


@pytest.mark.regression
@pytest.mark.ui
@ado_ui_testcase
def test_product_task_bulk_edit_take_action(page, test_user, reporter, ado_runner, request):
    test_meta = request.node.meta
    steps = request.node.steps

    # 🔧 Create 3 tasks to enable bulk edit flow
    for _ in range(3):
        create_adhoc_product_tasks(test_user, test_meta)

    # Login and Setup
    login_to_dashboard(page, test_user, reporter, steps)
    navigate_to_hitl_dashboard(page, test_user, reporter, steps)
    select_domain_card(page, test_meta, reporter, steps)

    # Prepare tasks and open Bulk Edit
    prepare_tasks_for_bulk_edit_flow(page, test_meta, test_user, reporter, steps)

    # Run the full Bulk Edit & Take Action scenarios
    run_bulk_edit_and_take_action_flow(page, test_meta,test_user, reporter, steps)


@allure.step("Prepare tasks for Bulk Edit")
def prepare_tasks_for_bulk_edit_flow(page, test_meta, test_user, reporter: DBReporter, step_logger: StepLogger):
    task_page = TaskManagerListPage(page)
    task_page.prepare_tasks_for_bulk_edit_flow(test_meta, test_user, reporter, step_logger)


@allure.step("Run Bulk Edit and Take Action Flow")
def run_bulk_edit_and_take_action_flow(page, test_meta, test_user, reporter, step_logger: StepLogger):
    task_page = TaskManagerListPage(page)

    # Step 1: Close the bulk edit modal if it's open
    task_page.close_bulk_edit_modal()

    # Step 2: Apply bulk edit for Age only, then cancel
    task_page.bulk_edit_age_only_then_no(age_value="25")

    # Step 3: Apply bulk edit for Age only, then continue and validate error
    task_page.bulk_edit_age_only_then_yes_and_validate_errors(age_value="30")

    # Step 4: Apply bulk edit for Age and First Name, proceed with Take Action
    task_page.bulk_edit_age_firstname_then_yes_and_validate_success( "30","John", "qaAutoTest",test_meta, test_user, reporter, step_logger )

    # Step 5: Confirm all tasks saved
    task_page.confirm_all_task_saved(reporter, step_logger)

