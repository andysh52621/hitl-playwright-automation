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
def test_product_task_resolve(page, test_user, reporter, ado_runner, request):
    test_meta = request.node.meta
    steps = request.node.steps

    # create product task to save for later
    create_adhoc_product_tasks(test_user, test_meta)

    test_user.domain = test_meta.get("domain")
    test_user.entity = test_meta.get("entity")

    # access the task manager portal
    login_to_dashboard(page, test_user, reporter, steps)
    navigate_to_hitl_dashboard(page, test_user, reporter, steps)
    select_domain_card(page, test_meta, reporter, steps)

    # resolve the hitl tasks
    resolve_hitl_task(page, test_meta, test_user, reporter, steps)

    test_user.domain = "QAProduct"
    test_user.entity = "QAEntityApprover"
    test_meta["entity"] = "QAEntityApprover"

    # access the task manager portal
    # login_to_dashboard(page, test_user, reporter, steps)
    navigate_to_hitl_dashboard(page, test_user, reporter, steps)
    select_domain_card(page, test_meta, reporter, steps)

    # resolve the hitl tasks
    resolve_hitl_task_for_approver(page, test_user, reporter, steps)


@allure.step("Edit & Resolve tasks from the domain task table")
def resolve_hitl_task(page, test_meta, test_user, reporter: DBReporter, step_logger: StepLogger):
    resolve_tasks_page = TaskManagerListPage(page)
    resolve_tasks_page.begin_resolves_tasks(False, test_meta, test_user, reporter, step_logger)
    resolve_tasks_page.confirm_all_task_saved(reporter, step_logger)


@allure.step("Edit & Resolve tasks from the domain task table")
def resolve_hitl_task_for_approver(page, test_user, reporter: DBReporter, step_logger: StepLogger):
    resolve_tasks_page = TaskManagerListPage(page)
    resolve_tasks_page.resolve_current_task_from_ui(False, test_user, reporter, step_logger)
    resolve_tasks_page.confirm_all_task_saved(reporter, step_logger)
