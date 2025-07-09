import allure
import pytest

from dao.test_execution_db_updater_dao import DBReporter
from pages.ui_pages.tm_list_page import TaskManagerListPage
from tests.core_test_suite.create_adhoc_product_tasks import create_adhoc_product_tasks
from tests.core_test_suite.shared_tests import (
    login_to_dashboard,
    navigate_to_hitl_dashboard,
    select_domain_card
)
from utils.ado.ado_decorators import ado_ui_testcase
from utils.ado.ado_step_logger import StepLogger


@pytest.mark.regression
@pytest.mark.ui
@ado_ui_testcase
def test_product_task_save_for_later(page, test_user, reporter, ado_runner, request):
    test_meta = request.node.meta
    step_logger = request.node.steps

    # Step 1: Create task via API
    create_adhoc_product_tasks(test_user, test_meta)

    test_user.domain = test_meta.get("domain")
    test_user.entity = test_meta.get("entity")

    # Step 2: Login and access UI for the first user
    login_and_open_task_manager(page, test_user, test_meta, reporter, step_logger)

    # Step 3: Perform Save for Later action
    save_task_for_later(page, test_meta, test_user, reporter, step_logger)

    # Step 4: Logout and validate
    perform_logout_and_validate(page, test_user, reporter, step_logger)

    # Step 5: Login and access UI for the second user
    test_user.user_id = "userxref@vizientinc.com"
    test_user.password = "#Demo2022"
    login_and_open_task_manager(page, test_user, test_meta, reporter, step_logger)

    # Step 6: Resolve the HITL task with override confirmation
    resolve_hitl_overriding_task(page, test_meta, test_user, reporter, step_logger)


@allure.step("Login and navigate to Task Manager domain/entity")
def login_and_open_task_manager(page, test_user, test_meta, reporter, step_logger):
    login_to_dashboard(page, test_user, reporter, step_logger)
    navigate_to_hitl_dashboard(page, test_user, reporter, step_logger)
    select_domain_card(page, test_meta, reporter, step_logger)


@allure.step("Save product task for later")
def save_task_for_later(page, test_meta, test_user, reporter: DBReporter, step_logger: StepLogger):
    task_page = TaskManagerListPage(page)
    task_page.begin_saveforlater_tasks(test_meta, test_user, reporter, step_logger)
    task_page.confirm_all_task_saved(reporter, step_logger)


@allure.step("Logout and validate successful logout")
def perform_logout_and_validate(page, test_user, reporter: DBReporter, step_logger: StepLogger):
    task_page = TaskManagerListPage(page)
    task_page.perform_logout(test_user, reporter, step_logger)


@allure.step("Validate and resolve overriding task")
def resolve_hitl_overriding_task(page, test_meta, test_user, reporter: DBReporter, step_logger: StepLogger):
    resolve_tasks_page = TaskManagerListPage(page)
    resolve_tasks_page.begin_resolve_overriding_task(False, test_meta, test_user, reporter, step_logger)
    resolve_tasks_page.confirm_all_task_saved(reporter, step_logger)
