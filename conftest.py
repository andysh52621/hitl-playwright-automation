import json
import logging
import os
import platform
import shutil
import socket
import subprocess
import sys
from datetime import datetime

import allure
import pytest
from playwright.sync_api import sync_playwright

from ado.ado_test_runner import ADOTestRunner
from dao.test_execution_db_updater_dao import DBReporter
from db_engine.test_automation_engine import get_test_db_engine
from db_models.ui_test_db_models import Base
from domain_models.test_user_model import load_user_config_from_excel
from email_utility.email_util import get_timestamped_filename
from utils.ado.ado_test_case_enricher import enrich_yaml_with_ado_test_case
from utils.ado.ado_test_plan_reader import fetch_total_planned_cases
from utils.allure.allure_writer import write_allure_environment_file, generate_fancy_summary, \
    allure_generate_categories_and_piecharts
from utils.generic.get_project_root import get_project_root
from utils.generic.logger_config import configure_logging
from utils.generic.screenshots_cleanup import clean_screenshots_dir
from utils.generic.test_cleanup import clean_test_steps
from utils.generic.test_metadata_loader import load_test_meta, get_meta_path_from_test_file

hitlLogger = logging.getLogger("HitlLogger")
system = platform.system()

BASE_DIR = None

if system == "Windows":
    BASE_DIR = get_project_root()
    print("Running on Windows")
elif system == "Linux" or os.getenv("WORK_DIR") == "/app":
    BASE_DIR = os.getenv("WORK_DIR", "/app")
    print("Running on Linux")
else:
    print(f"Running on: {system}")

ALLURE_RESULTS_DIR = os.path.join(BASE_DIR, "allure-results")
ALLURE_REPORT_DIR = os.path.join(BASE_DIR, "allure-report")
SCREENSHOTS_DIR = os.path.join(BASE_DIR, "screenshots")
LOG_FILE_PATH = os.path.join(BASE_DIR, "hitl_test.log")

hitlLogger.info(f"📁 BASE_DIR: {BASE_DIR}")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE_PATH, mode='w', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ],
    force=True
)


def write_allure_categories():
    categories = [
        {"name": "Assertion Failed", "matchedStatuses": ["failed"], "messageRegex": ".*AssertionError.*"},
        {"name": "Timeout", "matchedStatuses": ["failed"], "messageRegex": ".*Timeout.*"},
        {"name": "Element Not Found", "matchedStatuses": ["failed"], "traceRegex": ".*NoSuchElementException.*"},
        {"name": "Broken Test", "matchedStatuses": ["broken"]},
        {"name": "Flaky Test", "matchedStatuses": ["passed", "failed"]}
    ]

    if not os.path.exists(ALLURE_RESULTS_DIR):
        os.makedirs(ALLURE_RESULTS_DIR)
        hitlLogger.info(f"📁 Created Allure results folder at: {ALLURE_RESULTS_DIR}")

    with open(os.path.join(ALLURE_RESULTS_DIR, "categories.json"), "w") as f:
        json.dump(categories, f, indent=2)

    hitlLogger.info("🔹 Allure categories.json written.")


def write_allure_executor():
    executor_data = {
        "name": "PyCharm Local",
        "type": "local",
        "reportName": "HILT Automation Report",
        "buildName": socket.gethostname(),
        "buildUrl": "",
        "reportUrl": "",
        "executorUri": socket.gethostbyname(socket.gethostname())
    }

    if not os.path.exists(ALLURE_RESULTS_DIR):
        os.makedirs(ALLURE_RESULTS_DIR)
        hitlLogger.info(f"📁 Created Allure results folder at: {ALLURE_RESULTS_DIR}")

    with open(os.path.join(ALLURE_RESULTS_DIR, "executor.json"), "w") as f:
        json.dump(executor_data, f, indent=2)

    hitlLogger.info("🔹 Allure executor.json written for test metadata.")


def copy_allure_history():
    src = os.path.join(BASE_DIR, "allure-report", "history")
    dst = os.path.join(ALLURE_RESULTS_DIR, "history")

    if os.path.exists(src):
        if not os.path.exists(ALLURE_RESULTS_DIR):
            os.makedirs(ALLURE_RESULTS_DIR)
        shutil.copytree(src, dst, dirs_exist_ok=True)
        hitlLogger.info("🔹 Allure history copied for trend tracking.")
    else:
        hitlLogger.info("⚠️ No previous Allure report history found to copy.")


def get_git_metadata():
    try:
        commit_hash = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).decode().strip()
        branch_name = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]).decode().strip()
        return commit_hash, branch_name
    except Exception as e:
        return "unknown", "unknown"


def collect_test_metadata(test_env: str):
    commit_hash, branch_name = get_git_metadata()
    return {
        "env": test_env,
        "machine": os.getenv("COMPUTERNAME") or os.getenv("HOSTNAME") or "Unknown",
        "owner": "andy.sharma@vizientinc.com",
        "host_name": socket.gethostname(),
        "host_address": socket.gethostbyname(socket.gethostname()),
        "os_name": platform.system(),
        "os_version": platform.version(),
        "browser": "Chromium",
        "python_version": sys.version.split()[0],
        "branch": branch_name,
        "commit": commit_hash,
    }


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_setup(item):
    yield  # Let all fixtures initialize first

    if "test_user" in item.funcargs:
        test_user = item.funcargs["test_user"]
    else:
        hitlLogger.warning("⚠️ test_user is not initialized. Skipping metadata tagging.")
        return

    meta = collect_test_metadata(test_user.test_env)
    for key, value in meta.items():
        allure.dynamic.label(key, value)

    if item.get_closest_marker("regression"):
        allure.dynamic.label("duration", "long")
    elif item.get_closest_marker("smoke"):
        allure.dynamic.label("duration", "short")
    else:
        allure.dynamic.label("duration", "medium")

    with allure.step("Test Metadata"):
        info = "\n".join([f"{k.upper()}: {v}" for k, v in meta.items()])
        allure.attach(info, name="Test Environment Info", attachment_type=allure.attachment_type.TEXT)


@pytest.fixture(scope='session')
def test_user():
    excel_path = os.path.join(BASE_DIR, "user-config", "test_user_config.xlsx")
    user_config = load_user_config_from_excel(excel_path)
    if not user_config:
        pytest.exit("❌ test_user_config.xlsx missing or unreadable.")
    return user_config


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    engine = get_test_db_engine()
    Base.metadata.create_all(engine)


@pytest.fixture(scope="function")
def browser():
    with sync_playwright() as p:
        headless = os.getenv("HEADLESS", "true").lower() == "true"
        browser = p.chromium.launch(
            headless=headless,
            args=["--window-size=1980,1080", "--window-position=0,0"]
            # devtools=True
        )
        yield browser
        browser.close()


@pytest.fixture(scope="function")
def context(browser, request, ado_runner):
    video_dir = os.path.join(BASE_DIR, "videos")
    os.makedirs(video_dir, exist_ok=True)

    context = browser.new_context(no_viewport=True, record_video_dir=video_dir)
    request.node.video_info = {}  # Init

    yield context  # ⬅️ page will be created by `page` fixture

    try:
        # Access page AFTER yield when it has been created
        pages = context.pages
        if pages:
            page = pages[0]
            video = getattr(page, "video", None)
            if video:
                orig = video.path()
                meta = getattr(request.node, "meta", {})
                case_id = str(meta.get("ado_case_id", "unknown"))
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                new = os.path.join(video_dir, f"video_{case_id}_{ts}.webm")
                request.node.video_info = {"original": orig, "renamed": new, "case_id": case_id}
    except Exception as e:
        hitlLogger.warning(f"⚠️ Video finalization failed: {e}")

    context.close()


@pytest.fixture(scope="function")
def page(context):
    return context.new_page()


def pytest_sessionstart(session):
    clean_test_steps()
    configure_logging()
    hitlLogger.info("🧹 Cleaning screenshots and videos folder before test session...")

    # Clean screenshots directory
    clean_screenshots_dir(screenshots_dir=SCREENSHOTS_DIR, age_minutes=0)

    # Clean videos directory
    videos_dir = os.path.join(BASE_DIR, "videos")
    if os.path.exists(videos_dir):
        for f in os.listdir(videos_dir):
            try:
                path = os.path.join(videos_dir, f)
                if os.path.isfile(path):
                    os.remove(path)
                    hitlLogger.info(f"🗑️ Removed video: {f}")
            except Exception as e:
                hitlLogger.warning(f"⚠️ Failed to delete video {f}: {e}")
    else:
        os.makedirs(videos_dir)
        hitlLogger.info(f"📁 Created videos folder: {videos_dir}")

    # Allure config and metadata
    copy_allure_history()
    write_allure_executor()
    write_allure_categories()
    # write_allure_executor_file(ALLURE_RESULTS_DIR)
    # write_allure_categories_file(ALLURE_RESULTS_DIR)

    try:
        excel_path = os.path.join(BASE_DIR, "user-config", "test_user_config.xlsx")
        user_config = load_user_config_from_excel(excel_path)

        if user_config:
            metadata = collect_test_metadata(user_config.test_env)
            write_allure_environment_file(ALLURE_RESULTS_DIR, user_config, metadata)
        else:
            hitlLogger.warning("⚠️ user_config could not be loaded in pytest_sessionstart.")
    except Exception as e:
        hitlLogger.warning(f"⚠️ Exception during writing allure environment file: {e}")


def pytest_sessionfinish(session, exitstatus):
    if not hasattr(session, "ado_runner"):
        hitlLogger.warning("⚠️ 'ado_runner' not available — skipping Allure reporting.")
        return

    for item in getattr(session, "items", []):
        info = getattr(item, "video_info", {})
        orig, renamed, case_id = info.get("original"), info.get("renamed"), info.get("case_id")
        if orig and renamed and os.path.exists(orig):
            try:
                os.rename(orig, renamed)
                session.ado_runner.set_result_id_for_case(case_id)
                session.ado_runner.attach_video(renamed, comment="Test session video")
            except Exception as e:
                hitlLogger.warning(f"❌ Could not finalize video {orig}: {e}")

    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
    screenshots_zip = os.path.join(SCREENSHOTS_DIR, get_timestamped_filename("screenshots_bundle", "zip"))
    allure_zip = os.path.join(SCREENSHOTS_DIR, get_timestamped_filename("allure-report", "zip"))

    SMTP_SERVER = "mailman.corp.vizientinc.com"
    SMTP_PORT = 25
    EMAIL_USER = "alertmanager@vizientinc.com"
    EMAIL_PASSWORD = ""
    TO_EMAIL = "andy.sharma@vizientinc.com"

    try:
        socket.gethostbyname(SMTP_SERVER)
        hitlLogger.info(f"🔹 SMTP server resolved: {SMTP_SERVER}")

        # ✅ Now safe to access ado_runner-dependent code
        allure_generate_categories_and_piecharts(session)
        generate_fancy_summary(session, session.ado_runner)

        command = shutil.which(
            "allure") if system != "Windows" else get_project_root() + "\\allure-2.33.0\\bin\\allure.bat"
        hitlLogger.info(f"🔹 Using Allure CLI: {command}")
        subprocess.run([command, "generate", ALLURE_RESULTS_DIR, "-o", ALLURE_REPORT_DIR, "--clean"], check=True)
        hitlLogger.info("🔹 Allure report generated.")
    except Exception as e:
        hitlLogger.error(f"❌ Failed during Allure processing or email: {e}")

    # if zip_screenshots(SCREENSHOTS_DIR, screenshots_zip):
    #     send_email_with_zip(SMTP_SERVER, SMTP_PORT, EMAIL_USER, EMAIL_PASSWORD, TO_EMAIL,
    #                         "HITL Automation - Error Screenshots",
    #                         "Attached are the HITL app screenshots.", screenshots_zip)

    report_path = os.path.join("allure-results", "test_coverage_report.html")
    session.ado_runner.attach_to_run(report_path, comment="HITL Test Coverage Summary Report")
    add_email_notification_on_failure(session, session.ado_runner, SCREENSHOTS_DIR, ALLURE_RESULTS_DIR,
                                      session.test_user_obj)


@pytest.fixture(scope="function")
def reporter(request, test_user):
    from utils.generic.test_metadata_loader import load_test_meta
    test_func = request.node.function
    meta = load_test_meta(test_user, str(request.node.fspath))
    db = DBReporter()
    db.start_test_execution(
        test_name=meta.get("name", request.node.name),
        description=meta.get("description", test_func.__doc__ or "No doc provided."),
        env=test_user.test_env,
        browser=test_user.browser_type,
        domain=meta.get("domain"),
        entity=meta.get("entity"),
        created_by=meta.get("created_by", "automation_user"),
        from_pipeline=meta.get("from_pipeline", "local"),
        ado_plan_id=meta.get("ado_plan_id"),
        ado_suite_id=meta.get("ado_suite_id"),
        ado_case_id=meta.get("ado_case_id"),
        build_definition_id=meta.get("build_definition_id")
    )
    yield db
    if not db._execution_ended:
        status = getattr(request.node, "rep_call", None)
        if status is None or status.failed:
            db.end_test_execution("FAILED")
        elif status.skipped:
            db.end_test_execution("SKIPPED")
        else:
            db.end_test_execution("PASSED")


@pytest.fixture(scope="session", autouse=True)
def ado_runner(request, test_user):
    meta = load_test_meta(test_user, get_meta_path_from_test_file("test_product_task_resolve.py"))
    meta = enrich_yaml_with_ado_test_case(meta)
    runner = ADOTestRunner(meta)
    runner.start_test_run()
    request.session.ado_runner = runner
    runner.failures = []
    yield runner
    summary = f"❌ {len(runner.failures)} failed: {', '.join(runner.failures)}" if runner.failures else "✅ All tests passed."
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    path = os.path.join(SCREENSHOTS_DIR, f"ado_test_run_summary_{ts}.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(summary)
    runner.attach_to_run(path, comment="Run summary")

    run_env = os.getenv("RUN_ENV", "").lower() or test_user.test_env
    is_pipeline = os.getenv("IS_PIPELINE", "local").lower()
    run_type = "Pipeline" if is_pipeline == "cicd" else "Local"
    timestamp = datetime.now().strftime("%Y-%m-%d %I:%M%p")
    try:
        branch_name = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]).decode().strip()
    except Exception as e:
        branch_name = "unknown"

    total_cases = fetch_total_planned_cases(runner)
    executed_cases = runner.executed_test_count
    passed_cases = runner.executed_test_count - len(runner.failures)
    skipped = runner.skipped_test_count
    coverage = (executed_cases / total_cases) * 100
    # move this logic to ado runner and not in conftest file

    run_summary_comment = (
        f"\n\n Test Run Summary:\n"
        f"- CortexDomainTag: {meta.get('cortex_domain_tag')}\n"
        f"- Mode: {run_type}\n"
        f"- Env: {run_env.upper()}\n"
        f"- Branch: {branch_name}\n"
        f"- Timestamp: {timestamp}\n"
        f"- Planned: {total_cases}\n"
        f"- Executed: {executed_cases}\n"
        f"- TestCoverage: {coverage:.2f}%\n"
        f"- Passed: {passed_cases}\n"
        f"- Failed: {len(runner.failures)}\n"
        f"- Skipped: {skipped}\n"
        f"- Errored: {skipped}\n"
    )

    runner.complete_run(run_summary_comment)

    request.session.test_user_obj = test_user


@pytest.hookimpl
def pytest_runtest_makereport(item, call):
    @pytest.hookimpl
    def pytest_runtest_makereport(item, call):
        if call.when == "call":
            setattr(item, "rep_call", call)
            if call.excinfo and call.excinfo.type.__name__ == "AssertionError":
                # Automatically mark test as failed for email tracking
                if hasattr(item.session, "ado_runner") and hasattr(item.session.ado_runner, "failures"):
                    item.session.ado_runner.failures.append(item.name)


def add_email_notification_on_failure(session, runner, screenshots_dir, allure_results_dir, test_user):
    from email.message import EmailMessage
    import smtplib
    import os
    import mimetypes
    from utils.email.email_html_generator import generate_html_email

    if not runner.failures:
        return

    # ✅ Skip email if not running in CI/CD pipeline
    if os.getenv("IS_PIPELINE", "local").lower() != "cicd":
        runner_log = getattr(runner, 'hitlLogger', None)
        if runner_log:
            runner_log.info("📭 Email skipped: not running in pipeline mode.")
        return

    # Build failure detail links
    failure_details_html = ""
    for name in runner.failures:
        case_id = next((cid for cid, outcome in runner.case_outcomes.items() if outcome == "Failed"), None)
        work_item_link = f"{runner.org_url}/{runner.project}/_workitems/edit/{case_id}" if case_id else "#"
        result_id = runner.result_id_map.get(str(case_id))
        result_link = (
            f"{runner.org_url}/{runner.project}/_TestManagement/Runs?runId={runner.run_id}&_a=resultSummary&resultId={result_id}"
            if result_id else "#"
        )
        failure_details_html += f"""
        <li>
          <strong>{name}</strong><br/>
          🔗 <a href="{work_item_link}">Work Item (Case ID: {case_id})</a><br/>
          🧪 <a href="{result_link}">Test Result Detail</a>
        </li>
        """

    # Generate HTML body
    html_body = generate_html_email(runner, test_user, failure_details_html)

    # Generate subject line
    from datetime import datetime
    import subprocess

    failed = len(runner.failures)
    run_env = os.getenv("RUN_ENV", "").lower() or test_user.test_env
    is_pipeline = os.getenv("IS_PIPELINE", "local").lower()
    run_type = "PIPELINE" if is_pipeline == "cicd" else "LOCAL"
    timestamp = datetime.now().strftime("%Y-%m-%d %I:%M%p")

    try:
        branch_name = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]).decode().strip()
    except Exception as e:
        branch_name = "unknown"

    subject = f"❌ {failed} Test(s) Failed | {run_type} | ENV: {run_env.upper()} | BRANCH: {branch_name} | {timestamp}"

    # Prepare email
    msg = EmailMessage()
    msg["From"] = "alertmanager@vizientinc.com"
    msg["To"] = "andy.sharma@vizientinc.com;gurubaran.sethuraman@vizientinc.com;deepali.shah@vizientinc.com"
    msg["Subject"] = subject
    msg.set_content("This is a MIME email. Please view it in HTML.")
    msg.add_alternative(html_body, subtype="html")

    # Attach pytest_html_report.html
    html_report_path = os.path.join("pytest_html_report.html")
    if os.path.exists(html_report_path):
        with open(html_report_path, "rb") as f:
            file_data = f.read()
            file_name = os.path.basename(html_report_path)
            mime_type, _ = mimetypes.guess_type(html_report_path)
            maintype, subtype = mime_type.split("/") if mime_type else ("application", "octet-stream")
            msg.add_attachment(file_data, maintype=maintype, subtype=subtype, filename=file_name)

    # Send the email
    with smtplib.SMTP("mailman.corp.vizientinc.com", 25) as server:
        server.send_message(msg)


def pytest_addoption(parser):
    parser.addoption("--suite-type", action="store", default="", help="Suite type: regression/smoke/standalone")


def pytest_configure(config):
    suite_type = config.getoption("--suite-type")

    if not suite_type:
        # Fallback inference based on markers or keyword expressions
        mark_expr = config.option.markexpr
        keyword_expr = config.option.keyword

        if "regression" in mark_expr:
            suite_type = "regression suite"
        elif "smoke" in mark_expr:
            suite_type = "smoke suite"
        elif keyword_expr:
            suite_type = "adhoc test"
        else:
            suite_type = "unidentified test"

    os.environ["SUITE_TYPE"] = suite_type
