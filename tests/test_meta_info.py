import path_setup
import json

from src.utils import extract_meta_info, merge_meta_info
from src.configs.common_configs import PathConfig

location = PathConfig().data
log_dir = "rfc4271_ep-20250218125805-px88r_2025_02_19_11_02_34"
log_name = "meta-info_rfc4271_prompt-4271-mti-2_query-4.txt"
log_path = location / log_dir / log_name
meta_info = extract_meta_info(log_path)

meta_info_dict = {}
for item_raw in meta_info:  # 遍历原始数据列表
    if not item_raw.strip():  # 跳过空字符串或纯空白字符
        continue
    
    try:
        # 解析JSON（自动处理单对象和列表）
        parsed_data = json.loads(item_raw)
        
        # 统一转换为列表处理（无论原始是单个对象还是列表）
        if isinstance(parsed_data, dict):
            json_list = [parsed_data]  # 单个对象转列表
        elif isinstance(parsed_data, list):
            json_list = parsed_data  # 已经是列表直接使用
        else:
            continue  # 跳过非字典/列表的无效数据
        
        # 处理每个JSON对象
        for info_json in json_list:
            # 确保结构包含必要字段
            if "struct_name" not in info_json:
                continue
            
            struct_name = info_json["struct_name"]
            
            # 按struct_name分类存储
            if struct_name in meta_info_dict:
                meta_info_dict[struct_name].append(info_json)
            else:
                meta_info_dict[struct_name] = [info_json]
                
    except json.JSONDecodeError as e:
        print(f"JSON decode failed: {e.msg}, raw json: {item_raw[:50]}...")  # 打印前50字符辅助调试
    except Exception as e:
        print(f"未知错误: {str(e)}")

# for item in meta_info_dict:
#     print(f"结构名：{item}，数量：{len(meta_info_dict[item])}")
        
# print(meta_info_dict["AS_PATH"])

print(meta_info_dict["Origin"][0]["info"]["chapter"])

# print(raw_info[0])

# for info in raw_info:
#     print(info)

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