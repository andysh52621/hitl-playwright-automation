import allure
import pytest
from dao.test_execution_db_updater_dao import DBReporter
from pages.ui_pages.tm_list_page import TaskManagerListPage
from tests.api_test_suite.test_api_product_create_adhoc_tasks import test_create_adhoc_product_tasks
from tests.core_test_suite.shared_tests import (
    login_to_dashboard,
    navigate_to_hitl_dashboard,
    select_domain_card
)
from utils.ado.ado_decorators import ado_ui_testcase
from utils.ado.ado_step_logger import StepLogger

@pytest.mark.regression
@ado_ui_testcase
def test_pagination_and_bulk_selection(page, test_user, reporter, ado_runner, request):
    meta = request.node.meta
    steps = request.node.steps
    test_create_adhoc_product_tasks(test_user, reporter, ado_runner, request)
    login_to_dashboard(page, test_user, reporter, steps)
    navigate_to_hitl_dashboard(page, test_user, reporter, steps)
    select_domain_card(page, meta, reporter, steps)
    validate_pagination_and_bulk_selection(page, meta, test_user, reporter, steps)

@allure.step("Validate pagination and select/unselect all functionality")
def validate_pagination_and_bulk_selection(page, meta, test_user, reporter: DBReporter, step_logger: StepLogger):
    task_page = TaskManagerListPage(page)
    # Assume DAO has inserted at least 40 tasks for pagination test
    task_page.refresh_task_ongrid(reporter, step_logger)
    task_page.verify_pagination_batching(reporter, step_logger)
    task_page.verify_select_all_current_page_only(reporter, step_logger)
    task_page.verify_selection_persistence_across_pages(reporter, step_logger)
    task_page.verify_shift_click_range_selection(reporter, step_logger)
    task_page.verify_deselect_checkbox_behavior(reporter, step_logger)
    task_page.verify_bulk_action_applies_only_to_selected(reporter, step_logger)
