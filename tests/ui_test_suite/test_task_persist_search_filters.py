import allure
import pytest

from dao.test_execution_db_updater_dao import DBReporter
from pages.ui_pages.tm_custom_task_search_page import CustomTaskSearchPage
from pages.ui_pages.tm_list_page import TaskManagerListPage
from pages.ui_pages.tm_schema_page import SchemaPage
from tests.core_test_suite.create_adhoc_product_tasks import create_adhoc_product_tasks
from tests.core_test_suite.shared_tests import login_to_dashboard, navigate_to_hitl_dashboard, select_domain_card
from utils.ado.ado_decorators import ado_ui_testcase
from utils.ado.ado_step_logger import StepLogger


@pytest.mark.regression
@ado_ui_testcase
def test_task_filter_search(page, test_user, reporter, ado_runner, request):
    test_meta = request.node.meta
    steps = request.node.steps
    test_data = test_meta.get("test_data", {})

    product_key_value = test_data.get("test", {}).get("product_key")
    product_base_key_value = test_data.get("test", {}).get("product_base_key")

    # Step 1: Create task programmatically
    create_adhoc_product_tasks(test_user, test_meta)

    # Step 2: Navigate to Task Manager and domain context
    login_to_dashboard(page, test_user, reporter, steps)
    navigate_to_hitl_dashboard(page, test_user, reporter, steps)
    select_domain_card(page, test_meta, reporter, steps)

    # Step 3: Fill out the search schema
    valid_schema = test_data.get("test", {}).get("task_search_schema", {}).get("task_search_schema")
    SchemaPage(page).edit_search_schema(valid_schema, reporter, steps)
    CustomTaskSearchPage(page).set_custom_task_search_to_product_task(reporter, steps, product_key_value, product_base_key_value)

    # Step 4: Edit an entry and save for later
    save_task_for_later(page, test_user, reporter, steps)
    # Check to make sure search parameters are still present
    CustomTaskSearchPage(page).validate_custom_task_search_persist(reporter, steps, product_key_value, product_base_key_value)

    # Step 5: Revert search schema
    empty_schema = test_data.get("test", {}).get("task_search_schema", {}).get("empty_task_search_schema")
    SchemaPage(page).edit_search_schema(empty_schema, reporter, steps)
    CustomTaskSearchPage(page).validate_custom_task_search_with_empty_schema(reporter, steps)

@allure.step("Save product task for later")
def save_task_for_later(page, test_user, reporter: DBReporter, step_logger: StepLogger):
    task_page = TaskManagerListPage(page)
    test_meta = {"domain": "QAProduct", "entity": "Product"}  # Get these values from the YAML config
    task_page.begin_saveforlater_tasks(test_meta, test_user, step_logger)
    # task_page.confirm_all_task_saved(reporter, step_logger)