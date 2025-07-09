import logging
import time

import pytest
from sqlalchemy import func

from db_engine.test_automation_engine import get_app_db_session, get_test_db_session
from db_models.api_test_db_models import APIUITaskMapping
from db_models.hitl_app_db_models import DM_QAProduct_Product, TM_Exception_Log
from tests.core_test_suite.create_batch_product_tasks import create_batch_product_tasks
from utils.ado.ado_decorators import ado_api_testcase
from utils.api.api_batch_product_payload_builder import build_batch_payload
from utils.generic.get_readable_method_name import get_method_name
from utils.generic.post_test_actions_handler import save_success, handle_exception

hitlLogger = logging.getLogger("HitlLogger")


@pytest.mark.api
@pytest.mark.regression
@ado_api_testcase
def test_create_batch_product_tasks(test_user, reporter, ado_runner, request):
    tasks_count = 100
    run_batch_insert_success_case(test_user, tasks_count, reporter, request)
    run_batch_insert_missing_event_domain_case(test_user, tasks_count, reporter, request)


# comment
def run_batch_insert_success_case(test_user, tasks_count, reporter, request):
    method_name = get_method_name()
    step_logger = request.node.steps
    test_meta = request.node.meta

    hitlLogger.info(f"✅ Starting: {method_name}")
    try:
        hitlLogger.info(f"✅ Building payload for {tasks_count} tasks")
        payload = build_batch_payload(test_meta, tasks_count)

        hitlLogger.info("✅ Submitting full batch payload...")
        transaction_id = create_batch_product_tasks(test_user, tasks_count, payload)

        _log_and_wait(transaction_id)

        hitlLogger.info("✅ Querying batch insert results...")
        status, completed_count, error_count = query_batch_insert_status(
            test_user, transaction_id, reporter, step_logger
        )

        hitlLogger.info(f"✅ Status: {status}, Completed: {completed_count}, Errors: {error_count}")

        assert status == "Completed", f"Expected status 'Completed', got '{status}'"
        assert completed_count == tasks_count, f"Expected {tasks_count} tasks, got {completed_count}"
        assert error_count == 0, f"Expected 0 errors, got {error_count}"

        save_success(reporter, method_name)
        if step_logger:
            step_logger.add_step(method_name, "Batch insert succeeded with expected task count and no errors.")

    except Exception as ex:
        hitlLogger.error(f"✅ Exception in {method_name}: {ex}")
        if step_logger:
            step_logger.fail_step(method_name, "Batch insert failed unexpectedly.", str(ex))
        handle_exception(None, ex, reporter, method_name)
        raise


def run_batch_insert_missing_event_domain_case(test_user, tasks_count, reporter, request):
    method_name = get_method_name()
    step_logger = request.node.steps
    test_meta = request.node.meta

    hitlLogger.info(f"✅ Starting: {method_name}")
    try:
        hitlLogger.info(f"✅ Building payload for {tasks_count} tasks (without eventDomain)")
        payload = build_batch_payload(test_meta, tasks_count)
        payload.pop("eventDomain", None)

        hitlLogger.info("✅ Submitting batch insert with missing eventDomain...")
        transaction_id = create_batch_product_tasks(test_user, tasks_count, payload)

        _log_and_wait(transaction_id)

        hitlLogger.info("✅ Querying failed batch insert results...")
        status, completed_count, error_count = query_batch_insert_status(
            test_user, transaction_id, reporter, step_logger
        )

        hitlLogger.info(f"✅ Status: {status}, Completed: {completed_count}, Errors: {error_count}")

        assert status == "Failed", f"Expected status 'Failed', got '{status}'"
        assert completed_count == 0, f"Expected 0 tasks completed, got {completed_count}"
        assert error_count >= 1, f"Expected at least 1 error, got {error_count}"

        save_success(reporter, method_name)
        if step_logger:
            step_logger.add_step(method_name, "Missing eventDomain triggered expected batch failure.")

    except Exception as ex:
        hitlLogger.error(f"✅ Exception in {method_name}: {ex}")
        if step_logger:
            step_logger.fail_step(method_name, "Expected batch failure did not occur.", str(ex))
        handle_exception(None, ex, reporter, method_name)
        raise


def query_batch_insert_status(test_user, transaction_id, reporter=None, step_logger=None):
    method_name = get_method_name()
    app_db_session = get_app_db_session(test_user)
    test_db_session = get_test_db_session()

    try:
        if not transaction_id:
            msg = "✅ No valid transaction ID supplied for batch status check."
            hitlLogger.info(msg)
            if step_logger:
                step_logger.add_step(method_name, msg)
            pytest.skip(msg)

        hitlLogger.info(f"✅ Processing transaction ID: {transaction_id}")
        if step_logger:
            step_logger.add_step(method_name, f"Processing transaction ID: {transaction_id}")

        tasks_batch_completed = (
            app_db_session.query(func.count())
            .filter(DM_QAProduct_Product.Transaction_ID == transaction_id)
            .scalar()
        )
        hitlLogger.info(f"✅ Tasks Completed: {tasks_batch_completed}")
        if step_logger:
            step_logger.add_step(method_name, f"Tasks Completed: {tasks_batch_completed}")

        result = (
            app_db_session.query(
                func.min(DM_QAProduct_Product.Created_Date).label("StartTime"),
                func.max(DM_QAProduct_Product.Created_Date).label("EndTime")
            )
            .filter(DM_QAProduct_Product.Transaction_ID == transaction_id)
            .one()
        )
        start_time = result.StartTime
        end_time = result.EndTime
        duration_ms = (
            int((end_time - start_time).total_seconds() * 1000)
            if start_time and end_time else None
        )

        hitlLogger.info(f"✅ Start Time: {start_time}")
        hitlLogger.info(f"✅ End Time: {end_time}")
        hitlLogger.info(f"✅ Duration: {duration_ms} ms")
        if step_logger:
            step_logger.add_step(method_name, f"Start Time: {start_time}")
            step_logger.add_step(method_name, f"End Time: {end_time}")
            step_logger.add_step(method_name, f"Duration (ms): {duration_ms}")

        batch_errors = (
            app_db_session.query(func.count())
            .filter(TM_Exception_Log.Key == transaction_id)
            .scalar()
        )
        hitlLogger.info(f"✅ Errors Detected: {batch_errors}")
        if step_logger:
            step_logger.add_step(method_name, f"Batch Errors: {batch_errors}")

        status = "Failed" if batch_errors > 0 or duration_ms is None else "Completed"
        hitlLogger.info(f"✅ Final Status: {status}")
        if step_logger:
            step_logger.add_step(method_name, f"Final Status: {status}")

        mapping = (
            test_db_session.query(APIUITaskMapping)
            .filter(APIUITaskMapping.transaction_id == transaction_id)
            .first()
        )
        if mapping:
            mapping.batch_processing_time_ms = duration_ms
            mapping.batch_errors = batch_errors
            mapping.status = status
            test_db_session.commit()
            hitlLogger.info(f"✅ Mapping updated in DB for transaction ID: {transaction_id}")
            if step_logger:
                step_logger.add_step(method_name, f"Mapping updated in DB for transaction ID: {transaction_id}")
        else:
            hitlLogger.warning(f"✅ No matching mapping found for TransactionId {transaction_id}")
            if step_logger:
                step_logger.add_step(method_name, f"No mapping found for transaction ID: {transaction_id}")

        if reporter:
            save_success(reporter, method_name)

        return status, tasks_batch_completed, batch_errors

    except Exception as e:
        hitlLogger.error(f"✅ Exception during batch processing time calculation: {e}")
        if step_logger:
            step_logger.fail_step(method_name, "Exception during batch status query.", str(e))
        if reporter:
            test_db_session.rollback()
        raise

    finally:
        test_db_session.close()
        app_db_session.close()


def _log_and_wait(transaction_id, sleeptime=2):
    hitlLogger.info(f"✅ Sleeping for {sleeptime} seconds before querying transaction ID: {transaction_id}")
    time.sleep(sleeptime)
