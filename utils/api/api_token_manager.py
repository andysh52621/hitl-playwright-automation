import base64
from typing import Optional

import requests
from sqlalchemy.orm import Session

from db_engine.test_automation_engine import get_test_db_engine
from db_models.api_test_db_models import APIServiceConfig


def get_access_token(service_env) -> str:
    """
    Fetch access token using credentials stored in the API_Test_Service_Config table.
    """

    # Setup SQLAlchemy session
    engine = get_test_db_engine()
    with Session(engine) as session:
        # Get config for the matching environment
        config: Optional[APIServiceConfig] = (
            session.query(APIServiceConfig).filter(APIServiceConfig.service_env == service_env).first()
        )

        if not config:
            raise ValueError(f"No service config found for env: {service_env}")

        # Prepare request details
        url = f"https://{config.access_token_server}/{config.access_token_endpoint}"
        credentials = f"{config.client_id_service_account}:{config.client_secret_service_account}"
        base64_auth = base64.b64encode(credentials.encode()).decode()

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {base64_auth}",
            "Host": config.access_token_server,
            "SubscriptionKey": config.primary_subscription_key,
            "Scope": "apimuser"
        }

        data = {
            "grant_type": "client_credentials",
            "scope": "apimuser"
        }

        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        return response.json().get("access_token")


# Debug: run standalone
if __name__ == "__main__":
    try:
        token = get_access_token("prod")
        print(f"✅ Access Token: {token}")
    except Exception as e:
        print(f"❌ Failed to fetch token: {e}")
