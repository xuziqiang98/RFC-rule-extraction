import path_setup
import json

from src.mti import merge_reduntant_mti, mti2dict, extract_meta_info, read_mti, nest_mti
from src.configs.common_configs import PathConfig
from src.logger import NullLogger
from src.configs.prompt_factory import make_prompt, make_query

location = PathConfig().data
log_dir = "rfc4271_deepseek-r1_2025_02_21_11_31_04"
log_name = "fixed_meta_info_deepseek-r1_prompt-mti-fix-1_query-5.txt"
log_path = location / log_dir / log_name
meta_info = extract_meta_info(log_path)

# print(f"共有{len(meta_info)}个规则")
# for idx, item in enumerate(meta_info):
#     if idx < 5:
#         print(item)
    
mti_dict = mti2dict(meta_info)
# print(f"共有{len(mti_dict)}个元信息")
# for key in mti_dict:
#     print(f"结构名：{key}，数量：{len(mti_dict[key])}")
print(mti_dict["Type"])

logger = NullLogger()
api = "qwen"
model = "deepseek-r1"
prompt_item = "prompt-mti-merge-1"
query_item = "query-5"
prompt = make_prompt(prompt_item)
query = make_query(query_item)
save_path = location / log_dir / f"merged_meta_info_{model}_{prompt_item}_{query_item}.txt"

new_mti_dict = merge_reduntant_mti(mti_dict, logger, api, model,  prompt, query, save_path)

# new_mti_dict = read_mti(save_path)

# print(new_mti_dict["KEEPALIVE"])
# print(new_mti_dict["Marker"])
# print(new_mti_dict["Length"])
# print(new_mti_dict["Type"])

# nested_mti = nest_mti(new_mti_dict)

# print(json.dumps(nested_mti, indent=4))