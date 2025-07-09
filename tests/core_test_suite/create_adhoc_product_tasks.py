import os
from datetime import datetime

import requests
from sqlalchemy.orm import Session

from db_engine.test_automation_engine import get_test_db_engine
from db_models.api_test_db_models import APIServiceConfig, APIUITaskMapping
from pages.core_pages.home_page import hitlLogger
from utils.api.api_adhoc_product_payload_builder import build_product_payload
from utils.api.api_token_manager import get_access_token


def create_adhoc_product_tasks(test_user, test_meta):
    try:
        engine = get_test_db_engine()
        with Session(engine) as session:
            # Fetch service config from DB
            config = session.query(APIServiceConfig).filter(
                APIServiceConfig.service_env == test_user.test_env
            ).first()

        # hitlLogger.info(f"API service config: {config.__dict__}")

        if not config:
            raise ValueError(f"No APIServiceConfig found for env: {test_user.test_env}")

        # 🔐 Access Token
        token = get_access_token(test_user.test_env)

        # 🛠️ Headers
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "RequestId": "1",
            "SubscriptionKey": config.primary_subscription_key
        }

        # 📦 Payload
        payload = build_product_payload(test_meta)
        # print(payload)

        # 🌐 Endpoint
        url = f"https://{config.apim_base_url_server}{config.apim_base_url_endpoint}"

        hitlLogger.info(f"Task record is sent to : {url}")

        # 📡 Call API
        response = requests.post(url=url, json=payload, headers=headers, timeout=30)

        if response.status_code in (200, 201):
            hitlLogger.info(f"✅ Response code: {response.status_code}")
            hitlLogger.info(f"Response content: {response.text}")
            
            try:
                data = response.json()
            except Exception as e:
                hitlLogger.error(f"Failed to parse response as JSON: {e}")
                data = None

            if not data:
                hitlLogger.error("Response data is None or empty")
                raise ValueError("API response data is None or empty")

            task_id = data.get("data", {}).get("id")
            transaction_id = data.get("data", {}).get("jsonData", {}).get("transactionId")
            product_key = data.get("data", {}).get("jsonData", {}).get("ProductKey")
            domain = data.get("data", {}).get("jsonData", {}).get("eventDomain")
            entity = data.get("data", {}).get("jsonData", {}).get("eventType")

            if task_id and product_key:
                hitlLogger.info(f"✅ Successfully received Task ID: {task_id}, ProductKey: {product_key}")
                # hitlLogger.info("Task Record sent to : " + url)

                mapping = APIUITaskMapping(
                    task_id=task_id,
                    transaction_id=transaction_id,
                    product_key=product_key,
                    status="Submitted",
                    datetime=datetime.now(),
                    env=test_user.test_env,
                    is_az_pipeline=os.environ.get("IS_PIPELINE"),
                    domain=domain,
                    entity=entity,
                    request_type="adhoc",
                )
                session.add(mapping)
                session.commit()
                hitlLogger.info(f"📝 Inserted into API_UI_Task_Mapping for Task ID: {task_id}")
                return task_id
            else:
                hitlLogger.warning("❌ Missing Task ID or ProductKey in response")
                return None
        else:
            hitlLogger.warning(f"❌ Unexpected status code: {response.status_code}")
    except Exception as e:
        hitlLogger.info(str(e))
        raise e
