import logging

import allure

from utils.generic.screenshot_handler import handle_exception_with_screenshot

hitlLogger = logging.getLogger("HitlLogger")


def save_success(reporter, method_name):
    hitlLogger.info(f"💾 {method_name} test step successful PASSED")
    reporter.add_step(f"{method_name} test step successful", "PASSED")


def handle_exception(page, exception, reporter, method_name):
    reporter.add_step(method_name + " Test step failed", "FAILED", str(exception))
    if hasattr(reporter, 'end_test_execution'):
        reporter.end_test_execution("FAILED", str(exception))
    else:
        reporter.fail_step(method_name, "Test step failed", str(exception))
    allure.attach(str(exception), name="Exception", attachment_type=allure.attachment_type.TEXT)
    if page:
        handle_exception_with_screenshot(page, str(exception), method_name, method_name + " failed.")
