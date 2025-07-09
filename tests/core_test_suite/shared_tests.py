import allure

from dao.test_execution_db_updater_dao import DBReporter
from pages.core_pages.home_page import HomePage
from pages.core_pages.login_page import LoginPage
from utils.ado.ado_step_logger import StepLogger


@allure.step("Login and Validate the test user")
def login_to_dashboard(page, test_user, reporter: DBReporter, step_logger: StepLogger = None):
    login = LoginPage(page, reporter)
    login.navigate(test_user.test_url, reporter, step_logger)
    login.login(test_user.user_id, test_user.password, reporter, step_logger)
    login.validate_login(test_user.user_id, reporter, step_logger)
    allure.attach(test_user.user_id, name="Logged-in User")


@allure.step("Navigate to HITL dashboard")
def navigate_to_hitl_dashboard(page, test_user, reporter: DBReporter, step_logger: StepLogger = None):
    home_page = HomePage(page)
    home_page.click_person_icon(test_user.user_id, reporter, step_logger)
    home_page.click_navigation_menu(reporter, step_logger)
    home_page.click_task_manager(reporter, step_logger)
    home_page.validate_hitl_dashboard(test_user.user_id, reporter, step_logger)


@allure.step("Select domain card")
def select_domain_card(page, meta, reporter: DBReporter, step_logger: StepLogger = None):
    home_page = HomePage(page)
    home_page.select_domain_card(meta.get("domain"), meta.get("entity"), reporter, step_logger)
