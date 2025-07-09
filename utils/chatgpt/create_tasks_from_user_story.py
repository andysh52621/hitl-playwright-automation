import base64
import os

import requests
from openai import OpenAI

# --------- CONFIG ---------
ORG = "vizientinc"  # Your Azure DevOps organization
PROJECT = "MDM"  # Your ADO project
ADO_PAT = os.getenv("HITL_ADO_PAT")  # Must be set in env or .env
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Set in env or .env
ADO_API_URL = f"https://dev.azure.com/{ORG}/{PROJECT}/_apis"
HEADERS = {
    "Content-Type": "application/json-patch+json",  # ✅ REQUIRED for ADO PATCH/POST APIs
    "Authorization": f"Basic {base64.b64encode(f':{ADO_PAT}'.encode()).decode()}"
}
client = OpenAI(api_key=OPENAI_API_KEY)


# --------------------------


def get_user_story_details(story_id):
    url = f"{ADO_API_URL}/wit/workitems/{story_id}?api-version=7.0"
    response = requests.get(url, headers=HEADERS)

    print(f"🔍 Request URL: {url}")
    print(f"📦 Status code: {response.status_code}")

    if not response.ok:
        print("❌ Failed to fetch user story")
        print("Response Text:\n", response.text)
        response.raise_for_status()

    try:
        data = response.json()
    except Exception as e:
        print("❌ Could not parse JSON from response:")
        print(response.text)
        raise

    title = data['fields'].get('System.Title', '')
    description = data['fields'].get('System.Description', '')
    return title, description


def generate_tasks_from_story(story_id, story_title, description):
    return """
### Task 1: Implement Transaction Detection
Detect TransactionId from API_UI_Task_Mapping table where RequestType = 'batch' and Status in ('submitted', 'pending').

### Task 2: Calculate Batch Processing Time
Calculate the time difference in milliseconds between the earliest and latest Created_Date for that TransactionId in DM_QAProduct_Product.

### Task 3: Count Error Records
Check TM_Exception_Log for the number of errors related to the TransactionId.

### Task 4: Derive Batch Status
Set Status to Failed, Completed, or Pending based on presence of errors and timestamps.
"""


def create_child_task(parent_id, title, description):
    url = f"{ADO_API_URL}/wit/workitems/$Task?api-version=7.0"
    body = [
        {"op": "add", "path": "/fields/System.Title", "value": title},
        {"op": "add", "path": "/fields/System.Description", "value": description},
        {"op": "add", "path": "/relations/-", "value": {
            "rel": "System.LinkTypes.Hierarchy-Reverse",
            "url": f"https://dev.azure.com/{ORG}/_apis/wit/workItems/{parent_id}",
            "attributes": {"comment": "Auto-created child task"}
        }}
    ]
    response = requests.post(url, headers=HEADERS, json=body)

    if not response.ok:
        print("❌ ADO Task Creation Failed")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        response.raise_for_status()

    return response.json()["id"]


def parse_and_create_tasks(story_id, markdown_output):
    tasks = []
    lines = markdown_output.strip().split('\n')
    current_title = ""
    current_desc = ""
    for line in lines:
        if line.strip().startswith("### "):
            if current_title:
                tasks.append((current_title, current_desc.strip()))
            current_title = line.replace("###", "").strip()
            current_desc = ""
        elif line.strip().startswith("**Title:**"):
            current_title = line.split("**Title:**")[-1].strip()
        else:
            current_desc += line + "\n"
    if current_title:
        tasks.append((current_title, current_desc.strip()))

    for title, desc in tasks:
        task_id = create_child_task(story_id, title, desc)
        print(f"✅ Created task #{task_id}: {title}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate and add ADO tasks for a user story.")
    parser.add_argument("--story", type=int, required=True, help="User Story ID")
    args = parser.parse_args()

    title, description = get_user_story_details(args.story)
    task_markdown = generate_tasks_from_story(args.story, title, description)
    print("\n--- Generated Tasks ---\n")
    print(task_markdown)
    parse_and_create_tasks(args.story, task_markdown)
