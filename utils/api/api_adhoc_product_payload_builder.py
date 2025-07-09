import threading
import time
from datetime import datetime


def build_product_payload(test_meta):
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    transaction_id = int(time.time() * 1000_000) + threading.get_ident()

    payload = {
        "ProductKey": 164756,
        "ProductBaseKey": "500157664",
        "NumberofProductsonBase": "15",
        "ProductTypeCode": "M",
        "VendorName": {
            "text": "JMeter_Test",
            "value": "501k Recycling LLC"
        },
        "PrimaryCatalogNumber": "1169",
        "CatalogNumberStripped": "1169",
        "Description": f"Adhoc Good Product {now_str}",
        "DescriptionException": "False",
        "ProductSpendCategory": "Traditional Wound Care",
        "UNSPSCCommodityCode": "42311545.0",
        "UNSPSCCommodity": "Non adhesive dry bandages or dressings",
        "SyncCode": "PCWCT08a4",
        "SyncCodeSubCategory": "Non-Adhesive Dressing, Non-Adherent, Standard",
        "HCPCSIndicator": "True",
        "ProductComment": "Cardinal Branded Product [072023 ysc] [ND to PK: 1000009672(D)]",
        "ItemTypeIsValidated": "I",
        "CoNamePartNumIsValidated": "I",
        "UNSPSCIsValidated": "I",
        "DeleteIndicator": "False",
        "DeleteReason": None,
        "ReplacedByProductKey": None,
        "CreateUser": "PDM",
        "CreateTimestamp": now_str,
        "LastUpdateUser": "jMeter-QAtestUSer",
        "LastUpdateTimestamp": now_str,
        "PSCIsValidated": "I",
        "transactionId": transaction_id,
        "eventTime": now_str,
        "eventDomain": test_meta.get("domain"),
        "eventType": test_meta.get("entity"),
        "eventName": "TaskCreated",
        "user": {
            "ID": 0,
            "FirstName": "JMeter",
            "LastName": "DataGen",
            "MiddleName": "A",
            "emailAddress": "andy.sharma@vizientinc.com"
        }
    }

    return payload
