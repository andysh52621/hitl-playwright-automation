import logging
import os
from dataclasses import dataclass
from typing import Optional

import pandas as pd

from utils.generic.get_project_root import get_project_root

hitlLogger = logging.getLogger("HitlLogger")


@dataclass
class UserConfig:
    is_active: bool
    test_env: str
    test_application: str
    test_url: str
    user: str
    user_id: str
    password: str
    browser_type: str


def load_user_config_from_excel(file_path: str) -> Optional[UserConfig]:
    try:
        hitlLogger.log(1, f"📁 Loading config from: {file_path}")
        df = pd.read_excel(file_path)

        # Check if we're running in pipeline mode
        is_pipeline = os.environ.get('IS_PIPELINE')

        hitlLogger.info(f"✅  IS_PIPELINE: {os.getenv('IS_PIPELINE')}")
        hitlLogger.info(f"✅  RUN_ENV: {os.getenv('RUN_ENV')}")

        if is_pipeline == "cicd":
            hitlLogger.info("🔄 Running in pipeline mode")

            # Get RUN_ENV to determine which environment to use
            run_env = os.environ.get('RUN_ENV')
            if not run_env:
                hitlLogger.error("❌ Pipeline mode requires RUN_ENV to be set")
                return None

            hitlLogger.info(f"🌐 Using environment: {run_env}")

            # Filter rows that match the RUN_ENV value in testEnv column
            matching_env_rows = df[df["testEnv"] == run_env]

            if matching_env_rows.empty:
                hitlLogger.warning(f"⚠️ No configuration found for environment: {run_env}")
                return None

            # Take the first row that matches the environment
            row = matching_env_rows.iloc[0]
            hitlLogger.info(f"✅ Selected configuration for environment: {run_env}, user: {row['user']}")

        else:
            hitlLogger.info("🖥️ Running in local mode")

            # In local mode, filter for active rows
            active_rows = df[df["isActive"] == True]

            if active_rows.empty:
                hitlLogger.warning("⚠️ No active configuration found in the Excel file.")
                return None

            # Take the first active row
            row = active_rows.iloc[0]
            # print(row.to_dict())
            hitlLogger.info(f"✅  Selected active for user: {row.to_string()}")

        return UserConfig(
            is_active=bool(row["isActive"]),
            test_env=str(row["testEnv"]),
            test_application=str(row["testApplication"]),
            test_url=str(row["testUrl"]),
            user=str(row["user"]),
            user_id=str(row["userId"]),
            password=str(row["password"]),
            browser_type=str(row["browserType"]),
        )

    except Exception as e:
        hitlLogger.error(f"❌ Failed to load user config: {e}")
        return None


if __name__ == "__main__":
    BASE_DIR = None

    if os.system == "Windows":
        BASE_DIR = get_project_root()
        print("Running on Windows")
    elif os.system == "Linux" or os.getenv("WORK_DIR") == "/app":
        BASE_DIR = os.getenv("WORK_DIR", "/app")
        print("Running on Linux")
    else:
        print(f"Running on: {os.system}")
    excel_path = os.path.join(BASE_DIR, "user-config", "test_user_config.xlsx")
    user_config = load_user_config_from_excel(excel_path)
