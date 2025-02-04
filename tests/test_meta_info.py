import path_setup
import json

from src.utils import extract_meta_info, merge_meta_info
from src.configs.common_configs import PathConfig

location = PathConfig().data
log_dir = "rfc4271_deepseek-r1_32b_2025_02_03_19_56_36"
log_name = "meta-info_rfc4271_prompt-4271-mti-1_query-3.txt"
log_path = location / log_dir / log_name
raw_info = extract_meta_info(log_path)

for info in raw_info:
    print(info)

# json_info = merge_meta_info(raw_info)

# output = json.dumps(json_info, indent=4)
# print(output)

# print(f"一共有{len(meta_info)}个规则")

# for info in meta_info:
#     print(info)

# print(meta_info[1])

# mti1 = f'''
# {{
#     "Struct_list": {{
#         "struct_name": "Message Header",
#         "value": [
#             128,
#             16,
#             8
#         ],
#         "fieldname": [
#             "Marker",
#             "Length",
#             "Type"
#         ]
#     }},
#     "Value_list": {{
#         "Type": {{
#             "OPEN": "1",
#             "UPDATE": "2",
#             "NOTIFICATION": "3",
#             "KEEPALIVE": "4"
#         }}
#     }}
# }}
# '''

# mti1 = f'''
# {{
#     "Struct_list": {{}},
#     "Value_list": {{}}
# }}
# '''

# mti2 = f'''
# {{
#     "Value_list": {{
#         "OPEN Message Error Subcode": {{
#             "Unsupported Version Number": "1",
#             "Bad Peer AS": "2",
#             "Unacceptable Hold Time": "3",
#             "Bad BGP Identifier": "4",
#             "Unsupported Optional Parameters": "5",
#             "Unspecific": "0"
#         }},
#         "test": {{
#             "key1": "one",
#             "key2": "two"
#         }}
#     }}
# }}
# '''

# data1 = json.loads(mti1)
# print(data1["Value_list"])
# data2 = json.loads(mti2)
# data2 = json.loads(raw_info[1])
# print(data2["Value_list"])

# for item in data2["Value_list"]:
#     for i in data2["Value_list"][item]:
#         if data2["Value_list"][item][i].isdigit():
#             print(f"i is ok")
#         else:
#             print(f"i is not ok")
#             break

# for item in data2["Value_list"]:
#     if all(data2["Value_list"][item][key].isdigit() for key in data2["Value_list"][item]):
#         try:
#             data1["Value_list"].update(data2["Value_list"][item])
#         except TypeError as e:
#             continue
# print(data1)

# data1["Value_list"].update(data2["Value_list"])
# # data1.update(data2)
# print(data1)