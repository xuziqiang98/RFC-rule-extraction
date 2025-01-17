import path_setup
import json
from src.parser import build_nested_json
from src.configs.common_configs import PathConfig

location = PathConfig().data
mti_dir = "rfc4271_deepseek-chat_2025_01_17_17_27_22"
mti_name = "meta-info_rfc4271.json"
mti_path = location / mti_dir / mti_name

# 一个简单的测试demo
# location = PathConfig().root
# mti_path = location / 'demo.json'

rfc = "rfc4271"

data = json.load(open(mti_path, "r"))
# print(json.dumps(data, indent=4))
# for item in data["Struct_list"]:
#     print(item['fieldname'])

nested_json = build_nested_json(rfc, data)

print(json.dumps(nested_json, indent=4))
