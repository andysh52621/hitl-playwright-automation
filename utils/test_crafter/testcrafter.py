import argparse
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


def sanitize_filename(title: str, fallback: str = "") -> str:
    stopwords = {"hitl", "qa", "automation", "story", "test", "case", "endpoint", "enhance", "via"}
    title = re.sub(r'[^\w\s]', '', title.lower())
    keywords = [w for w in title.split() if len(w) > 2 and w not in stopwords]
    name = '_'.join(keywords[:5])
    return f"test_{name}"[:50] if name else fallback or "test_story"


def to_pascal_case(title: str) -> str:
    stopwords = {"hitl", "qa", "automation", "story", "test", "case", "endpoint", "enhance", "via"}
    title = re.sub(r'[^\w\s]', '', title.lower())
    words = [w.capitalize() for w in title.split() if len(w) > 2 and w not in stopwords]
    return ''.join(words[:5]) or "GeneratedPage"


def convert_to_line_items(text: str) -> str:
    clean = re.sub(r'<[^>]+>', '\n', text)
    clean = re.sub(r'&[a-z]+;', ' ', clean)
    clean = re.sub(r'\n+', '\n', clean).strip()
    lines = re.split(r'(?:^|\n)\s*\d+[.)-]\s*', clean)
    items = [line.strip() for line in lines if line.strip()]
    return "\n".join(f"<li>{item}</li>" for item in items)


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
    steps = []
    for li in li_items:
        text = re.sub(r"<[^>]+>", "", li)  # Remove HTML tags
        text = re.sub(r"&[a-z]+;", " ", text)  # Replace HTML entities like &nbsp;
        text = text.strip()
        if len(text) > 10:
            steps.append({
                "action": text,
                "expected": "As per acceptance criteria"
            })
    return steps


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

    # Extract test steps
    steps = extract_test_steps(acceptance_html)
    print(f"\n🧪 Extracted {len(steps)} test steps:")
    # for s in steps:
    # print(" -", s["action"])

    if steps:
        content = "<steps id='0'>" + "".join(
            f"<step id='{i + 1}' type='ActionStep'>"
            f"<parameterizedString isformatted='true'>{s['action']}</parameterizedString>"
            f"<parameterizedString isformatted='true'>{s['expected']}</parameterizedString>"
            f"<outcome>None</outcome></step>"
            for i, s in enumerate(steps)) + "</steps>"

        patch_url = f"{ORG_URL}/{PROJECT}/_apis/wit/workitems/{test_case_id}?api-version={API_VERSION}"
        patch_payload = [{
            "op": "replace",  # 🔁 Use replace instead of add
            "path": "/fields/Microsoft.VSTS.TCM.Steps",
            "value": content
        }]

        response = requests.patch(patch_url, headers=headers_patch, json=patch_payload)
        response.raise_for_status()

    # Add to test suite
    requests.post(
        f"{ORG_URL}/{PROJECT}/_apis/test/Plans/{PLAN_ID}/suites/{SUITE_ID}/testcases/{test_case_id}?api-version={API_VERSION}",
        headers=headers_json).raise_for_status()

    return test_case_id


def generate_test_file(story_id: int, filename: str):
    os.makedirs(os.path.dirname(filename) or ".", exist_ok=True)
    content = f"""import allure
import pytest

from dao.test_execution_db_updater_dao import DBReporter
from pages.ui_pages.tm_list_page import TaskManagerListPage
from tests.api_test_suite.test_api_product_create_adhoc_tasks import test_create_adhoc_product_tasks
from tests.core_test_suite.shared_tests import (login_to_dashboard,
                                                navigate_to_hitl_dashboard, select_domain_card)
from utils.ado.ado_decorators import ado_ui_testcase
from utils.ado.ado_step_logger import StepLogger

@pytest.mark.regression
@ado_ui_testcase
def test_story_{story_id}(page, test_user, reporter, ado_runner, request):
    meta = request.node.meta
    steps = request.node.steps

    test_create_adhoc_product_tasks(test_user, reporter, ado_runner, request)
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
    print(f"✅ Python test file created: {filename}")


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

    def str_presenter(dumper, data):
        if '\n' in data:
            return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
        return dumper.represent_scalar('tag:yaml.org,2002:str', data)

    yaml.SafeDumper.add_representer(str, str_presenter)

    with open(filename, "w", encoding="utf-8") as f:
        yaml.dump(yaml_data, f, sort_keys=False, allow_unicode=True, Dumper=yaml.SafeDumper)

    print(f"✅ YAML file created: {filename}")


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
from db_engine.test_automation_engine import get_test_db_engine
from utils.ado.ado_step_logger import StepLogger
from utils.generic.post_test_actions_handler import save_success, handle_exception
from dao.test_execution_db_updater_dao import DBReporter

hitlLogger = logging.getLogger("HitlLogger")

class {class_name}:
    def __init__(self, page):
        from lib.hitl_logger import LoggerPage
        self.page = page
        self.log = LoggerPage(page)
        self.dao = TaskIdMapperDAO(get_test_db_engine())

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
    print(f"✅ Page object created: {page_path}")


def main():
    parser = argparse.ArgumentParser(
        description="TestCrafter: Generate test cases, YAML, and page objects from ADO User Stories.")
    parser.add_argument('--story-id', required=True, type=int, help='ADO User Story ID')
    parser.add_argument('--output-dir', required=True, help='Folder where test, YAML, and page files are generated')
    args = parser.parse_args()

    story_id = args.story_id
    output_dir = args.output_dir
    os.makedirs(output_dir, exist_ok=True)

    headers_json, headers_patch = get_auth_headers()
    story = fetch_story(story_id, headers_json)

    title = story.get("fields", {}).get("System.Title", f"Story {story_id}")

    raw_acceptance = story.get("fields", {}).get("Microsoft.VSTS.Common.AcceptanceCriteria", "")
    print("\n📄 Raw Acceptance Criteria:\n", raw_acceptance)

    if "<li>" not in raw_acceptance.lower():
        print("\n🔁 Converting acceptance criteria to <li> format...")
        acceptance_html = f"<ul>\n{convert_to_line_items(raw_acceptance)}\n</ul>"
        print("\n✅ Converted Acceptance Criteria:\n", acceptance_html)
    else:
        acceptance_html = raw_acceptance

    raw_description = generate_short_description(acceptance_html, title)
    clean_description = textwrap.dedent(raw_description).strip()

    filename_base = sanitize_filename(title, fallback=f"test_story_{story_id}")
    test_file = os.path.join(output_dir, f"{filename_base}.py")
    yaml_file = os.path.join(output_dir, f"{filename_base}.yaml")

    print(f"\n📘 Story title: {title}")
    print(f"🧪 Test file: {test_file}")
    print(f"📄 YAML file: {yaml_file}")

    tasks = extract_tasks_from_acceptance_criteria(acceptance_html)
    for i, task in enumerate(tasks, start=1):
        task["title"] = f"Task {i}: {task['title']}"
        task_id = create_task(task, story_id, headers_patch)
        print(f"✅ Created Task {task_id}: {task['title']}")

    test_case_id = create_test_case_with_steps(story_id, title, acceptance_html, headers_json, headers_patch)
    print(f"✅ Test case created and added to suite: {test_case_id}")

    generate_test_file(test_case_id, test_file)
    generate_yaml_file(test_case_id, title, clean_description, yaml_file)
    generate_page_object_file(title, test_file)

    print("\n🎉 All tasks complete!")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Error: {e}")
