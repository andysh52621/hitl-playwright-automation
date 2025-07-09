from datetime import datetime

import allure
import pytest

from dao.test_execution_db_updater_dao import DBReporter
from pages.core_pages.home_page import HomePage
from pages.ui_pages.tm_domain_details_Page import DomainDetailsPage
from pages.ui_pages.tm_entity_details_Page import EntityDetailsPage
from pages.ui_pages.tm_list_page import TaskManagerListPage
from tests.core_test_suite.shared_tests import login_to_dashboard, navigate_to_hitl_dashboard, select_domain_card
from utils.ado.ado_decorators import ado_ui_testcase
from utils.ado.ado_step_logger import StepLogger


@pytest.mark.regression
@pytest.mark.smoke
@pytest.mark.ui
@ado_ui_testcase
def test_create_domain_entity(page, test_user, reporter, ado_runner, request):
    meta = request.node.meta
    steps = request.node.steps

    login_to_dashboard(page, test_user, reporter, steps)
    navigate_to_hitl_dashboard(page, test_user, reporter, steps)
    select_domain_card(page, meta, reporter, steps)

    # ✅ Disable Task Search
    set_task_search_toggle(page, reporter, steps, enable=False)

    # ✅ Validate that filter icon is NOT visible
    validate_filter_icon_not_visible(page, reporter, steps)

    # ✅ Enable Task Search
    set_task_search_toggle(page, reporter, steps, enable=True)

    # Validate filter icon presence and interaction
    validate_filter_icon_is_visible(page, reporter, steps)


@allure.step("Toggle Task Search for Entity")
def set_task_search_toggle(page, reporter: DBReporter, step_logger: StepLogger, enable: bool = True):
    entity_details_page = EntityDetailsPage(page)
    entity_details_page.toggle_task_search(enable_search=enable, reporter=reporter, step_logger=step_logger)


@allure.step("Validate filter icon is hidden when Task Search is disabled")
def validate_filter_icon_not_visible(page, reporter: DBReporter, step_logger: StepLogger):
    task_page = TaskManagerListPage(page)
    task_page.verify_filter_icon_hidden(reporter, step_logger)

@allure.step("Validate filter icon is visible and interactive when Task Search is enabled")
def validate_filter_icon_is_visible(page, reporter: DBReporter, step_logger: StepLogger):
    task_page = TaskManagerListPage(page)
    task_page.verify_filter_icon_clickable(reporter, step_logger)



