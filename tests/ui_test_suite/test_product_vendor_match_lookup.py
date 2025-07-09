import pytest

from pages.ui_pages.product_vendor_lookup_page import ProductVendorLookupPage
from pages.ui_pages.tm_schema_page import SchemaPage
from tests.core_test_suite.create_adhoc_product_tasks import create_adhoc_product_tasks
from tests.core_test_suite.shared_tests import login_to_dashboard, navigate_to_hitl_dashboard, select_domain_card
from utils.ado.ado_decorators import ado_ui_testcase


@pytest.mark.regression
@pytest.mark.ui
@ado_ui_testcase
def test_product_vendor_lookup_match(page, test_user, reporter, ado_runner, request):
    test_meta = request.node.meta
    steps = request.node.steps
    test_data = test_meta.get("test_data", {})

    # Step 1: Create test task
    create_adhoc_product_tasks(test_user, test_meta)

    # Step 2: Login and UI navigation
    login_to_dashboard(page, test_user, reporter, steps)
    navigate_to_hitl_dashboard(page, test_user, reporter, steps)
    select_domain_card(page, test_meta, reporter, steps)

    # Step 3: Verify behavior with empty search schema
    empty_schema = test_data.get("test", {}).get("search_schema", {}).get("empty_product_search_schema")
    SchemaPage(page).edit_search_schema(empty_schema, reporter, steps)

    vendor_page = ProductVendorLookupPage(page)
    vendor_page.get_filter_task(test_meta, test_user, reporter, steps)
    vendor_page.validate_missing_search_schema(reporter, steps)

    # Step 4: Verify vendor modal with valid schema
    valid_schema = test_data.get("test", {}).get("search_schema", {}).get("product_vendor_search_schema")
    SchemaPage(page).edit_search_schema(valid_schema, reporter, steps)
    vendor_page.validate_search_modal_behavior(reporter, steps)
