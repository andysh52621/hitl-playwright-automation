import base64
from pathlib import Path

import yaml


def load_config():
    base_path = Path(__file__).resolve().parent.parent
    config_path = base_path / "api_config" / "settings.yaml"

    if not config_path.exists():
        raise FileNotFoundError(f"❌ settings.yaml not found at: {config_path}")

    config = yaml.safe_load(open(config_path))

    # Add computed/derived values
    env = config.get("ENV")
    env_config = config["environments"].get(env, {})
    config["env_config"] = env_config

    config["hitl_base_url"] = env_config.get("hitl_api_base_url")
    config["hitl_api_endpoint"] = env_config.get("hitl_api_endpoint")
    config[
        "apim_token_url"] = f"https://{env_config.get('access_token_server')}/{env_config.get('access_token_endpoint')}"

    # Base64 encode the Basic Auth credentials
    credentials = f"{env_config.get('client_id_service_account')}:{env_config.get('client_secret_service_account')}"
    config["base64_auth"] = base64.b64encode(credentials.encode()).decode()

    return config


if __name__ == "__main__":
    config = load_config()
    import pprint

    pprint.pprint(config)
