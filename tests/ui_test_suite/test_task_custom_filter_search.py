import pytest

from pages.ui_pages.tm_custom_task_search_page import CustomTaskSearchPage
from pages.ui_pages.tm_schema_page import SchemaPage
from tests.core_test_suite.shared_tests import login_to_dashboard, navigate_to_hitl_dashboard, select_domain_card
from utils.ado.ado_decorators import ado_ui_testcase


@pytest.mark.regression
@pytest.mark.ui
@ado_ui_testcase
def test_task_filter_search(page, test_user, reporter, ado_runner, request):
    test_meta = request.node.meta
    steps = request.node.steps
    test_data = test_meta.get("test_data", {})

    # Step 1: Navigate to Task Manager and domain context
    login_to_dashboard(page, test_user, reporter, steps)
    navigate_to_hitl_dashboard(page, test_user, reporter, steps)
    select_domain_card(page, test_meta, reporter, steps)

    # Step 2: Use empty task schema and validate behavior
    empty_schema = test_data.get("test", {}).get("task_search_schema", {}).get("empty_task_search_schema")
    SchemaPage(page).edit_search_schema(empty_schema, reporter, steps)
    CustomTaskSearchPage(page).validate_custom_task_search_with_empty_schema(reporter, steps)

    # Step 3: Use valid schema and test full search flow
    valid_schema = test_data.get("test", {}).get("task_search_schema", {}).get("task_search_schema")
    SchemaPage(page).edit_search_schema(valid_schema, reporter, steps)
    CustomTaskSearchPage(page).validate_custom_task_search_with_correct_schema(reporter, steps)
