import path_setup

from src.configs.common_configs import PathConfig
from src.utils import extract_formatted_rules, insert2excel

rfc = "RFC4271"
location = PathConfig().data / "rfc4271_deepseek-r1_32b_2025_02_03_19_56_36"
log_name = "pktrule_rfc4271_prompt-4271-pkt-3_query-2.txt"
log_path = location / log_name
rules = extract_formatted_rules(log_path)
print(f"一共有{len(rules)}个规则")
for rule in rules:
    print(rule)
insert2excel(rfc, log_name, location)