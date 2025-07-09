# utils/ado_test_step_reporter.py
import base64
import os
from datetime import datetime

import requests

from email_utility.email_util import hitlLogger


def generate_test_step_report_file(steps: list[dict], result_dir: str = "test_steps") -> str:
    os.makedirs(result_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = os.path.join(result_dir, f"test_steps_{timestamp}.txt")

    with open(file_path, "w", encoding="utf-8", errors="replace") as f:
        f.write("Test Execution Steps\n")
        f.write("====================\n")
        for i, step in enumerate(steps, 1):
            step_time = step.get("timestamp") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"Step {i}: {step['action']}\n")
            f.write(f"Expected: {step['expected']}\n")
            f.write(f"Result: {step['outcome']}\n")
            f.write(f"Timestamp: {step_time}\n")
            f.write("--------------------\n")

    return file_path


def attach_step_report_to_ado(file_path: str, run_id: int, result_id: int, org_url: str, project: str, pat: str):
    with open(file_path, "rb") as f:
        content_base64 = base64.b64encode(f.read()).decode("utf-8")

    url = f"{org_url}/{project}/_apis/test/Runs/{run_id}/Results/{result_id}/attachments?api-version=7.1"
    payload = {
        "stream": content_base64,
        "fileName": os.path.basename(file_path),
        "comment": "Test step execution report",
        "attachmentType": "GeneralAttachment"
    }

    headers = {
        "Authorization": "Basic " + base64.b64encode(f":{pat}".encode()).decode(),
        "Content-Type": "application/json"
    }

    r = requests.post(url, headers=headers, json=payload)
    r.raise_for_status()
    hitlLogger.info("✅ Test step report attached to ADO test result.")


def attach_and_upload_step_log(steps: list[dict], runner):
    """
    Generates a step log file and attaches it to ADO test result.
    """
    file_path = generate_test_step_report_file(steps)
    attach_step_report_to_ado(
        file_path=file_path,
        run_id=runner.run_id,
        result_id=runner.result_id,
        org_url=runner.org_url,
        project=runner.project,
        pat=runner.pat
    )
