import logging
from datetime import datetime
from typing import Optional

import pytest
import requests
from sqlalchemy.orm import Session

from db_engine.test_automation_engine import get_test_db_engine
from db_models.api_test_db_models import APIServiceConfig
from utils.ado.ado_decorators import ado_api_testcase
from utils.api.payload.api_build_domain_payload import build_domain_payload
from utils.api.payload.api_build_entity_payload import build_entity_payload
from utils.api.token_manager.api_basic_token_manager import get_basic_access_token
from utils.generic.get_readable_method_name import get_method_name
from utils.generic.post_test_actions_handler import save_success, handle_exception

hitlLogger = logging.getLogger("HitlLogger")


@pytest.mark.api
@pytest.mark.regression
@ado_api_testcase
def test_api_create_disable_domain_entity(test_user, reporter, ado_runner, request):
    test_meta = request.node.meta
    step_logger = request.node.steps
    method_name = get_method_name()

    try:
        # Generate unique domain name once for the entire test
        unique_domain_name = "API" + test_meta.get("domain") + datetime.now().strftime("%m%d%H%M%S%f")

        create_domain(test_user, test_meta, unique_domain_name)
        create_entity(test_user, test_meta, unique_domain_name)
        disable_entity(test_user, test_meta, unique_domain_name)
        disable_domain(test_user, test_meta, unique_domain_name)

        save_success(reporter, method_name)
        if step_logger:
            step_logger.add_step(method_name, "Domain and entity create/disable operations completed successfully")

    except Exception as exception:
        if step_logger:
            step_logger.fail_step(method_name, "Failed to complete domain/entity operations", str(exception))
        handle_exception(None, exception, reporter, method_name)
        raise


def create_domain(test_user, test_meta, unique_domain_name):
    method_name = get_method_name()
    service_env = test_user.test_env

    hitlLogger.info(f"✅ Starting: {method_name}")
    try:
        engine = get_test_db_engine()
        with Session(engine) as session:
            # Get config for the matching environment
            config: Optional[APIServiceConfig] = (
                session.query(APIServiceConfig)
                .filter(APIServiceConfig.service_env == service_env)
                .filter(APIServiceConfig.request_type == "adhoc")
                .filter(APIServiceConfig.service_desc == "createDomain")
                .first()
            )

            if not config:
                raise ValueError(f"No service config found for env: {service_env}")

        hitlLogger.info(f"✅ Building payload for {method_name}")
        payload = build_domain_payload(unique_domain_name, True)

        # 🔐 Access Token
        token = get_basic_access_token(service_env, "createDomain", "adhoc")

        # 🛠️ Headers
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        # 🌐 Endpoint
        url = f"https://{config.server_name}{config.service_endpoint_path}"

        hitlLogger.info(f"Create domain request is sent to : {url}")

        # 📡 Call API
        response = requests.post(url=url, json=payload, headers=headers, timeout=30)

        if response.status_code in (200, 201):
            hitlLogger.info(f"✅ Response code: {response.status_code}")

            # Handle empty or invalid JSON responses
            try:
                data = response.json() if response.text.strip() else {}
            except ValueError as json_error:
                hitlLogger.warning(f"⚠️ Invalid JSON response: {json_error}")
                data = {}

            if data and "data" in data:
                domain_id = data.get("data", {}).get("id")
                if domain_id:
                    hitlLogger.info(f"✅ Domain created with ID: {domain_id}")
                else:
                    hitlLogger.info("✅ Domain created successfully (no ID returned)")
            else:
                hitlLogger.info("✅ Domain created successfully (response structure differs)")
        else:
            raise Exception(f"Create domain failed with response code: {response.status_code}")

    except Exception as ex:
        hitlLogger.error(f"✅ Exception in {method_name}: {ex}")
        raise


def create_entity(test_user, test_meta, unique_domain_name):
    method_name = get_method_name()
    service_env = test_user.test_env

    hitlLogger.info(f"✅ Starting: {method_name}")
    try:
        engine = get_test_db_engine()
        with Session(engine) as session:
            # Get config for the matching environment
            config: Optional[APIServiceConfig] = (
                session.query(APIServiceConfig)
                .filter(APIServiceConfig.service_env == service_env)
                .filter(APIServiceConfig.request_type == "adhoc")
                .filter(APIServiceConfig.service_desc == "createEntity")
                .first()
            )

            if not config:
                raise ValueError(f"No service config found for env: {service_env}")

        hitlLogger.info(f"✅ Building payload for {method_name}")
        payload = build_entity_payload(unique_domain_name, True)

        # 🔐 Access Token
        token = get_basic_access_token(service_env, "createEntity", "adhoc")

        # 🛠️ Headers
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        # 🌐 Endpoint
        url = f"https://{config.server_name}{config.service_endpoint_path}"

        hitlLogger.info(f"Create Entity request is sent to : {url}")

        # 📡 Call API
        response = requests.post(url=url, json=payload, headers=headers, timeout=30)

        if response.status_code in (200, 201):
            hitlLogger.info(f"✅ Response code: {response.status_code}")

            # Handle empty or invalid JSON responses
            try:
                data = response.json() if response.text.strip() else {}
            except ValueError as json_error:
                hitlLogger.warning(f"⚠️ Invalid JSON response: {json_error}")
                data = {}

            if data and "data" in data and data.get("data") is not None:
                entity_id = data.get("data", {}).get("id")
                if entity_id:
                    hitlLogger.info(f"✅ Entity created with ID: {entity_id}")
                else:
                    hitlLogger.info("✅ Entity created successfully (no ID returned)")
            else:
                hitlLogger.info("✅ Entity created successfully (response structure differs)")
        else:
            raise Exception(f"Create entity failed with response code: {response.status_code}")

    except Exception as ex:
        hitlLogger.error(f"✅ Exception in {method_name}: {ex}")
        raise


def disable_entity(test_user, test_meta, unique_domain_name):
    method_name = get_method_name()
    service_env = test_user.test_env

    hitlLogger.info(f"✅ Starting: {method_name}")
    try:
        engine = get_test_db_engine()
        with Session(engine) as session:
            # Get config for the matching environment
            config: Optional[APIServiceConfig] = (
                session.query(APIServiceConfig)
                .filter(APIServiceConfig.service_env == service_env)
                .filter(APIServiceConfig.request_type == "adhoc")
                .filter(APIServiceConfig.service_desc == "createEntity")
                .first()
            )

            if not config:
                raise ValueError(f"No service config found for env: {service_env}")

        hitlLogger.info(f"✅ Building payload for {method_name}")
        payload = build_entity_payload(unique_domain_name, False)

        # 🔐 Access Token
        token = get_basic_access_token(service_env, "createEntity", "adhoc")

        # 🛠️ Headers
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        # 🌐 Endpoint
        url = f"https://{config.server_name}{config.service_endpoint_path}"

        hitlLogger.info(f"Disable Entity request is sent to : {url}")

        # 📡 Call API
        response = requests.post(url=url, json=payload, headers=headers, timeout=30)

        if response.status_code in (200, 201):
            hitlLogger.info(f"✅ Response code: {response.status_code}")

            # Handle empty or invalid JSON responses
            try:
                data = response.json() if response.text.strip() else {}
            except ValueError as json_error:
                hitlLogger.warning(f"⚠️ Invalid JSON response: {json_error}")
                data = {}

            if data and "data" in data and data.get("data") is not None:
                entity_id = data.get("data", {}).get("id")
                if entity_id:
                    hitlLogger.info(f"✅ Entity disabled with ID: {entity_id}")
                else:
                    hitlLogger.info("✅ Entity disabled successfully (no ID returned)")
            else:
                hitlLogger.info("✅ Entity disabled successfully (response structure differs)")
        else:
            raise Exception(f"Disable entity failed with response code: {response.status_code}")

    except Exception as ex:
        hitlLogger.error(f"✅ Exception in {method_name}: {ex}")
        raise


def disable_domain(test_user, test_meta, unique_domain_name):
    method_name = get_method_name()
    service_env = test_user.test_env

    hitlLogger.info(f"✅ Starting: {method_name}")
    try:
        engine = get_test_db_engine()
        with Session(engine) as session:
            # Get config for the matching environment
            config: Optional[APIServiceConfig] = (
                session.query(APIServiceConfig)
                .filter(APIServiceConfig.service_env == service_env)
                .filter(APIServiceConfig.request_type == "adhoc")
                .filter(APIServiceConfig.service_desc == "createDomain")
                .first()
            )

            if not config:
                raise ValueError(f"No service config found for env: {service_env}")

        hitlLogger.info(f"✅ Building payload for {method_name}")
        payload = build_domain_payload(unique_domain_name, False)

        # 🔐 Access Token
        token = get_basic_access_token(service_env, "createDomain", "adhoc")

        # 🛠️ Headers
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        # 🌐 Endpoint
        url = f"https://{config.server_name}{config.service_endpoint_path}"

        hitlLogger.info(f"Disable domain request is sent to : {url}")

        # 📡 Call API
        response = requests.post(url=url, json=payload, headers=headers, timeout=30)

        if response.status_code in (200, 201):
            hitlLogger.info(f"✅ Response code: {response.status_code}")

            # Handle empty or invalid JSON responses
            try:
                data = response.json() if response.text.strip() else {}
            except ValueError as json_error:
                hitlLogger.warning(f"⚠️ Invalid JSON response: {json_error}")
                data = {}

            if data and "data" in data and data.get("data") is not None:
                domain_id = data.get("data", {}).get("id")
                if domain_id:
                    hitlLogger.info(f"✅ Domain disabled with ID: {domain_id}")
                else:
                    hitlLogger.info("✅ Domain disabled successfully (no ID returned)")
            else:
                hitlLogger.info("✅ Domain disabled successfully (response structure differs)")
        else:
            raise Exception(f"Disable domain failed with response code: {response.status_code}")

    except Exception as ex:
        hitlLogger.error(f"✅ Exception in {method_name}: {ex}")
        raise
