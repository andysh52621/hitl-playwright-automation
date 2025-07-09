import allure
import pytest

from pages.ui_pages.tm_list_page import TaskManagerListPage
from pages.ui_pages.tm_schema_page import SchemaPage
from tests.core_test_suite.create_adhoc_product_tasks import create_adhoc_product_tasks
from tests.core_test_suite.shared_tests import login_to_dashboard, navigate_to_hitl_dashboard, select_domain_card
from utils.ado.ado_decorators import ado_ui_testcase
from utils.ado.ado_step_logger import StepLogger


@pytest.mark.regression
@pytest.mark.ui
@ado_ui_testcase
def test_form_action_schema(page, test_user, reporter, ado_runner, request):
    test_meta = request.node.meta
    steps = request.node.steps
    test_data = test_meta.get("test_data", {})

    # Step 1: Log in and select domain
    login_to_dashboard(page, test_user, reporter, steps)
    navigate_to_hitl_dashboard(page, test_user, reporter, steps)
    select_domain_card(page, test_meta, reporter, steps)

    # Step 2: Run schema update scenarios
    # Scenario B: Invalid test endpoint in action schema
    create_adhoc_product_tasks(test_user, test_meta)
    validate_schema_with_invalid_action_endpoint(page, test_meta, test_user, test_data, reporter, steps)

    # Scenario C: Non-existing action name in form schema
    create_adhoc_product_tasks(test_user, test_meta)
    validate_schema_with_non_existing_action_name(page, test_meta, test_user, test_data, reporter, steps)

    # Scenario A: Valid form + valid action (reset back)
    create_adhoc_product_tasks(test_user, test_meta)
    validate_schema_with_valid_action_endpoint(page, test_meta, test_user, test_data, reporter, steps)


@allure.step("Validate form & action schema with valid test endpoint")
def validate_schema_with_valid_action_endpoint(page, test_meta, test_user, test_data, reporter, steps: StepLogger):
    action_schema = test_data["test"]["action_schema"]["action_schema_with_valid_testEndpoint"]
    form_schema = test_data["test"]["form_schema"]["form_schema_with_valid_testEndpoint"]

    SchemaPage(page).edit_action_schema(action_schema, reporter, steps)
    SchemaPage(page).edit_form_schema(form_schema, reporter, steps)
    begin_resolve_tasks(page, check_error=False, test_meta=test_meta, test_user=test_user, reporter=reporter,
                        steps=steps)


@allure.step("Validate form schema with invalid action endpoint")
def validate_schema_with_invalid_action_endpoint(page, test_meta, test_user, test_data, reporter, steps: StepLogger):
    action_schema = test_data["test"]["action_schema"]["action_schema_with_invalid_testEndpoint"]
    form_schema = test_data["test"]["form_schema"]["form_schema_with_valid_testEndpoint"]

    SchemaPage(page).edit_action_schema(action_schema, reporter, steps)
    SchemaPage(page).edit_form_schema(form_schema, reporter, steps)
    begin_resolve_tasks(page, check_error=True, test_meta=test_meta, test_user=test_user, reporter=reporter,
                        steps=steps)


@allure.step("Validate form schema with non-existing action name")
def validate_schema_with_non_existing_action_name(page, test_meta, test_user, test_data, reporter, steps: StepLogger):
    action_schema = test_data["test"]["action_schema"]["action_schema_with_valid_testEndpoint"]
    form_schema = test_data["test"]["form_schema"]["form_schema_with_non_existing_endpoint"]

    SchemaPage(page).edit_action_schema(action_schema, reporter, steps)
    SchemaPage(page).edit_form_schema(form_schema, reporter, steps)
    begin_resolve_tasks(page, check_error=True, test_meta=test_meta, test_user=test_user, reporter=reporter,
                        steps=steps)


@allure.step("Trigger task and resolve schema updates")
def begin_resolve_tasks(page, check_error: bool, test_meta, test_user, reporter, steps: StepLogger):
    TaskManagerListPage(page).begin_resolves_tasks(check_error, test_meta, test_user, reporter, steps)
