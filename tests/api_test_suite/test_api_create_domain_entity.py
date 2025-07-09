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
def test_api_create_domain_entity(test_user, reporter, ado_runner, request):
    test_meta = request.node.meta
    step_logger = request.node.steps

    service_env = test_user.test_env
    unique_domain_name = "API" + test_meta.get("domain") + datetime.now().strftime("%m%d%H%M%S%f")
    validate_domain_creation(unique_domain_name, service_env, reporter, step_logger)
    validate_entity_creation(unique_domain_name, service_env, reporter, step_logger)
    validate_entity_disable(unique_domain_name, service_env, reporter, step_logger)
    validate_domain_disable(unique_domain_name, service_env, reporter, step_logger)


def validate_domain_creation(unique_domain_name, service_env, reporter, step_logger):
    method_name = get_method_name()

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

        assert response.status_code == 200

        if response.status_code in (200, 201):

            data = response.json()
            hitlLogger.info(f"✅ Response code: {response.status_code}")
            domain_id = data.get("data", {}).get("id")
            assert domain_id is not None

            save_success(reporter, method_name + f" domain id created : {domain_id}")

            if step_logger:
                step_logger.add_step(method_name, f"domain id created : {domain_id}")
        else:
            step_logger.fail_step(method_name, "Create domain failed response msg :", str(response.status_code))


    except Exception as ex:
        hitlLogger.error(f"✅ Exception in {method_name}: {ex}")
        if step_logger:
            step_logger.fail_step(method_name, "Create domain failed unexpectedly.", str(ex))
        handle_exception(None, ex, reporter, method_name)
        raise


def validate_entity_creation(unique_domain_name, service_env, reporter, step_logger):
    method_name = get_method_name()

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

        assert response.status_code == 200

        if response.status_code in (200, 201):

            data = response.json()
            hitlLogger.info(f"✅ Response code: {response.status_code}")
            entity_id = data.get("data", {}).get("id")
            assert entity_id is not None

            save_success(reporter, method_name + f" entity id created : {entity_id}")

            if step_logger:
                step_logger.add_step(method_name, f"entity id created : {entity_id}")
        else:
            step_logger.fail_step(method_name, "Create entity failed response msg :", str(response.status_code))


    except Exception as ex:
        hitlLogger.error(f"✅ Exception in {method_name}: {ex}")
        if step_logger:
            step_logger.fail_step(method_name, "Create entity failed unexpectedly.", str(ex))
        handle_exception(None, ex, reporter, method_name)
        raise


def validate_entity_disable(unique_domain_name, service_env, reporter, step_logger):
    method_name = get_method_name()

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

        assert response.status_code == 200

        if response.status_code in (200, 201):

            data = response.json()
            hitlLogger.info(f"✅ Response code: {response.status_code}")
            entity_id = data.get("data", {}).get("id")
            assert entity_id is not None

            save_success(reporter, method_name + f" entity id disabled : {entity_id}")

            if step_logger:
                step_logger.add_step(method_name, f"entity id disabled : {entity_id}")
        else:
            step_logger.fail_step(method_name, "Disable entity failed response msg :", str(response.status_code))


    except Exception as ex:
        hitlLogger.error(f"✅ Exception in {method_name}: {ex}")
        if step_logger:
            step_logger.fail_step(method_name, "Disable entity failed unexpectedly.", str(ex))
        handle_exception(None, ex, reporter, method_name)
        raise


def validate_domain_disable(unique_domain_name, service_env, reporter, step_logger):
    method_name = get_method_name()

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

        hitlLogger.info(f"Disabled domain request is sent to : {url}")

        # 📡 Call API
        response = requests.post(url=url, json=payload, headers=headers, timeout=30)

        assert response.status_code == 200

        if response.status_code in (200, 201):

            data = response.json()
            hitlLogger.info(f"✅ Response code: {response.status_code}")
            domain_id = data.get("data", {}).get("id")
            assert domain_id is not None

            save_success(reporter, method_name + f" domain id disabled : {domain_id}")

            if step_logger:
                step_logger.add_step(method_name, f"domain id disabled : {domain_id}")
        else:
            step_logger.fail_step(method_name, "Disable domain failed response msg :", str(response.status_code))


    except Exception as ex:
        hitlLogger.error(f"✅ Exception in {method_name}: {ex}")
        if step_logger:
            step_logger.fail_step(method_name, "Disable domain failed unexpectedly.", str(ex))
        handle_exception(None, ex, reporter, method_name)
        raise
