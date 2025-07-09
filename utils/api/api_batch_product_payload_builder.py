import time
from datetime import datetime


def build_batch_payload(test_meta, num_tasks):
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    transaction_id = int(time.time_ns() / 1_000)  # microsecond precision

    def create_task(task_index):
        return {
            "ProductKey": 100000 + task_index,
            "ProductBaseKey": "500157664",
            "NumberofProductsonBase": "15",
            "ProductTypeCode": "M",
            "VendorName": {
                "text": f"Task_Test_{task_index}",
                "value": "501k Recycling LLC"
            },
            "PrimaryCatalogNumber": "1169",
            "CatalogNumberStripped": "1169",
            "Description": f"Batch Good Product {now_str}",
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
            "user": {
                "ID": 0,
                "FirstName": "Andy",
                "LastName": "record level",
                "MiddleName": "A",
                "emailAddress": "andy.sharma@vizientinc.com"
            }
        }

    payload = {
        "transactionId": transaction_id,
        "eventTime": now_str,
        "eventDomain": test_meta.get("domain"),
        "eventType": test_meta.get("entity"),
        "eventName": "BulkTaskCreated",
        "user": {
            "id": 12345678,
            "firstName": "andy",
            "lastName": "bulkLevel",
            "middleName": "",
            "emailAddress": "andy.sharma@vizientinc.com"
        },
        "tasks": [create_task(i) for i in range(num_tasks)]
    }

    return payload
