# utils/ado/ado_test_plan_reader.py

import requests


def fetch_total_planned_cases(ado_runner):
    """
    Fetch total planned test cases for the suite from ADO test plan.
    """
    url = f"{ado_runner.org_url}/{ado_runner.project}/_apis/test/plans/{ado_runner.plan_id}/suites/{ado_runner.suite_id}/testcases?api-version=7.1"

    headers = {
        "Authorization": "Basic " + ado_runner.headers["Authorization"].split(" ")[1],
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    cases = response.json().get("value", [])
    return len(cases)
