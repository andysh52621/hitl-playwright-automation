import base64
import os
import re
import textwrap

import requests

ORG_URL = "https://dev.azure.com/Vizientinc"
PROJECT = "VizTech"
PAT_ENV = "HITL_ADO_PAT"
API_VERSION = "7.1-preview.3"
STORY_ID = 1040714



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


def fetch_user_story(story_id, headers):
    url = f"{ORG_URL}/{PROJECT}/_apis/wit/workitems/{story_id}?$expand=all&api-version={API_VERSION}"
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    return r.json()


def prettify_task_line(line: str):
    line = re.sub(r'<[^>]+>', '', line).strip()
    line = re.sub(r'\s+', ' ', line)  # normalize whitespace
    title = line[:100].strip().capitalize()
    description = "\n".join(textwrap.wrap(line.strip(), width=90))
    return title, description


def extract_li_tasks(acceptance_criteria_html: str):
    li_items = re.findall(r"<li.*?>(.*?)</li>", acceptance_criteria_html, re.DOTALL | re.IGNORECASE)
    tasks = []
    for raw_line in li_items:
        title, desc = prettify_task_line(raw_line)
        tasks.append({
            "title": title if len(title) < 100 else title[:97] + "...",
            "description": desc
        })
    return tasks


def create_task_under_story(task, story_id, headers_patch):
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


def main():
    headers_json, headers_patch = get_auth_headers()
    story = fetch_user_story(STORY_ID, headers_json)
    acceptance_criteria = story.get("fields", {}).get("Microsoft.VSTS.Common.AcceptanceCriteria", "")
    print("📄 RAW ACCEPTANCE CRITERIA HTML:\n", acceptance_criteria[:500],
          "..." if len(acceptance_criteria) > 500 else "")

    tasks = extract_li_tasks(acceptance_criteria)
    if not tasks:
        print("❌ No <li> items found in acceptance criteria.")
        return
    print(f"📌 Creating {len(tasks)} tasks from <li> items in acceptance criteria.")
    for task in tasks:
        task_id = create_task_under_story(task, STORY_ID, headers_patch)
        print(f"✅ Created Task {task_id}: {task['title']}")


if __name__ == "__main__":
    main()
