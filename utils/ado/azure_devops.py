import os

import requests
from requests.auth import HTTPBasicAuth


def get_latest_successful_build_number(
        organization: str,
        project: str,
        definition_id: int,
        pat_token: str
) -> str:
    url = f"https://dev.azure.com/{organization}/{project}/_apis/build/builds"
    params = {
        "definitions": definition_id,
        "statusFilter": "completed",
        "resultFilter": "succeeded",
        "$top": 1,
        "api-version": "7.1-preview.7"
    }

    response = requests.get(
        url,
        params=params,
        auth=HTTPBasicAuth('', pat_token)
    )

    if response.status_code != 200:
        raise Exception(f"Failed to get builds: {response.status_code} - {response.text}")

    builds = response.json().get("value", [])
    if not builds:
        raise Exception("No successful builds found.")

    return builds[0]["buildNumber"]


# Example usage
if __name__ == "__main__":
    ORG = "Vizientinc"
    PROJECT = "VizTech"
    DEFINITION_ID = 3499
    PAT_TOKEN = os.getenv("HITL_ADO_PAT")

    build_number = get_latest_successful_build_number(ORG, PROJECT, DEFINITION_ID, PAT_TOKEN)
    print(f"Latest successful build number: {build_number}")
