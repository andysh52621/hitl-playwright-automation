import logging
import os
import time

import allure
import pytest
import requests

from utils.ado.ado_decorators import ado_api_testcase
from utils.api.payload.build_service_bus_payload import build_service_bus_payload
from utils.api.token_manager.get_sb_sas_token import generate_sas_token
from utils.generic.get_readable_method_name import get_method_name
from utils.generic.post_test_actions_handler import save_success, handle_exception

hitlLogger = logging.getLogger("HitlLogger")


@pytest.mark.api
@pytest.mark.regression
@ado_api_testcase
def test_post_message_to_service_bus(test_user, reporter, ado_runner, request):
    step_logger = request.node.steps
    meta = request.node.meta
    method_name = get_method_name()

    try:
        # === Setup ===
        namespace = "vzn-eastus2-hitl-task-manager-test-sbus-01"
        queue_name = "taskqueue"
        full_uri = f"https://{namespace}.servicebus.windows.net/{queue_name}"
        key_name = "RootManageSharedAccessKey"
        key_value = os.environ.get("ServiceBusSharedAccessKey")
        endpoint = f"{full_uri}/messages"

        # === Tokens ===
        sas_token = generate_sas_token(full_uri, key_name, key_value)
        invalid_token = "InvalidTokenString"

        # === Positive Test ===
        with allure.step("✅ Positive Test: Send valid message to Azure Service Bus"):
            headers = {"Authorization": sas_token, "Content-Type": "application/json"}
            response = requests.post(endpoint, headers=headers, json=build_service_bus_payload(0, meta))
            hitlLogger.info(f"Positive: {response.status_code} - received.")
            assert response.status_code == 201
            step_logger.add_step("Positive Message Send", "Valid payload delivered successfully to Service Bus")
            hitlLogger.info("Positive Message Send: Valid payload delivered successfully to Service Bus")

        # === Negative Test: Invalid SAS Token ===
        with allure.step("❌ Negative Test: Send with invalid SAS token"):
            headers_invalid = {"Authorization": invalid_token, "Content-Type": "application/json"}
            response = requests.post(endpoint, headers=headers_invalid, json=build_service_bus_payload(1, meta))
            hitlLogger.info(f"Invalid Token: {response.status_code} received.")
            assert response.status_code in (401, 403)
            step_logger.add_step("Invalid Token Handling", f"Rejected with expected error code: {response.status_code}")
            hitlLogger.info(f"Invalid Token Handling: Rejected with expected error code: {response.status_code}")

        # === Negative Test: Malformed Payload ===
        with allure.step("❌ Negative Test: Send malformed payload"):
            bad_payload = {"corrupted": "data"}
            headers = {"Authorization": sas_token, "Content-Type": "application/json"}
            response = requests.post(endpoint, headers=headers, json=bad_payload)
            hitlLogger.info(f"Malformed Payload: {response.status_code} received.")
            assert response.status_code == 201, "Service Bus accepted malformed payload as expected"
            step_logger.add_step("Invalid Payload Rejection",
                                 "Malformed payload accepted by SB transport (as expected)")
            hitlLogger.info("Invalid Payload Rejection: Malformed payload accepted by SB transport (as expected)")

        # === Performance Test: Send 100 messages within limits ===
        with allure.step("📈 Throughput Test: Send 100 tasks and measure avg time"):
            headers = {"Authorization": sas_token, "Content-Type": "application/json"}
            start = time.time()
            for i in range(100):
                response = requests.post(endpoint, headers=headers, json=build_service_bus_payload(i, meta))
                assert response.status_code == 201, f"Failed at index {i}: {response.status_code}"
            total_time = time.time() - start
            avg_time = total_time / 100
            hitlLogger.info(f"⏱️ Total time: {total_time:.2f}s, Avg: {avg_time:.2f}s per task")
            assert avg_time <= 3, f"Throughput degraded: {avg_time:.2f}s per task"
            step_logger.add_step("Throughput Verification", f"100 messages sent avg: {avg_time:.2f}s/task")
            hitlLogger.info(f"Throughput Verification: 100 messages sent avg: {avg_time:.2f}s/task")

        save_success(reporter, method_name)

    except Exception as ex:
        hitlLogger.error(f"❌ Exception in {method_name}: {ex}")
        step_logger.fail_step(method_name, "Failure in Azure Service Bus test flow", str(ex))
        handle_exception(None, ex, reporter, method_name)
        raise
