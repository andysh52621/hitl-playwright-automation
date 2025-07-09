import pytest

from tests.core_test_suite.create_adhoc_product_tasks import create_adhoc_product_tasks
from utils.ado.ado_decorators import ado_api_testcase
from utils.generic.get_readable_method_name import get_method_name
from utils.generic.post_test_actions_handler import save_success, handle_exception


@pytest.mark.api
@pytest.mark.regression
@ado_api_testcase
def test_create_adhoc_product_tasks(test_user, reporter, ado_runner, request):
    test_meta = request.node.meta
    step_logger = request.node.steps
    method_name = get_method_name()

    try:
        create_adhoc_product_tasks(test_user, test_meta)

        save_success(reporter, method_name)
        if step_logger:
            step_logger.add_step(method_name, "Ad-hoc product task created successfully")

    except Exception as exception:
        if step_logger:
            step_logger.fail_step(method_name, "Failed to create ad-hoc product task", str(exception))
        handle_exception(None, exception, reporter, method_name)
        raise
