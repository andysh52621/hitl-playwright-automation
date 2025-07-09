import allure

from conftest import hitlLogger
from utils.generic.screenshots_capture import capture_screenshot


def handle_exception_with_screenshot(page_object, exception, method_name: str, context: str = ""):
    """Captures a screenshot and attaches it to Allure with a formatted name."""
    error_message = f"Exception in {method_name}: {str(exception)} "
    screenshot_path = capture_screenshot(page_object, f"{method_name}_failure")
    allure.attach.file(
        screenshot_path,
        name=f"{method_name} Screenshot",
        attachment_type=allure.attachment_type.PNG
    )
    hitlLogger.info(f"✅ Playwright captured {method_name}_failure. {context}")
    hitlLogger.info(f"📍 Stored at: {screenshot_path}")
    hitlLogger.info(error_message)
    hitlLogger.info(f"✅ Playwright captured {method_name}_failure. {context}")
    hitlLogger.info(f"📍 Stored at: {screenshot_path}")
    hitlLogger.info(str(error_message))
