from playwright.sync_api import Page

from dao.test_execution_db_updater_dao import DBReporter
from lib.hitl_logger import LoggerPage
from utils.ado.ado_step_logger import StepLogger
from utils.generic.get_readable_method_name import get_method_name
from utils.generic.post_test_actions_handler import save_success, handle_exception


class LoginPage:

    def __init__(self, page: Page, reporter: DBReporter):
        method_name = get_method_name()
        try:
            self.page = page
            self.log = LoggerPage(page)

            # Maximize browser window for more space
            self.page.evaluate("""
                () => {
                    window.moveTo(0, 0);
                    window.resizeTo(screen.availWidth, screen.availHeight);
                }
            """)

            save_success(reporter, method_name)
        except Exception as exception:
            handle_exception(self, exception, reporter, method_name)
            raise

    def navigate(self, url: str, reporter: DBReporter, step_logger: StepLogger = None):
        method_name = get_method_name()
        try:
            self.log.log("navigate", f"URL: {url}")
            self.page.goto(url)
            save_success(reporter, method_name)
            if step_logger:
                step_logger.add_step("Navigate to login URL", f"Navigated to {url}")
        except Exception as exception:
            if step_logger:
                step_logger.fail_step("Navigate to login URL", f"Navigated to {url}", str(exception))
            handle_exception(self, exception, reporter, method_name)
            raise

    def login(self, username, password, reporter: DBReporter, step_logger: StepLogger = None):
        method_name = get_method_name()
        try:
            self.log.log("login", f"Attempting login for user: {username}")

            email_locator = self.page.get_by_role("textbox", name="Email")
            self.log.fill(email_locator, username, "Email Field")

            next_button_locator = self.page.get_by_role("button", name="Next")
            self.log.click(next_button_locator, "Next Button")

            password_locator = self.page.get_by_role("textbox", name="Password")
            self.log.fill(password_locator, password, "Password Field")

            sign_in_button_locator = self.page.get_by_role("button", name="Sign in")
            self.log.click(sign_in_button_locator, "Sign In Button")

            save_success(reporter, method_name)
            if step_logger:
                step_logger.add_step("Enter credentials and login", "User submitted login form")
        except Exception as exception:
            if step_logger:
                step_logger.fail_step("Enter credentials and login", "User submitted login form", str(exception))
            handle_exception(self, exception, reporter, method_name)
            raise

    def validate_login(self, username, reporter: DBReporter, step_logger: StepLogger = None):
        method_name = get_method_name()
        try:
            welcome_locator = self.page.get_by_text("Welcome to Provider Copilot")
            self.log.wait_for_visible(welcome_locator, "Welcome Message")

            assert self.page.is_visible("text=Welcome to Provider Copilot"), \
                "Login may have failed - dashboard not visible"

            self.log.log("validate_login", f"Login successful for user: {username}")
            save_success(reporter, method_name)
            if step_logger:
                step_logger.add_step("Validate login", "Dashboard is visible")
        except Exception as exception:
            if step_logger:
                step_logger.fail_step("Validate login", "Dashboard is visible", str(exception))
            handle_exception(self, exception, reporter, method_name)
            raise
