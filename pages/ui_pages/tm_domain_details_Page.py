import logging

from playwright.sync_api import Page

from dao.test_execution_db_updater_dao import DBReporter
from lib.hitl_logger import LoggerPage
from utils.ado.ado_step_logger import StepLogger
from utils.generic.get_readable_method_name import get_method_name
from utils.generic.post_test_actions_handler import save_success, handle_exception

hitlLogger = logging.getLogger("HitlLogger")


class DomainDetailsPage:
    def __init__(self, page: Page):
        self.page = page
        self.log = LoggerPage(page)

    def create_domain(self, domain, reporter: DBReporter, step_logger: StepLogger = None):
        method_name = get_method_name()
        try:
            domain_link = self.page.get_by_role("button", name="Domain")
            self.log.click(domain_link, "Domain Button")

            domain_name_edit_box = self.page.get_by_role("textbox", name="Domain Name")
            self.log.fill(domain_name_edit_box, domain, "Domain Name")

            display_name_edit_box = self.page.get_by_role("textbox", name="Display Name")
            self.log.fill(display_name_edit_box, domain, "Display Name")

            description_edit_box = self.page.get_by_role("textbox", name="Description")
            self.log.fill(description_edit_box, "This is automation created domain", "Description")

            contact_email_edit_box = self.page.get_by_role("textbox", name="Contact Email")
            self.log.fill(contact_email_edit_box, "andy.sharma@vizientinc.com", "Contact Email")

            save_button = self.page.get_by_role("button", name="Submit")
            self.log.click(save_button, "Save Button")

            save_success(reporter, method_name)
            if step_logger:
                step_logger.add_step("Create domain", "Domain and metadata should be saved")

        except Exception as exception:
            if step_logger:
                step_logger.fail_step("Create domain", "Domain and metadata should be saved", str(exception))
            handle_exception(self, exception, reporter, method_name)
            raise

    def confirm_domain_disabled(self, reporter: DBReporter, step_logger: StepLogger = None):
        method_name = get_method_name()
        try:
            is_active_locator = self.page.get_by_label("Is Active")
            self.log.click(is_active_locator, "Is Active")

            is_active_no = self.page.get_by_role("option", name="No")
            self.log.click(is_active_no, "Is Active No")

            submit_button_locator = self.page.get_by_role("button", name="Submit")
            self.log.click(submit_button_locator, "Submit Button")

            save_success(reporter, method_name)
            if step_logger:
                step_logger.add_step("Remove domain", "Domain should be marked inactive")

        except Exception as exception:
            if step_logger:
                step_logger.fail_step("Remove domain", "Domain should be marked inactive", str(exception))
            handle_exception(self, exception, reporter, method_name)
            raise
