import base64
import os
from collections import Counter

import requests

ORG = "Vizientinc"
PROJECT = "VizTech"
base_url = f"https://dev.azure.com/{ORG}/{PROJECT}/_apis"
TEST_PLAN_ID = 999999
TEST_RUN_ID = 99999
PAT = os.environ.get("HITL_ADO_PAT")
# Encode PAT with colon prefix
auth_str = f":{PAT}"
b64_auth = base64.b64encode(auth_str.encode()).decode()

HEADERS = {
    "Authorization": f"Basic {b64_auth}"
}


def get_test_results(run_id):
    url = f"{base_url}/test/runs/{run_id}/results?api-version=7.1-preview.6"
    response = requests.get(url, headers=HEADERS)
    print(f"Fetching results for Run ID {run_id} - Status Code:", response.status_code)
    if response.status_code != 200:
        print("Error:", response.text)
        return []
    return response.json()["value"]


def summarize_results(results):
    outcome_counts = Counter(result.get("outcome", "Unknown") for result in results)
    total = len(results)
    passed = outcome_counts.get("Passed", 0)
    failed = outcome_counts.get("Failed", 0)
    not_executed = outcome_counts.get("NotExecuted", 0)
    other = total - passed - failed - not_executed

    pass_percentage = round((passed / total) * 100, 2) if total else 0.0

    summary = {
        "Total": total,
        "Passed": passed,
        "Failed": failed,
        "NotExecuted": not_executed,
        "Other": other,
        "Pass %": pass_percentage,
    }

    return summary, outcome_counts


# Main logic for a single run
print(f"Fetching test results for Test Plan ID: {TEST_PLAN_ID}, Run ID: {TEST_RUN_ID}")
results = get_test_results(TEST_RUN_ID)

summary, outcomes = summarize_results(results)

# Print summary
print("\nTest Run Summary:")
for key, value in summary.items():
    print(f"  {key}: {value}")

# 🧪 Print detailed results
print("\nDetailed Test Results:")
for i, result in enumerate(results, start=1):
    test_name = result.get("automatedTestName") or result.get("testCaseTitle") or "Unnamed Test"
    outcome = result.get("outcome")
    print(f"  {i:02d}. {test_name} | Outcome: {outcome} | Run ID: {TEST_RUN_ID}")
