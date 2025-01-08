import path_setup
import json

from src.utils import extract_meta_info, merge_meta_info
from src.configs.common_configs import PathConfig

location = PathConfig().data
log_name = "RFC4271_deepseek-chat_prompt-4271-mti-1_2025_01_07_19_16_23.txt"
log_path = location / log_name
raw_info = extract_meta_info(log_path)

# for info in raw_info:
#     print(info)

json_info = merge_meta_info(raw_info)


output = json.dumps(json_info, indent=4)
print(output)

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
#         }}
#     }}
# }}
# '''

# data1 = json.loads(mti1)
# print(data1["Value_list"])
# # data2 = json.loads(mti2)
# data2 = json.loads(raw_info[1])
# print(data2["Value_list"])

# data1["Value_list"].update(data2["Value_list"])
# # data1.update(data2)
# print(data1)