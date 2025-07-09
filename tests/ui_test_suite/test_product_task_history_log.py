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
def test_product_task_audit_history_tracking(page, test_user, reporter, ado_runner, request):
    test_meta = request.node.meta
    steps = request.node.steps

    # Step 1: Create task via API
    create_adhoc_product_tasks(test_user, test_meta)

    # Step 2: Login and navigate to domain
    login_to_dashboard(page, test_user, reporter, steps)
    navigate_to_hitl_dashboard(page, test_user, reporter, steps)
    select_domain_card(page, test_meta, reporter, steps)

    # Step 3: Save task for later
    save_task_for_later(page, test_meta, test_user, reporter, steps)

    # Step 4: Re-filter and open history
    validate_audit_history(page, test_meta, test_user, reporter, steps)


@allure.step("Save product task for later")
def save_task_for_later(page, test_meta, test_user, reporter: DBReporter, step_logger: StepLogger):
    task_page = TaskManagerListPage(page)
    task_page.begin_saveforlater_tasks(test_meta, test_user, reporter, step_logger)
    # task_page.confirm_all_task_saved(reporter, step_logger)


@allure.step("Validate audit history entries for task")
def validate_audit_history(page, test_meta, test_user, reporter: DBReporter, step_logger: StepLogger):
    task_page = TaskManagerListPage(page)
    task_page.view_audit_history_log(test_meta, test_user, reporter, step_logger)
