import os
from datetime import datetime

import allure


def capture_screenshot(self, base_filename: str) -> str:
    """Capture screenshot using self.page and return full file path."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{base_filename}_{timestamp}.png"
    screenshots_dir = os.path.join(os.getcwd(), "screenshots")
    os.makedirs(screenshots_dir, exist_ok=True)
    screenshot_path = os.path.join(screenshots_dir, filename)
    self.page.screenshot(path=screenshot_path, full_page=True)
    return screenshot_path


def screenshot_exception_handler(self, method_name: str):
    """Calls capture_screenshot from a page-holding object and attaches to Allure."""
    screenshot_path = capture_screenshot(self, f"{method_name}_failure")
    allure.attach.file(
        screenshot_path,
        name=f"{method_name} Screenshot",
        attachment_type=allure.attachment_type.PNG
    )
    print(f"✅ Playwright captured {method_name}_failure.")
    print(f"📍 Stored at: {screenshot_path}")
