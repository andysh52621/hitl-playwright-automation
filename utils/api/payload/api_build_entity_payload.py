def build_entity_payload(unique_domain_name, isActive):
    payload = {
        "name": "payload",
        "shortDesc": "payload",
        "description": "payload",
        "domainName": unique_domain_name,
        "contactEmails": "aa@aa.com",
        "notificationFlag": True,
        "navigationFlag": True,
        "globalClientId": "",
        "globalClientSecret": "",
        "isActive": isActive,
        "isSearchEnabled": True,
        "dataSchema": {
            "type": "object",
            "properties": {
                "firstName": {
                    "type": "string",
                    "minLength": 3,
                    "description": "Please enter your name"
                },
                "lastName": {
                    "type": "string",
                    "minLength": 3,
                    "description": "Please enter your last name"
                },
                "nationality": {
                    "type": "string",
                    "enum": [
                        "DE",
                        "IT",
                        "JP",
                        "US",
                        "RU",
                        "Other"
                    ]
                },
                "age": {
                    "type": "number",
                    "description": "Please enter your age"
                },
                "developer": {
                    "type": "boolean"
                }
            },
            "required": []
        },
        "formSchema": {
            "type": "VerticalLayout",
            "elements": [
                {
                    "type": "HorizontalLayout",
                    "elements": [
                        {
                            "type": "Control",
                            "scope": "#/properties/firstName"
                        },
                        {
                            "type": "Control",
                            "scope": "#/properties/lastName"
                        },
                        {
                            "type": "Control",
                            "scope": "#/properties/age"
                        },
                        {
                            "type": "Control",
                            "scope": "#/properties/nationality"
                        },
                        {
                            "type": "Control",
                            "scope": "#/properties/developer"
                        }
                    ]
                }
            ]
        },
        "gridSchema": {
            "columns": [
                {
                    "name": "firstName",
                    "label": "First Name"
                },
                {
                    "name": "lastName",
                    "label": "Last Name"
                },
                {
                    "name": "age",
                    "label": "Age"
                },
                {
                    "name": "developer",
                    "label": "Developer"
                }
            ]
        },
        "actionSchema": None,
        "searchSchema": None,
        "createdBy": "adminxref@vizientinc.com",
        "user": {
            "email": "adminxref@vizientinc.com",
            "userGuid": "08a84773-11c3-4b67-a8bd-52b91b5e1cc5",
            "role": "Admin"
        }
    }

    return payload
