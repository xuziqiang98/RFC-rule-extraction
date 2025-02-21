import path_setup
import json

from src.mti import merge_reduntant_mti, mti2dict, extract_meta_info, read_mti, nest_mti
from src.configs.common_configs import PathConfig
from src.logger import NullLogger
from src.configs.prompt_factory import make_prompt, make_query

location = PathConfig().data
log_dir = "rfc4271_deepseek-r1_2025_02_21_11_31_04"
log_name = "merged_meta_info_deepseek-r1_prompt-mti-merge-1_query-5.txt"
log_path = location / log_dir / log_name

nested_mti_path = location / log_dir / f"nested_meta_info.txt"

new_mti_dict = read_mti(log_path)

# fix之后Marker字段怎么处理丢了？
Marker = f"""
{{
    "struct_name": "Marker",
    "info": {{
        "rfc": "rfc4271",
        "chapter": "4.1.",
        "mutable": false
    }},
    "bitwidth": {{
        "len": 16,
        "type": "bytes"
    }},
    "valid": ["0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF"]
}}
"""

new_mti_dict["Marker"] = json.loads(Marker)

# for key in new_mti_dict:
#     print(f"结构名：{key}，数量：{len(new_mti_dict[key])}")

# print(new_mti_dict["Message_Header"])
# print(new_mti_dict["Type"])

nested_mti = nest_mti(new_mti_dict)

print(json.dumps(nested_mti, indent=4))

with open(nested_mti_path, "w") as file:
    file.write(f"{json.dumps(nested_mti, indent=4)}")
file.close() 