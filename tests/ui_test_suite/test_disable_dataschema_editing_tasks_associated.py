from datetime import datetime

import allure
import pytest

from dao.test_execution_db_updater_dao import DBReporter
from pages.core_pages.home_page import HomePage
from pages.ui_pages.tm_domain_details_Page import DomainDetailsPage
from pages.ui_pages.tm_entity_details_Page import EntityDetailsPage
from pages.ui_pages.tm_list_page import TaskManagerListPage
from pages.ui_pages.tm_schema_page import SchemaPage
from tests.core_test_suite.create_adhoc_product_tasks import create_adhoc_product_tasks
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
    test_data = meta.get("test_data", {})

    login_to_dashboard(page, test_user, reporter, steps)
    navigate_to_hitl_dashboard(page, test_user, reporter, steps)
    create_domain(page, unique_domain_name, reporter, steps)
    create_entity(page, unique_domain_name, meta.get("entity"), reporter, steps)

    # Edit and submit data Schema
    set_data_schema(page, test_data, reporter, steps)

    # Step: Create task via API
    meta["domain"] = unique_domain_name
    create_adhoc_product_tasks(test_user, meta)

    # Step 3: Refresh task grid to make UI reflect the new task
    refresh_task_grid(page, reporter, steps)

    # Try to Edit and submit data Schema after the task is associated to it
    set_data_schema(page, test_data, reporter, steps)

    # Step 5: Delete the task via UI
    delete_task(meta, test_user, page, reporter, steps)


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

@allure.step("Set Grid Schema")
def set_data_schema(page, test_data, reporter: DBReporter, step_logger: StepLogger):
    schema_page = SchemaPage(page)
    data_schema = test_data.get("test", {}).get("data_schema", {})
    schema_page.edit_data_schema(data_schema, reporter, step_logger)

@allure.step("Refresh Task Grid")
def refresh_task_grid(page, reporter: DBReporter, step_logger: StepLogger):
    task_page = TaskManagerListPage(page)
    task_page.refresh_task_ongrid(reporter, step_logger)

@allure.step("Delete Selected Task")
def delete_task(test_meta, test_user, page, reporter: DBReporter, step_logger: StepLogger):
    task_page = TaskManagerListPage(page)
    task_page.delete_selected_task(test_meta, test_user, reporter, step_logger)
    task_page.confirm_all_task_saved(reporter, step_logger)
