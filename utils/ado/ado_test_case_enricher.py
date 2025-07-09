# utils/ado_testcase_enricher.py
import base64
import os

import requests


def enrich_yaml_with_ado_test_case(meta: dict) -> dict:
    org_url = meta.get("ado_org_url", "").rstrip("/")
    project = meta.get("ado_project")
    plan_id = meta.get("ado_plan_id")
    suite_id = meta.get("ado_suite_id")
    case_id = meta.get("ado_case_id")
    pat = os.getenv("HITL_ADO_PAT")

    if not all([org_url, project, plan_id, suite_id, case_id, pat]):
        raise ValueError("Missing ADO credentials or identifiers in metadata")

    headers = {
        "Authorization": "Basic " + base64.b64encode(f":{pat}".encode()).decode(),
        "Content-Type": "application/json"
    }

    # Fetch test case info
    url = f"{org_url}/{project}/_apis/test/plans/{plan_id}/suites/{suite_id}/testcases/{case_id}?api-version=7.1-preview.3"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    test_case = response.json()

    # Inject useful fields
    meta["ado_case_title"] = test_case.get("testCase", {}).get("name")
    meta["ado_case_url"] = test_case.get("url")
    return meta
