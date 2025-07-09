import base64
import hashlib
import hmac
import time
import urllib.parse


def encode_uri_component(value: str) -> str:
    """
    Encodes a URI component like JavaScript's encodeURIComponent.
    """
    return urllib.parse.quote(value, safe='').replace('+', '%20')


def generate_sas_token(uri: str, key_name: str, key: str, expiry_in_seconds: int = 3600) -> str:
    """
    Generates a Shared Access Signature (SAS) token for Azure Service Bus.
    Args:
        uri (str): Full Service Bus URI (e.g., https://namespace.servicebus.windows.net/queue)
        key_name (str): The shared access policy name (e.g., RootManageSharedAccessKey)
        key (str): The shared access key string
        expiry_in_seconds (int): Token validity in seconds (default 1 hour)

    Returns:
        str: Fully constructed SAS token string
    """
    expiry = int(time.time()) + expiry_in_seconds
    string_to_sign = f"{encode_uri_component(uri)}\n{expiry}"

    hmac_sha256 = hmac.new(
        key=key.encode('utf-8'),
        msg=string_to_sign.encode('utf-8'),
        digestmod=hashlib.sha256
    )
    signature = base64.b64encode(hmac_sha256.digest()).decode('utf-8')

    return (
        f"SharedAccessSignature sr={encode_uri_component(uri)}"
        f"&sig={encode_uri_component(signature)}"
        f"&se={expiry}&skn={key_name}"
    ) 