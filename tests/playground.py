test = f'''
{{
    "Struct_list": [
        {{
            "struct_name": "Message Header",
            "value": [
                128,
                16,
                8
            ],
            "fieldname": [
                "Marker",
                "Length",
                "Type"
            ]
        }}
    ],
    "Value_list": {{
        "Type": {{
            "OPEN": "1",
            "UPDATE": "2",
            "NOTIFICATION": "3",
            "KEEPALIVE": "4"
        }}
    }}
}}
'''
print(test)