import allure
import pytest
import requests

from dao.test_execution_db_updater_dao import DBReporter
from utils.ado.ado_decorators import ado_api_testcase
from utils.ado.ado_step_logger import StepLogger


@pytest.mark.api
@pytest.mark.regression
@ado_api_testcase
def test_host_ado_runner_app(test_user, reporter, ado_runner, request):
    meta = request.node.meta
    steps = request.node.steps

    verify_ado_runner_app(reporter, steps)


@allure.step("Run a sample request to ado runner app")
def verify_ado_runner_app(reporter: DBReporter, step_logger: StepLogger):
    # Health check endpoint URL
    health_url = "https://fastapi-hitl-task-manager-eastus2-dev-01.vzn-eastus2-intase-sandbox-ase-02.appserviceenvironment.net/health"
    
    try:
        # Make GET request to health endpoint
        response = requests.get(health_url, headers={'accept': 'application/json'}, timeout=30)
        
        # Log response details
        reporter.add_step(
            "Health Check Response",
            "INFO",
            f"Status Code: {response.status_code}\nResponse: {response.text}"
        )
        
        # Verify response
        assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"
        
        response_data = response.json()
        assert response_data.get('status') == 'healthy', f"Expected status 'healthy', but got {response_data.get('status')}"
        
        reporter.add_step("Health Check", "PASSED", "Application health check successful")
        
    except requests.RequestException as e:
        reporter.add_step("Health Check", "FAILED", f"Failed to connect to health endpoint: {str(e)}")
        raise
    except AssertionError as e:
        reporter.add_step("Health Check", "FAILED", f"Health check assertion failed: {str(e)}")
        raise
    except Exception as e:
        reporter.add_step("Health Check", "FAILED", f"Unexpected error during health check: {str(e)}")
        raise
