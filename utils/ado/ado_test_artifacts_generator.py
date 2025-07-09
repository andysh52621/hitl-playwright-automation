import base64
import os
import re
import textwrap

import requests
import yaml

# Constants
ORG_URL = "https://dev.azure.com/Vizientinc"
PROJECT = "VizTech"
PLAN_ID = 979524
SUITE_ID = 1040029
BUILD_DEFINITION_ID = 3499
DOMAIN = "QAProduct"
ENTITY = "Product"
API_VERSION = "7.1-preview.3"
PAT_ENV = "HITL_ADO_PAT"


def get_auth_headers():
    pat = os.getenv(PAT_ENV)
    if not pat:
        raise EnvironmentError(f"Missing Azure DevOps PAT in env variable: {PAT_ENV}")
    auth = base64.b64encode(f":{pat}".encode()).decode()
    return {
        "Authorization": f"Basic {auth}",
        "Content-Type": "application/json"
    }, {
        "Authorization": f"Basic {auth}",
        "Content-Type": "application/json-patch+json"
    }


def fetch_story(story_id: int, headers_json):
    url = f"{ORG_URL}/{PROJECT}/_apis/wit/workitems/{story_id}?$expand=all&api-version={API_VERSION}"
    response = requests.get(url, headers=headers_json)
    response.raise_for_status()
    return response.json()


def sanitize_filename(name: str) -> str:
    name = re.sub(r'[^\w\s-]', '', name)
    name = re.sub(r'\s+', '_', name.strip().lower())
    return f"test_{name}"


def to_pascal_case(name: str) -> str:
    return ''.join(word.capitalize() for word in re.sub(r'[^\w\s]', '', name).split())


def generate_short_description(acceptance_html: str, fallback_title: str) -> str:
    items = re.findall(r"<li.*?>(.*?)</li>", acceptance_html, re.DOTALL | re.IGNORECASE)
    bullets = []
    for raw in items:
        clean = re.sub(r"<[^>]+>", "", raw).strip()
        if clean and len(clean) > 15:
            bullets.append(f"- {clean}")
        if len(bullets) >= 3:
            break
    return "\n".join(bullets) if bullets else fallback_title


def extract_tasks_from_acceptance_criteria(html: str):
    li_items = re.findall(r"<li.*?>(.*?)</li>", html, re.DOTALL | re.IGNORECASE)
    tasks = []
    for raw in li_items:
        line = re.sub(r"<[^>]+>", "", raw).strip()
        line = re.sub(r'\s+', ' ', line)
        title = line[:100].capitalize()
        desc = "\n".join(textwrap.wrap(line, width=90))
        tasks.append({"title": title, "description": desc})
    return tasks


def create_task(task, story_id, headers_patch):
    url = f"{ORG_URL}/{PROJECT}/_apis/wit/workitems/$Task?api-version={API_VERSION}"
    payload = [
        {"op": "add", "path": "/fields/System.Title", "value": task["title"]},
        {"op": "add", "path": "/fields/System.Description", "value": task["description"]},
        {"op": "add", "path": "/relations/-", "value": {
            "rel": "System.LinkTypes.Hierarchy-Reverse",
            "url": f"{ORG_URL}/{PROJECT}/_apis/wit/workItems/{story_id}",
            "attributes": {"comment": "Created from <li> in Acceptance Criteria"}
        }}
    ]
    r = requests.post(url, headers=headers_patch, json=payload)
    r.raise_for_status()
    return r.json()["id"]


def extract_test_steps(acceptance_html: str):
    li_items = re.findall(r"<li.*?>(.*?)</li>", acceptance_html, re.DOTALL | re.IGNORECASE)
    return [{"action": re.sub(r"<[^>]+>", "", li).strip(), "expected": "As per acceptance criteria"}
            for li in li_items if len(li.strip()) > 10]


def create_test_case_with_steps(story_id: int, title: str, acceptance_html: str, headers_json, headers_patch):
    url = f"{ORG_URL}/{PROJECT}/_apis/wit/workitems/$Test%20Case?api-version={API_VERSION}"
    payload = [
        {"op": "add", "path": "/fields/System.Title", "value": title},
        {"op": "add", "path": "/relations/-", "value": {
            "rel": "System.LinkTypes.Hierarchy-Reverse",
            "url": f"{ORG_URL}/{PROJECT}/_apis/wit/workItems/{story_id}",
            "attributes": {"comment": "Test case linked to story"}
        }}
    ]
    r = requests.post(url, headers=headers_patch, json=payload)
    r.raise_for_status()
    test_case_id = r.json()["id"]

    steps = extract_test_steps(acceptance_html)
    if steps:
        content = "<steps id='0'>" + "".join(
            f"<step id='{i + 1}' type='ActionStep'><parameterizedString isformatted='true'>{s['action']}</parameterizedString>"
            f"<parameterizedString isformatted='true'>{s['expected']}</parameterizedString><outcome>None</outcome></step>"
            for i, s in enumerate(steps)) + "</steps>"
        patch_url = f"{ORG_URL}/{PROJECT}/_apis/wit/workitems/{test_case_id}?api-version={API_VERSION}"
        patch_payload = [{"op": "add", "path": "/fields/Microsoft.VSTS.TCM.Steps", "value": content}]
        requests.patch(patch_url, headers=headers_patch, json=patch_payload).raise_for_status()

    requests.post(
        f"{ORG_URL}/{PROJECT}/_apis/test/Plans/{PLAN_ID}/suites/{SUITE_ID}/testcases/{test_case_id}?api-version={API_VERSION}",
        headers=headers_json).raise_for_status()

    return test_case_id


def generate_test_file(story_id: int, filename: str):
    os.makedirs(os.path.dirname(filename) or ".", exist_ok=True)
    content = f"""import allure
import pytest

from dao.test_execution_db_updater_dao import DBReporter
from pages.ui_pages.tm_entity_details_Page import EntityDetailsPage
from pages.ui_pages.tm_list_page import TaskManagerListPage
from tests.api_test_suite.test_api_product_create_task import test_api_product_create_task
from tests.core_test_suite.shared_tests import login_to_dashboard, navigate_to_hitl_dashboard, select_domain_card
from utils.ado.ado_decorators import ado_ui_testcase
from utils.ado.ado_step_logger import StepLogger

@pytest.mark.regression
@ado_ui_testcase
def test_story_{story_id}(page, test_user, reporter, ado_runner, request):
    meta = request.node.meta
    steps = request.node.steps

    test_api_product_create_adhoc_tasks(test_user, reporter, ado_runner, request)
    login_to_dashboard(page, test_user, reporter, steps)
    navigate_to_hitl_dashboard(page, test_user, reporter, steps)
    select_domain_card(page, meta, reporter, steps)

    run_sample_flow(page, reporter, steps)

@allure.step("Run a sample vendor lookup flow")
def run_sample_flow(page, reporter: DBReporter, step_logger: StepLogger):
    task_page = TaskManagerListPage(page)
    task_page.navigate_tasks_using_prev_next("user", reporter, step_logger)
"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Python test file created: {filename}")


def generate_yaml_file(story_id: int, title: str, description: str, filename: str):
    yaml_data = {
        "description": description,
        "domain": DOMAIN,
        "entity": ENTITY,
        "build_definition_id": BUILD_DEFINITION_ID,
        "ado_plan_id": PLAN_ID,
        "ado_suite_id": SUITE_ID,
        "ado_case_id": story_id,
        "ado_org_url": ORG_URL,
        "ado_project": PROJECT,
        "allure": {
            "feature": "HITL Task Management",
            "story": title,
            "title": title,
            "description": description,
            "severity": "critical",
            "owner": "andy.sharma",
            "tags": ["regression", "ui"]
        }
    }
    with open(filename, "w", encoding="utf-8") as f:
        yaml.dump(yaml_data, f, sort_keys=False)
    print(f"YAML file created: {filename}")


def generate_page_object_file(title: str, test_file: str):
    class_name = to_pascal_case(title) + "Page"
    test_folder = os.path.dirname(test_file) or "."
    page_name = os.path.basename(test_file).replace("test_", "").replace(".py", "_page.py")
    page_path = os.path.join(test_folder, page_name)
    os.makedirs(test_folder, exist_ok=True)

    content = f"""import inspect
import logging
import allure

from dao.api_ui_taskId_mapper_dao import TaskIdMapperDAO
from db_engine.test_automation_engine import get_engine
from utils.ado.ado_step_logger import StepLogger
from utils.generic.post_test_actions_handler import save_success, handle_exception
from dao.test_execution_db_updater_dao import DBReporter

hitlLogger = logging.getLogger("HitlLogger")

class {class_name}:
    def __init__(self, page):
        from lib.hitl_logger import LoggerPage
        self.page = page
        self.log = LoggerPage(page)
        self.dao = TaskIdMapperDAO(get_engine())

    @allure.step("Sample page method with interaction")
    def sample_interaction(self, reporter: DBReporter, step_logger: StepLogger):
        method_name = inspect.currentframe().f_code.co_name
        try:
            self.log.log("info", "Sample log message for sample_interaction()")
            save_success(reporter, method_name)
            step_logger.add_step("Sample interaction", "Simulated success")
        except Exception as e:
            step_logger.fail_step("Sample interaction", "Simulated failure", str(e))
            raise
"""
    with open(page_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Page object created: {page_path}")


def main():
    story_id = input("Enter ADO User Story ID: ").strip()
    if not story_id.isdigit():
        print("Invalid Story ID")
        return
    story_id = int(story_id)

    headers_json, headers_patch = get_auth_headers()
    story = fetch_story(story_id, headers_json)

    title = story.get("fields", {}).get("System.Title", f"Story {story_id}")
    acceptance_html = story.get("fields", {}).get("Microsoft.VSTS.Common.AcceptanceCriteria", "")
    clean_description = generate_short_description(acceptance_html, title)

    filename_base = sanitize_filename(title)
    test_file = f"{filename_base}.py"
    yaml_file = f"{filename_base}.yaml"

    print(f"\nStory title: {title}")
    print(f"Test file: {test_file}")
    print(f"YAML file: {yaml_file}")

    print("\nCreating tasks...")
    tasks = extract_tasks_from_acceptance_criteria(acceptance_html)
    for task in tasks:
        task_id = create_task(task, story_id, headers_patch)
        print(f"Created Task {task_id}: {task['title']}")

    print("\nCreating test case and adding to suite...")
    test_case_id = create_test_case_with_steps(story_id, title, acceptance_html, headers_json, headers_patch)
    print(f"Test case created and added to suite: {test_case_id}")

    print("\nGenerating test artifacts...")
    generate_test_file(test_case_id, test_file)
    generate_yaml_file(test_case_id, title, clean_description, yaml_file)
    generate_page_object_file(title, test_file)

    print("\nAll tasks complete!")


if __name__ == "__main__":
    main()
