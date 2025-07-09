import allure
import pytest

from dao.test_execution_db_updater_dao import DBReporter
from pages.ui_pages.tm_entity_details_Page import EntityDetailsPage
from pages.ui_pages.tm_list_page import TaskManagerListPage
from tests.core_test_suite.create_adhoc_product_tasks import create_adhoc_product_tasks
from tests.core_test_suite.shared_tests import login_to_dashboard, navigate_to_hitl_dashboard, select_domain_card
from utils.ado.ado_decorators import ado_ui_testcase
from utils.ado.ado_step_logger import StepLogger


@pytest.mark.regression
@pytest.mark.ui
@ado_ui_testcase
def test_product_task_prev_next_navigation(page, test_user, reporter, ado_runner, request):
    test_meta = request.node.meta
    steps = request.node.steps

    # 🔧 Create 3 tasks to enable navigation
    for _ in range(3):
        create_adhoc_product_tasks(test_user, test_meta)

    # Login and Setup
    login_to_dashboard(page, test_user, reporter, steps)
    navigate_to_hitl_dashboard(page, test_user, reporter, steps)
    select_domain_card(page, test_meta, reporter, steps)

    # Set Navigation Flag to True before test
    set_navigation_flag(page, test_meta, flag_value=True, reporter=reporter, step_logger=steps)

    # Perform Prev/Next navigation validation
    run_navigation_task_flow(page, test_meta, test_user, reporter, steps)

    # Reset Navigation Flag after test
    set_navigation_flag(page, test_meta, flag_value=False, reporter=reporter, step_logger=steps)


@allure.step("Set Navigation Flag")
def set_navigation_flag(page, meta, flag_value: bool, reporter: DBReporter, step_logger: StepLogger):
    entity_page = EntityDetailsPage(page)
    entity_page.set_navigation_flag(meta, flag_value, reporter, step_logger)


@allure.step("Navigate through task records using Prev and Next")
def run_navigation_task_flow(page, test_meta, test_user, reporter: DBReporter, step_logger: StepLogger):
    task_page = TaskManagerListPage(page)
    task_page.navigate_tasks_using_prev_next(test_meta, test_user, reporter, step_logger)
