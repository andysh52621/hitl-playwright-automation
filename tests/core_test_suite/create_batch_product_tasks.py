import os
from datetime import datetime
from http import HTTPStatus

import requests
from sqlalchemy.orm import Session

from db_engine.test_automation_engine import get_test_db_engine
from db_models.api_test_db_models import APIServiceConfig, APIUITaskMapping
from pages.core_pages.home_page import hitlLogger
from utils.api.api_token_manager import get_access_token


def create_batch_product_tasks(test_user, tasks_count, payload):
    try:
        engine = get_test_db_engine()
        with Session(engine) as session:
            # 🧱 Fetch environment-specific service config for batch requests
            service_config = session.query(APIServiceConfig).filter(
                APIServiceConfig.service_env == test_user.test_env,
                APIServiceConfig.request_type == "batch"
            ).first()

            if not service_config:
                raise ValueError(f"No APIServiceConfig found for env: {test_user.test_env}")

            token = get_access_token(test_user.test_env)

            # Scenario: 1 (Send payload with invalid credentials to API Endpoint : validate 401 response)
            # ================================================================================================

            invalid_headers = get_headers(token, service_config.primary_subscription_key + "invalid")

            url = f"https://{service_config.apim_base_url_server}{service_config.apim_base_url_endpoint}"

            hitlLogger.info(f"📤 Sending Invalid Credentials to: {url}")
            response = requests.post(url=url, json=payload, headers=invalid_headers, timeout=30)

            json_data = response.json()
            status_code = response.status_code
            hitlLogger.info(f"📥 Received status code: {status_code} - {HTTPStatus(status_code).phrase}")

            assert status_code == 401, f"Expected status code 401, received {status_code}"
            error_message = json_data.get("errors", {})

            # Scenario: 2 (Send empty payload to API Endpoint : validate 400 response)
            # ================================================================================================

            valid_headers = get_headers(token, service_config.primary_subscription_key)

            url = f"https://{service_config.apim_base_url_server}{service_config.apim_base_url_endpoint}"

            hitlLogger.info(f"📤 Sending Empty payload request to: {url}")
            response = requests.post(url=url, json=None, headers=valid_headers, timeout=30)

            json_data = response.json()
            status_code = response.status_code
            hitlLogger.info(f"📥 Received status code: {status_code} - {HTTPStatus(status_code).phrase}")

            assert status_code == 400, f"Expected status code 400, received {status_code} Bad request !"
            error_message = json_data.get("errors", {})

            # Scenario 3 Send correct payload to API Endpoint : validate 200 response
            # ============================================================================

            valid_headers = get_headers(token, service_config.primary_subscription_key)
            # 🌐 API Endpoint
            url = f"https://{service_config.apim_base_url_server}{service_config.apim_base_url_endpoint}"

            hitlLogger.info(f"📤 Sending full batch task request to: {url}")
            response = requests.post(url=url, json=payload, headers=valid_headers, timeout=30)

            json_data = response.json()
            status_code = response.status_code
            hitlLogger.info(f"📥 Received status code: {status_code} - {HTTPStatus(status_code).phrase}")

            assert status_code == 200, f"Expected status code 200, received {status_code}"

            if status_code == 200:
                message = json_data.get("data", []).get("jsonData", []).get("message")
                transaction_id = payload.get("transactionId")
                domain = payload.get("eventDomain")
                entity = payload.get("eventType")

                hitlLogger.info(f"✅ {message}")
                mapping = APIUITaskMapping(
                    task_id=0,
                    transaction_id=transaction_id,
                    product_key=0,
                    status="Submitted",
                    datetime=datetime.now(),
                    env=test_user.test_env,
                    is_az_pipeline=os.environ.get("IS_PIPELINE"),
                    domain=domain,
                    entity=entity,
                    request_type="batch",
                    batch_records=tasks_count,
                )
                session.add(mapping)
                hitlLogger.info(f"📝 Bulk Insert API mapping inserted for Transaction ID: {transaction_id}")
                hitlLogger.info(f"📝 Bulk Inserted {tasks_count} products.")
                session.commit()

            else:
                hitlLogger.warning(f"❌ Unexpected status: {status_code}")
                hitlLogger.warning(f"Response: {json_data}")

    except Exception as e:
        hitlLogger.exception("❌ Exception occurred during batch task creation")
        raise e

    return transaction_id


def get_headers(token, primary_subscription_key):
    # 🛠️ Headers
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "RequestId": "batch-001",
        "SubscriptionKey": primary_subscription_key
    }
    return headers
