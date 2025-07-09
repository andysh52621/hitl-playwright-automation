from datetime import datetime

import allure
import pytest

from dao.test_execution_db_updater_dao import DBReporter
from pages.core_pages.home_page import HomePage
from pages.ui_pages.tm_domain_details_Page import DomainDetailsPage
from pages.ui_pages.tm_entity_details_Page import EntityDetailsPage
from tests.core_test_suite.shared_tests import login_to_dashboard, navigate_to_hitl_dashboard
from utils.ado.ado_decorators import ado_ui_testcase
from utils.ado.ado_step_logger import StepLogger


@pytest.mark.regression
@pytest.mark.smoke
@pytest.mark.ui
@ado_ui_testcase
def test_create_domain_entity(page, test_user, reporter, ado_runner, request):
    meta = request.node.meta
    steps = request.node.steps
    unique_domain_name = meta.get("domain") + datetime.now().strftime("%m%d%H%M%S%f")[:12]

    login_to_dashboard(page, test_user, reporter, steps)
    navigate_to_hitl_dashboard(page, test_user, reporter, steps)
    create_domain(page, unique_domain_name, reporter, steps)
    create_entity(page, unique_domain_name, meta.get("entity"), reporter, steps)

    confirm_entity_disable(page, unique_domain_name, meta.get("entity"), reporter, steps)
    confirm_domain_disable(page, unique_domain_name, reporter, steps)


@allure.step("Create Domain")
def create_domain(page, unique_domain_name, reporter: DBReporter, step_logger: StepLogger):
    domain_details_page = DomainDetailsPage(page)
    domain_details_page.create_domain(unique_domain_name, reporter, step_logger)


@allure.step("Create Entity")
def create_entity(page, domain, entity, reporter: DBReporter, step_logger: StepLogger):
    entity_details_page = EntityDetailsPage(page)
    entity_details_page.select_domain_add_entity(domain, reporter, step_logger)
    entity_details_page.create_entity(entity, reporter, step_logger)


@allure.step("Remove or disable the test Entity")
def confirm_entity_disable(page, domain, entity, reporter: DBReporter, step_logger: StepLogger):
    entity_details_page = EntityDetailsPage(page)
    entity_details_page.disable_entity(reporter, step_logger)


@allure.step("Remove or disable the test Domain")
def confirm_domain_disable(page, unique_domain_name, reporter: DBReporter, step_logger: StepLogger):
    home_page = HomePage(page)
    domain_details_page = DomainDetailsPage(page)
    home_page.click_task_manager_home(reporter, step_logger)
    home_page.edit_domain(unique_domain_name, reporter, step_logger)
    domain_details_page.confirm_domain_disabled(reporter, step_logger)
