# tests/base_test_case.py

from playwright.sync_api import Page

from ado.ado_test_runner import ADOTestRunner
from dao.test_execution_db_updater_dao import DBReporter
from domain_models.test_user_model import UserConfig
from tests.core_test_suite.shared_tests import (
    login_to_dashboard,
    navigate_to_hitl_dashboard,
    select_domain_card
)


class BaseTestCase:
    page: Page
    test_user: UserConfig
    reporter: DBReporter
    ado_runner: ADOTestRunner
    request: object
    meta: dict
    steps: object
    test_data: dict

    def init(self, request, page, test_user, reporter, ado_runner):
        self.page = page
        self.test_user = test_user
        self.reporter = reporter
        self.ado_runner = ado_runner
        self.request = request
        self.meta = request.node.meta
        self.steps = request.node.steps
        self.test_data = self.meta.get("test_data", {})

    def setup(self):
        """Common UI test setup: login, navigate, and select domain."""
        login_to_dashboard(self.page, self.test_user, self.reporter, self.steps)
        navigate_to_hitl_dashboard(self.page, self.test_user, self.reporter, self.steps)
        select_domain_card(self.page, self.meta, self.reporter, self.steps)
