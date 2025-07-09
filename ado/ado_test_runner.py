import base64
import logging
import os
import platform
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import requests
from requests.auth import HTTPBasicAuth

from utils.ado.ado_test_step_reporter import attach_and_upload_step_log

MAX_COMMENT_LENGTH = 2048  # ADO limit for comments
hitlLogger = logging.getLogger("HitlLogger")


class ADOTestRunner:
    def __init__(self, test_meta: dict):
        self.suite_type = os.getenv("SUITE_TYPE").lower()
        self.build_definition_id = test_meta.get("build_definition_id")
        self.test_env = test_meta.get("test_env")
        self.plan_id = test_meta.get("ado_plan_id")
        self.suite_id = test_meta.get("ado_suite_id")
        self.case_id = test_meta.get("ado_case_id")
        self.org_url = test_meta.get("ado_org_url").rstrip("/")
        self.project = test_meta.get("ado_project")
        self.pat = os.getenv("HITL_ADO_PAT")
        self.is_pipeline = os.environ.get("IS_PIPELINE")
        self.run_id = None
        self.result_id = None
        self.result_id_map = {}
        self.all_test_case_ids = []
        self.finalized_case_ids = set()
        self.case_outcomes = {}  # NEW: Track final outcome per case
        self.executed_test_count = 0
        self.passed_test_count = 0
        self.failed_test_count = 0
        self.skipped_test_count = 0
        self.headers = {
            "Authorization": "Basic " + base64.b64encode(f":{self.pat}".encode()).decode(),
            "Content-Type": "application/json"
        }

    def finalize_result(self, case_id: str, outcome: str, comment: str, steps: list = None, page=None, start_time=None):
        if not start_time:
            start_time = datetime.now(timezone.utc)
        elif start_time.tzinfo is None:
            start_time = start_time.replace(tzinfo=timezone.utc)
        end_time = datetime.now(timezone.utc)
        duration_ms = int((end_time - start_time).total_seconds() * 1000)

        self.set_result_id_for_case(case_id)
        self.patch_result(outcome, comment[:MAX_COMMENT_LENGTH])
        self.patch_test_result_metadata(
            duration_in_ms=duration_ms,
            computer_name=self.get_computer_name(),
            error_message=comment if outcome.lower() == "failed" else None
        )
        if outcome.lower() == "failed" and page:
            self.take_screen_shot(page, f"{case_id}_failure")
        if steps:
            self.add_test_steps(steps)
            attach_and_upload_step_log(steps, self)

        if str(case_id) not in self.finalized_case_ids:
            self.executed_test_count += 1
            if outcome.lower() == "passed":
                self.passed_test_count += 1
            elif outcome.lower() == "failed":
                self.failed_test_count += 1
            elif outcome.lower() == "skipped":
                self.skipped_test_count += 1

        self.finalized_case_ids.add(str(case_id))  # ✅ Only mark it finalized once

        self.case_outcomes[str(case_id)] = outcome  # Track final outcome

    def complete_run(self, summary: str = "Test execution completed."):
        self.mark_remaining_tests_not_run()
        run_url = f"{self.org_url}/{self.project}/_apis/test/runs/{self.run_id}?api-version=7.1"
        run_resp = requests.get(run_url, headers=self.headers)
        run_resp.raise_for_status()
        existing_comment = run_resp.json().get("comment", "")
        final_comment = existing_comment + summary
        payload = {
            "state": "Completed",
            "comment": final_comment[:MAX_COMMENT_LENGTH]
        }
        url = f"{self.org_url}/{self.project}/_apis/test/runs/{self.run_id}?api-version=7.1"
        r = requests.patch(url, headers=self.headers, json=payload)
        r.raise_for_status()
        hitlLogger.info("✅ Test run marked as completed with preserved comment.")

    def mark_remaining_tests_not_run(self):
        not_run_cases = set(self.all_test_case_ids) - self.finalized_case_ids
        if not not_run_cases:
            return
        hitlLogger.info(f"⚠️ Marking {len(not_run_cases)} test cases as NotRun...")
        payload = []
        for case_id in not_run_cases:
            result_id = self.result_id_map.get(case_id)
            if not result_id:
                hitlLogger.info(f"⚠️ Skipping unmapped test_case_id: {case_id}")
                continue
            payload.append({
                "id": result_id,
                "outcome": "NotExecuted",
                "state": "Completed",
                "comment": "Test was not executed during automation run.",
                "automatedTestName": f"TestCase_{case_id}",
                "automatedTestType": "PlaywrightTest",
                "automatedTestStorage": "playwright.automation"
            })
        if not payload:
            hitlLogger.info("⚠️ No eligible test results to mark as NotRun.")
            return
        url = f"{self.org_url}/{self.project}/_apis/test/runs/{self.run_id}/results?api-version=7.1"
        r = requests.patch(url, headers=self.headers, json=payload)
        try:
            r.raise_for_status()
            hitlLogger.info(f"✅ Marked {len(payload)} test case(s) as NotRun.")
            self.skipped_test_count += len(payload)
        except requests.exceptions.HTTPError as e:
            hitlLogger.info(f"❌ Failed to patch NotRun results: {e}")
            hitlLogger.info(f"🔍 Response content: {r.text}")

    def start_test_run(self):
        """
        Start a new test run in Azure DevOps.
        """
        # Get test plan and suite names for the run title
        plan_name = self.get_plan_name()
        suite_name = self.get_suite_name()
        point_ids = self.get_all_point_ids()

        # Get build information
        build_id = self.get_latest_successful_build_number()
        build_info = self.get_build_details(str(build_id))

        # Get test case owners
        test_case_owners = self.get_test_case_owners()

        # Metadata for comments
        comment = (
            f"🧱 Release: {build_info.get('buildNumber')} | "
            f"🔀 Stage: {build_info.get('sourceBranch', '').split('/')[-1]} | "
            f"🖥️ Platform: {build_info.get('queue', {}).get('name', 'ubuntu-latest')} | "
            f"🏗️ Flavor: {build_info.get('repository', {}).get('type', 'CI')} | "
            f"🧪 TestSettings: HITL-Automation | "
            f"🧪 Env: {self.test_env}"
        )

        # Create test run
        url = f"{self.org_url}/{self.project}/_apis/test/runs?api-version=7.1"
        payload = {
            "name": f"{plan_name} - {self.suite_type.capitalize()} "
                    f"({self.is_pipeline}-{self.test_env.capitalize()}) "
                    f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "plan": {"id": self.plan_id},
            "pointIds": point_ids,
            "automated": True,
            "state": "InProgress",
            "build": {"id": build_id},
            "comment": comment
        }

        r = requests.post(url, headers=self.headers, json=payload)
        r.raise_for_status()
        self.run_id = r.json()["id"]
        hitlLogger.info(f"✅ Created test run with ID: {self.run_id}")

        # Map result IDs for each test case
        self.map_result_ids_from_run()
        
        # Update test case assignments to match test plan
        self.update_test_case_assignments(test_case_owners)

        # Update run metadata with configuration
        self.update_run_metadata(
            release=build_info.get("buildNumber"),
            release_stage=build_info.get("sourceBranch", "").split("/")[-1],
            build_platform=build_info.get("queue", {}).get("name", "ubuntu-latest"),
            build_flavor=build_info.get("repository", {}).get("type", "CI"),
            test_settings="HITL-Automation",
            lab_environment=build_info.get("queue", {}).get("name", "ubuntu-latest")
        )

    def map_result_ids_from_run(self):
        url = f"{self.org_url}/{self.project}/_apis/test/runs/{self.run_id}/results?api-version=7.1"
        r = requests.get(url, headers=self.headers)
        r.raise_for_status()
        results = r.json().get("value", [])
        for result in results:
            test_case_id = str(result["testCase"]["id"])
            result_id = result["id"]
            self.result_id_map[test_case_id] = result_id
            hitlLogger.info(f"✅ Mapped existing result_id {result_id} to test_case_id {test_case_id}")
        self.all_test_case_ids = list(self.result_id_map.keys())

    def get_plan_name(self):
        url = f"{self.org_url}/{self.project}/_apis/test/plans/{self.plan_id}"
        r = requests.get(url, headers=self.headers)
        r.raise_for_status()
        return r.json().get("name", "UnknownPlan")

    def get_suite_name(self):
        url = f"{self.org_url}/{self.project}/_apis/test/plans/{self.plan_id}/suites/{self.suite_id}"
        r = requests.get(url, headers=self.headers)
        r.raise_for_status()
        return r.json().get("name", "UnknownSuite")

    def get_all_point_ids(self):
        url = f"{self.org_url}/{self.project}/_apis/test/plans/{self.plan_id}/suites/{self.suite_id}/points?api-version=7.1"
        r = requests.get(url, headers=self.headers)
        r.raise_for_status()
        return [pt["id"] for pt in r.json().get("value", [])]

    def get_test_case_owners(self):
        """
        Fetch test case owners from the test plan.
        Returns a dictionary mapping test case IDs to their assigned owners.
        """
        url = f"{self.org_url}/{self.project}/_apis/test/plans/{self.plan_id}/suites/{self.suite_id}/points?api-version=7.1"
        r = requests.get(url, headers=self.headers)
        r.raise_for_status()
        points = r.json().get("value", [])
        
        owners = {}
        for point in points:
            test_case = point.get("testCase", {})
            test_case_id = str(test_case.get("id"))
            assigned_to = point.get("assignedTo", {}).get("displayName", "")
            
            # Clean up the display name - remove GUID and email
            if assigned_to:
                # Extract just the name part before any < character
                clean_name = assigned_to.split("<")[0].strip()
                owners[test_case_id] = clean_name
                hitlLogger.info(f"📋 Test case {test_case_id} is assigned to {clean_name}")
            else:
                hitlLogger.info(f"⚠️ No owner found for test case {test_case_id}")
        
        return owners

    def set_result_id_for_case(self, case_id):
        self.case_id = case_id
        self.result_id = self.result_id_map.get(str(case_id))
        hitlLogger.info(f"✅ Mapped result_id {self.result_id} for test_case_id {case_id}")

    def patch_result(self, outcome: str, comment: str):
        url = f"{self.org_url}/{self.project}/_apis/test/runs/{self.run_id}/results?api-version=7.0"
        payload = [{
            "id": self.result_id,
            "outcome": outcome,
            "state": "Completed",
            "comment": comment,
            "automatedTestName": f"TestCase_{self.case_id}",
            "automatedTestType": "PlaywrightTest",
            "automatedTestStorage": "playwright.automation"
        }]
        r = requests.patch(url, headers=self.headers, json=payload)
        r.raise_for_status()

    def add_test_steps(self, steps: list):
        steps_html = "<steps id='0'>"
        for idx, step in enumerate(steps, start=1):
            steps_html += (
                f"<step id='{idx}' type='ActionStep'>"
                f"<parameterizedString isformatted='true'>{step.get('action')}</parameterizedString>"
                f"<parameterizedString isformatted='true'>{step.get('expected')}</parameterizedString>"
                f"<outcome>{step.get('outcome')}</outcome>"
                f"</step>"
            )
        steps_html += "</steps>"

        payload = [{
            "id": self.result_id,
            "iterationDetails": [{"steps": steps_html}]
        }]
        url = f"{self.org_url}/{self.project}/_apis/test/runs/{self.run_id}/results?api-version=7.1"
        r = requests.patch(url, headers=self.headers, json=payload)
        r.raise_for_status()

    def take_screen_shot(self, page, base_filename):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{base_filename}_{timestamp}.png"
            screenshots_dir = os.path.join(os.getcwd(), "screenshots")
            os.makedirs(screenshots_dir, exist_ok=True)
            screenshot_path = os.path.join(screenshots_dir, filename)
            page.screenshot(path=screenshot_path, full_page=False)
            self.attach_file(screenshot_path, "Failure screenshot")
        except Exception as e:
            hitlLogger.info(f"❌ Screenshot capture failed: {e}")

    def attach_video(self, file_path: str, comment: str):
        if not os.path.exists(file_path):
            hitlLogger.info(f"⚠️ File does not exist: {file_path}")
            return
        with open(file_path, "rb") as f:
            content = base64.b64encode(f.read()).decode("utf-8")
        url = f"{self.org_url}/{self.project}/_apis/test/Runs/{self.run_id}/Results/{self.result_id}/attachments?api-version=7.1"
        payload = {
            "stream": content,
            "fileName": os.path.basename(file_path),
            "comment": comment,
            "attachmentType": "GeneralAttachment"  # ✅ Use this for all file types
        }
        r = requests.post(url, headers=self.headers, json=payload)
        r.raise_for_status()

    def attach_file(self, file_path: str, comment: str):
        if not os.path.exists(file_path):
            hitlLogger.info(f"⚠️ File does not exist: {file_path}")
            return
        with open(file_path, "rb") as f:
            content = base64.b64encode(f.read()).decode("utf-8")
        url = f"{self.org_url}/{self.project}/_apis/test/Runs/{self.run_id}/Results/{self.result_id}/attachments?api-version=7.1"
        payload = {
            "stream": content,
            "fileName": os.path.basename(file_path),
            "comment": comment,
            "attachmentType": "GeneralAttachment"
        }
        r = requests.post(url, headers=self.headers, json=payload)
        r.raise_for_status()

    def attach_to_run(self, file_path: str, comment: str = "HITL Run summary") -> None:
        with open(file_path, "rb") as f:
            content = base64.b64encode(f.read()).decode("utf-8")
        url = f"{self.org_url}/{self.project}/_apis/test/runs/{self.run_id}/attachments?api-version=7.1"
        payload = {
            "stream": content,
            "fileName": os.path.basename(file_path),
            "comment": comment,
            "attachmentType": "GeneralAttachment"
        }
        r = requests.post(url, headers=self.headers, json=payload)
        r.raise_for_status()
        hitlLogger.info(f"✅ Summary attached at RUN level: {file_path}")

    def get_latest_successful_build_number(self) -> str:

        url = f"https://dev.azure.com/Vizientinc/VizTech/_apis/build/builds"
        params = {
            "definitions": self.build_definition_id,
            "statusFilter": "completed",
            "resultFilter": "succeeded",
            "$top": 1,
            "api-version": "7.1-preview.7"
        }

        response = requests.get(
            url,
            params=params,
            auth=HTTPBasicAuth('', self.pat)
        )

        if response.status_code != 200:
            raise Exception(f"Failed to get builds: {response.status_code} - {response.text}")

        builds = response.json().get("value", [])
        if not builds:
            raise Exception("No successful builds found.")

        return builds[0]["id"]

    def get_build_details(self, build_id: str) -> dict:
        """
        Fetch extended build details from Azure DevOps based on a build ID.
        """
        url = f"{self.org_url}/{self.project}/_apis/build/builds/{build_id}?api-version=7.1-preview.7"
        r = requests.get(url, headers=self.headers, auth=HTTPBasicAuth('', self.pat))
        r.raise_for_status()
        return r.json()

    def update_run_metadata(self,
                            release: str = None,
                            release_stage: str = None,
                            build_platform: str = None,
                            build_flavor: str = None,
                            test_settings: str = "Default",
                            lab_environment: str = None):
        payload = {}

        if release is not None:
            payload["release"] = release
        if release_stage is not None:
            payload["releaseStage"] = release_stage
        if build_platform is not None:
            payload["buildPlatform"] = build_platform
        if build_flavor is not None:
            payload["buildFlavor"] = build_flavor
        if test_settings is not None:
            payload["testSettings"] = test_settings
        if lab_environment is not None:
            payload["mtmlabEnvironment"] = lab_environment

        if not payload:
            hitlLogger.info("⚠️ No metadata provided to update.")
            return

        url = f"{self.org_url}/{self.project}/_apis/test/runs/{self.run_id}?api-version=5.1-preview.3"
        r = requests.patch(url, headers=self.headers, json=payload)
        try:
            r.raise_for_status()
            hitlLogger.info("✅ ADO test run metadata updated.")
        except requests.exceptions.HTTPError as e:
            hitlLogger.info(f"❌ Failed to update run metadata: {e}")
            hitlLogger.info(f"🔍 Response: {r.text}")

    def patch_test_result_metadata(self, duration_in_ms=0, computer_name=None, error_message=None):
        if not self.result_id:
            hitlLogger.info("⚠️ No result_id to patch result metadata.")
            return

        payload = [{
            "id": self.result_id,
            "durationInMs": duration_in_ms,
            "computerName": computer_name,
            "errorMessage": error_message
        }]

        url = f"{self.org_url}/{self.project}/_apis/test/runs/{self.run_id}/results?api-version=7.1"
        r = requests.patch(url, headers=self.headers, json=payload)
        try:
            r.raise_for_status()
            hitlLogger.info(f"✅ Patched test result metadata for result_id {self.result_id}")
        except requests.exceptions.HTTPError as e:
            hitlLogger.info(f"❌ Failed to patch test result metadata: {e}")
            hitlLogger.info(f"🔍 Response: {r.text}")

    def get_computer_name(self) -> str:
        return (
                os.getenv("COMPUTERNAME") or
                os.getenv("HOSTNAME") or
                (os.uname().nodename if hasattr(os, "uname") else "UnknownHost")
        )

    def get_dynamic_configuration_name(self):
        run_env = os.getenv("RUN_ENV", "local").lower()
        os_name = platform.system()
        return f"{run_env.capitalize()}-{os_name}"

    def create_or_update_test_configuration(self, name: str, description: str = "", state: str = "active",
                                            values: list = None):
        url = f"{self.org_url}/{self.project}/_apis/test/configurations?api-version=5"
        payload = {
            "name": name,
            "description": description,
            "state": state,
            "values": values or []
        }
        r = requests.post(url, headers=self.headers, json=payload)
        try:
            r.raise_for_status()
            config_id = r.json()["id"]
            hitlLogger.info(f"✅ Test configuration '{name}' created (ID: {config_id})")
            return config_id
        except requests.exceptions.HTTPError as e:
            hitlLogger.info(f"❌ Failed to create test configuration: {e}")
            hitlLogger.info(f"🔍 Response: {r.text}")
            return None

    def assign_configuration_to_suite_cases(self, configuration_id: int):
        url = f"{self.org_url}/{self.project}/_apis/test/plans/{self.plan_id}/suites/{self.suite_id}/points?api-version=7.1-preview.2"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        points = response.json().get("value", [])

        if not points:
            hitlLogger.info("⚠️ No test points found to assign configuration.")
            return

        payload = [{"id": pt["id"], "configuration": {"id": configuration_id}} for pt in points]

        r = requests.patch(url, headers=self.headers, json=payload)
        try:
            r.raise_for_status()
            hitlLogger.info(f"✅ Assigned configuration ID {configuration_id} to {len(payload)} test point(s).")
        except requests.exceptions.HTTPError as e:
            hitlLogger.info(f"❌ Failed to assign configuration: {e}")
            hitlLogger.info(f"🔍 Response: {r.text}")

    def update_test_case_assignments(self, test_case_owners):
        """
        Update test case assignments in the test run to match the test plan.
        """
        if not test_case_owners:
            hitlLogger.info("⚠️ No test case owners found to update")
            return

        # First, get all test results from the run
        url = f"{self.org_url}/{self.project}/_apis/test/runs/{self.run_id}/results?api-version=7.1"
        r = requests.get(url, headers=self.headers)
        r.raise_for_status()
        results = r.json().get("value", [])

        # Prepare updates for each test case
        updates = []
        for result in results:
            test_case_id = str(result.get("testCase", {}).get("id"))
            if test_case_id in test_case_owners:
                owner_name = test_case_owners[test_case_id]
                updates.append({
                    "id": result["id"],
                    "owner": {
                        "displayName": owner_name
                    }
                })
                hitlLogger.info(f"✏️ Setting owner for test case {test_case_id} to {owner_name}")

        if updates:
            # Update test case assignments in batches of 100
            for i in range(0, len(updates), 100):
                batch = updates[i:i + 100]
                r = requests.patch(url, headers=self.headers, json=batch)
                r.raise_for_status()
                hitlLogger.info(f"✅ Updated {len(batch)} test case assignments in the run (batch {i//100 + 1})")
        else:
            hitlLogger.info("⚠️ No test case assignments to update")
