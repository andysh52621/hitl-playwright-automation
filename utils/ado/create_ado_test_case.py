import base64
import os
import re

import requests


def fetch_user_story_details(org_url, project, story_id, headers_json):
    url = f"{org_url}/{project}/_apis/wit/workitems/{story_id}?$expand=all&api-version=7.1-preview.3"
    response = requests.get(url, headers=headers_json)
    response.raise_for_status()
    story = response.json()
    title = story.get("fields", {}).get("System.Title", f"Test Case for Story {story_id}")
    acceptance_html = story.get("fields", {}).get("Microsoft.VSTS.Common.AcceptanceCriteria", "")
    return title, acceptance_html


def extract_steps_from_html(acceptance_html):
    li_items = re.findall(r"<li.*?>(.*?)</li>", acceptance_html, re.DOTALL | re.IGNORECASE)
    steps = []
    for li in li_items:
        clean_line = re.sub(r"<.*?>", "", li).strip()
        if len(clean_line) >= 10:
            steps.append({
                "action": clean_line,
                "expected": "As per acceptance criteria"
            })
    return steps


def create_ado_test_case():
    org_url = "https://dev.azure.com/Vizientinc"
    project = "VizTech"
    plan_id = 979524
    suite_id = 1040029
    user_story_id = 1040714

    pat = os.getenv("HITL_ADO_PAT")
    if not pat:
        raise Exception("Environment variable 'HITL_ADO_PAT' is not set.")
    auth = base64.b64encode(f":{pat}".encode()).decode()
    headers_patch = {
        "Authorization": f"Basic {auth}",
        "Content-Type": "application/json-patch+json"
    }
    headers_json = {
        "Authorization": f"Basic {auth}",
        "Content-Type": "application/json"
    }

    # Fetch story details
    title, acceptance_html = fetch_user_story_details(org_url, project, user_story_id, headers_json)
    print(f"🔍 Creating test case based on story: {title}")

    # Create test case
    url_create = f"{org_url}/{project}/_apis/wit/workitems/$Test%20Case?api-version=7.1-preview.3"
    test_case_payload = [
        {"op": "add", "path": "/fields/System.Title", "value": title},
        {"op": "add", "path": "/relations/-", "value": {
            "rel": "System.LinkTypes.Hierarchy-Reverse",
            "url": f"{org_url}/{project}/_apis/wit/workItems/{user_story_id}",
            "attributes": {"comment": "Test case linked to story"}
        }}
    ]
    resp = requests.post(url_create, headers=headers_patch, json=test_case_payload)
    resp.raise_for_status()
    test_case_id = resp.json()["id"]
    print(f"✅ Created Test Case ID: {test_case_id}")

    # Extract and add test steps
    steps = extract_steps_from_html(acceptance_html)
    if not steps:
        print("⚠️ No <li> items found in acceptance criteria — no steps added.")
    else:
        steps_content = "<steps id='0'>"
        for i, step in enumerate(steps, 1):
            steps_content += f"""
            <step id='{i}' type='ActionStep'>
                <parameterizedString isformatted='true'>{step['action']}</parameterizedString>
                <parameterizedString isformatted='true'>{step['expected']}</parameterizedString>
                <outcome>None</outcome>
            </step>
            """
        steps_content += "</steps>"
        url_steps = f"{org_url}/{project}/_apis/wit/workitems/{test_case_id}?api-version=7.1-preview.3"
        steps_payload = [{"op": "add", "path": "/fields/Microsoft.VSTS.TCM.Steps", "value": steps_content}]
        r = requests.patch(url_steps, headers=headers_patch, json=steps_payload)
        r.raise_for_status()
        print("✅ Added dynamic test steps from acceptance criteria.")

    # Add to test suite
    url_add = f"{org_url}/{project}/_apis/test/Plans/{plan_id}/suites/{suite_id}/testcases/{test_case_id}?api-version=7.1-preview.3"
    r = requests.post(url_add, headers=headers_json)
    r.raise_for_status()
    print("✅ Added test case to regression suite.")


if __name__ == "__main__":
    create_ado_test_case()
