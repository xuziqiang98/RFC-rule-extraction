import path_setup

from src.configs.common_configs import PathConfig
from src.utils import extract_formatted_rules, insert2excel

rfc = "RFC4271"
location = PathConfig().data
log_name = "RFC4271_deepseek-chat_prompt-4271-pk-3_2025_01_07_14_56_18.txt"
log_path = location / log_name
rules = extract_formatted_rules(log_path)
print(f"一共有{len(rules)}个规则")
for rule in rules:
    print(rule)
# insert2excel(rfc, log_name)