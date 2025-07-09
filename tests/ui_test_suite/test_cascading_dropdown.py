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
def test_cascading_dropdown_behavior(page, test_user, reporter, ado_runner, request):
    test_meta = request.node.meta
    steps = request.node.steps

    # Step 1: Create task via API
    create_adhoc_product_tasks(test_user, test_meta)

    # Step 2: Login and access UI
    login_to_dashboard(page, test_user, reporter, steps)
    navigate_to_hitl_dashboard(page, test_user, reporter, steps)
    select_domain_card(page, test_meta, reporter, steps)

    # Step 3: Perform dropdown test
    validate_cascading_dropdown_task(page, test_meta, test_user, reporter, steps)


@allure.step("Validate and save cascading dropdown task")
def validate_cascading_dropdown_task(page, test_meta, test_user, reporter: DBReporter, step_logger: StepLogger):
    task_page = TaskManagerListPage(page)
    task_page.begin_validate_cascading_dropdowns(test_meta, test_user, reporter, step_logger)
    task_page.confirm_all_task_saved(reporter, step_logger)
