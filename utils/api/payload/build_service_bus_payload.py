from datetime import datetime


def build_service_bus_payload(index: int, meta: dict) -> dict:
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {
        "ProductKey": 164756 + index,
        "ProductBaseKey": "500157664",
        "NumberofProductsonBase": "15",
        "ProductTypeCode": "M",
        "VendorName": {"text": "JMeter_Test", "value": 863427},
        "PrimaryCatalogNumber": "1169",
        "CatalogNumberStripped": "1169",
        "Description": f"TX106_{index}",
        "DescriptionException": "False",
        "ProductSpendCategory": "Traditional Wound Care",
        "UNSPSCCommodityCode": "42311545.0",
        "UNSPSCCommodity": "Non adhesive dry bandages or dressings",
        "SyncCode": "PCWCT08a4",
        "SyncCodeSubCategory": "Non-Adhesive Dressing, Non-Adherent, Standard",
        "HCPCSIndicator": "True",
        "ProductComment": f"Auto-{index}",
        "ItemTypeIsValidated": "I",
        "CoNamePartNumIsValidated": "I",
        "UNSPSCIsValidated": "I",
        "DeleteIndicator": "False",
        "DeleteReason": None,
        "ReplacedByProductKey": None,
        "CreateUser": "PDM",
        "CreateTimestamp": now_str,
        "LastUpdateUser": "automation",
        "LastUpdateTimestamp": now_str,
        "PSCIsValidated": "I",
        "transactionId": int(datetime.now().timestamp() * 1000) + index,
        "eventDomain": meta.get("domain"),
        "eventType": meta.get("entity"),
        "eventName": "TaskCreated",
        "user": {
            "ID": 0,
            "FirstName": "JMeter",
            "LastName": "Automation",
            "emailAddress": "andy.sharma@vizientinc.com"
        }
    }
