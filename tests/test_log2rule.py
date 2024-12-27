import path_setup

from src.configs.common_configs import PathConfig
from src.utils import extract_formatted_rules, insert2excel

rfc = "RFC2328"
location = PathConfig().data
log_name = "RFC2328_mixtral-8x7b-32768_2024_12_27_10_59.txt"
log_path = location / log_name
rules = extract_formatted_rules(log_path)
print(f"一共有{len(rules)}个规则")
# for rule in rules:
#     print(rule)
insert2excel(rfc, log_name)