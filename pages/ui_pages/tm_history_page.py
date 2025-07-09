# pages/ui_pages/history_page.py

from playwright.sync_api import Page

class HistoryPage:
    def __init__(self, page: Page):
        self.page = page

    def get_audit_rows(self):
        return self.page.locator("div.ag-center-cols-container div.ag-row")

    def get_row_values(self, row_index: int, fields: list):
        row = self.get_audit_rows().nth(row_index)
        values = {}
        for field in fields:
            cell = row.locator(f'div.ag-cell[col-id="{field}"]')
            values[field] = cell.inner_text()
        return values

    def click_back(self):
        self.page.get_by_role("button", name="Back").click()
