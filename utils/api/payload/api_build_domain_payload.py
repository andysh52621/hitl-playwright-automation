def build_domain_payload(unique_domain_name, isActive):
    payload = {
        "name": unique_domain_name,
        "shortDesc": unique_domain_name,
        "contactEmail": "andy.sharma@vizientinc.com",
        "description": "Test Domain created by API test",
        "createdBy": "andy.sharma@vizientinc.com",
        "isActive": isActive
    }
    return payload
