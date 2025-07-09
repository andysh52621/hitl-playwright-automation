import functools
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

import allure
import yaml
from playwright.sync_api import Page

from dao.test_execution_db_updater_dao import DBReporter
from pages.ui_pages.tm_schema_page import hitlLogger
from utils.ado.ado_step_logger import StepLogger
from utils.ado.ado_test_case_enricher import enrich_yaml_with_ado_test_case
from utils.generic.test_metadata_loader import load_test_meta, apply_allure_labels


def ado_ui_testcase(func):
    @functools.wraps(func)
    def wrapper(page, test_user, reporter, ado_runner, request):
        meta = load_test_meta(test_user, str(request.node.fspath))
        meta = enrich_yaml_with_ado_test_case(meta)
        apply_allure_labels(meta)

        steps = StepLogger()
        request.node.meta = meta
        request.node.steps = steps

        from datetime import datetime, timezone
        request.node.start_time = datetime.now(timezone.utc)

        try:
            result = func(page, test_user, reporter, ado_runner, request)
        except Exception as ex:
            steps.fail_step("Unhandled exception", "Test should run cleanly", str(ex))
            page_arg = page if not page.is_closed() else None
            ado_runner.finalize_result(
                case_id=meta["ado_case_id"],
                outcome="Failed",
                comment=str(ex),
                steps=steps.get_steps(),
                page=page_arg,
                start_time=request.node.start_time
            )
            test_name = request.node.name
            ado_runner.failures.append(test_name)
            raise  # re-raise to fail Pytest
        else:
            page_arg = page if not page.is_closed() else None
            ado_runner.finalize_result(
                case_id=meta["ado_case_id"],
                outcome="Passed",
                comment="All test steps passed.",
                steps=steps.get_steps(),
                page=page_arg,
                start_time=request.node.start_time
            )
            return result

    return wrapper


def ado_api_testcase(func):
    @functools.wraps(func)
    def wrapper(test_user, reporter, ado_runner, request):
        meta = load_test_meta(test_user, str(request.node.fspath))
        meta = enrich_yaml_with_ado_test_case(meta)
        apply_allure_labels(meta)

        steps = StepLogger()
        request.node.meta = meta
        request.node.steps = steps
        hitlLogger.info(f"🔍 Executing ADO test case: {meta.get('ado_case_id')} - {meta.get('name')}")

        try:
            from datetime import datetime, timezone
            request.node.start_time = datetime.now(timezone.utc)
            result = func(test_user, reporter, ado_runner, request)
            ado_runner.finalize_result(
                case_id=meta["ado_case_id"],
                outcome="Passed",
                comment="All test steps passed.",
                steps=steps.get_steps(),
                start_time=request.node.start_time
            )
            return result
        except Exception as ex:
            steps.fail_step("Unhandled exception", "Test should run cleanly", str(ex))
            ado_runner.finalize_result(
                case_id=meta["ado_case_id"],
                outcome="Failed",
                comment=str(ex),
                steps=steps.get_steps(),
                start_time=request.node.start_time  # Safe: no page needed for API tests
            )
            if hasattr(ado_runner, "failures"):
                ado_runner.failures.append(meta["name"])
            else:
                ado_runner.failures = [meta["name"]]
            raise  # Ensure Pytest marks it as failed

    return wrapper
