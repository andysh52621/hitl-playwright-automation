from playwright.sync_api import Playwright


def pytest_playwright_config(playwright: Playwright):
    return {
        "use": {
            "browser_name": "chromium",  # Options: "chromium", "firefox", "webkit"
            "headless": False,  # Set to True for headless execution
            "slow_mo": 500,  # Slow down execution for debugging
            "baseURL": "https://www.tst.0013.edge.vizientinc.com/",  # Base URL for ui_test_suite
            "screenshot": "only-on-failure",  # Capture screenshots on failure
            "trace": "on-first-retry"  # Collect traces for debugging
        },
        "timeout": 60000,  # Set global timeout for actions (ms)
        "retries": 3,  # Retry failing ui_test_suite
        "workers": 12  # Parallel execution
    }
