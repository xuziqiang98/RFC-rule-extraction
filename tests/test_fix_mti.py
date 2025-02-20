import path_setup
import json

from src.utils import extract_meta_info, fix_mti_json, split_document_by_sections
from src.configs.common_configs import PathConfig
from src.logger import NullLogger
from src.configs.prompt_factory import make_prompt, make_query

location = PathConfig().data
# print(f"Location: {location}")
log_dir = "rfc4271_ep-20250218125805-px88r_2025_02_19_11_02_34"
log_name = "meta-info_rfc4271_prompt-4271-mti-2_query-4.txt"
log_path = location / log_dir / log_name

meta_info = extract_meta_info(log_path)

logger = NullLogger()
model = "ep-20250218125805-px88r"
rfc = "4271"
sections = split_document_by_sections(rfc)

fix_prompt_item = "prompt-mti-fix-1"
fix_query_item = "query-5"

fix_prompt = make_prompt(fix_prompt_item)
fix_query = make_query(fix_query_item)

save_path = location / log_dir / f"fixed_meta_info_{model}_{fix_prompt_item}_{fix_query_item}.txt"

fix_mti_json(logger, meta_info, model, sections, fix_prompt, fix_query, save_path)