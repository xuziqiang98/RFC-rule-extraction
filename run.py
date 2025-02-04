import click 
import scripts.path_setup
import json

from datetime import datetime
from pathlib import Path
from src.configs.common_configs import PathConfig
from src.rfc import RFC
from src.utils import split_document_by_sections, insert2excel, extract_meta_info, merge_meta_info
from src.configs.prompt_factory import make_prompt, make_query
from src.extraction import run as extraction_run
from src.logger import Logger
from src.utils import get_script_name
from src.configs.common_configs import LoggerConfig
from src.model import ModelFactory
from src.parser import build_nested_json

@click.command()
@click.option('--rfc', required = True, type = str, default="4271", help="The path to the RFC document.")
@click.option('--model', required = True, type = str, default="qwen-max", help="The LLM model used to extract rules.")
@click.option('--verbose', is_flag = True, help="Save exhausted log.")
def run(rfc, model, verbose):
    
    #############################
    # Set Variables             #
    #############################
    
    logger = None
    
    if verbose:
        logger_config = LoggerConfig()
        logger = Logger(get_script_name(), **logger_config)
        
    rfc_name = f"rfc{rfc}"
    # rfc_path = RFC().file_path(rfc)
    # print(f"RFC Folder Path: {rfc_path}")
    
    #############################
    # Set    Locations          #
    #############################
    
    # 获取当前时间
    now = datetime.now()
    # 按照指定格式进行格式化输出
    formatted_time = now.strftime('%Y_%m_%d_%H_%M_%S')
    data_location = PathConfig().data
    
    # RFC相关日志保存在output_dir文件夹下，完整的路径是data_location / output_dir
    # 文件夹命名不能包含冒号，所以需要将model中的冒号替换为下划线
    split_model = model.split(":")
    if len(split_model) > 1:
        rename_model = f"{split_model[0]}_{split_model[1]}"
        output_dir = f"{rfc_name}_{rename_model}_{formatted_time}"
    else:    
        output_dir = f"{rfc_name}_{model}_{formatted_time}"    
    output_path = data_location / output_dir
    
    # 创建文件夹
    output_path.mkdir(parents=True, exist_ok=True)
    
    #############################
    # Split RFCs                #
    #############################
    
    if logger is not None:
        logger.info(f"Splitting the document {rfc_name} into sections.")
    
    sections = split_document_by_sections(rfc)
    
    #############################
    # Extract PKT Rules         #
    #############################
    
    # 设置提示词和查询词
    pkt_prompt_item = "prompt-4271-pkt-3"
    pkt_query_item = "query-2"
    
    pkt_prompt = make_prompt(pkt_prompt_item)
    pkt_query = make_query(pkt_query_item)
    
    # pkt rule的日志
    pktrule_log = f"pktrule_{rfc_name}_{pkt_prompt_item}_{pkt_query_item}.txt"
    pktrule_log_path = output_path / pktrule_log
    
    if logger is not None:
        logger.info(f"Extracting pkt rules from {rfc_name} using LLM model {model}.")
    
    # LLMs提取规则的输出保存在pktrule_log_path中
    extraction_run(model, sections, pkt_prompt, pkt_query, pktrule_log_path, logger)
    
    # if logger is not None:
    #     logger.info(f"Extracted rules are saved to {output_path}.")
    
    if logger is not None:
        logger.info("Inserting extracted rules into Excel file.")
    
    # 将提取的规则插入到Excel文件中
    # 这里只是用来确认提取的规则是否正确
    insert2excel(rfc_name, pktrule_log, output_path)
    
    #############################
    # Extract Meta Info         #
    #############################
    
    mti_prompt_item = "prompt-4271-mti-1"
    mti_query_item = "query-3"
    
    mti_prompt = make_prompt(mti_prompt_item)
    mti_query = make_query(mti_query_item)
    
    # meta info的日志
    meta_info_log = f"meta-info_{rfc_name}_{mti_prompt_item}_{mti_query_item}.txt"
    meta_info_log_path = output_path / meta_info_log
    
    if logger is not None:
        logger.info(f"Extracting meta info from {rfc_name} using LLM model {model}.")
    
    extraction_run(model, sections, mti_prompt, mti_query, meta_info_log_path, logger)
    
    if logger is not None:
        logger.info(f"Extracting JSON formatted meta info from {meta_info_log_path}.")
    
    meta_info = extract_meta_info(meta_info_log_path)
    
    if logger is not None:
        logger.info(f"Merging meta info from {meta_info_log_path}.")
    
    # 合并完的meta info
    json_info = merge_meta_info(meta_info)
    
    meta_info_json = f"meta-info_{rfc_name}.json"
    meta_info_json_path = output_path / meta_info_json
    
    if logger is not None:
        logger.info(f"Saving JSON formatted meta info to {meta_info_json_path}.")
    
    with open(meta_info_json_path, "w") as file:
        json.dump(json_info, file, indent=4)
    
    # 将meta info处理成嵌套结构
    nested_json = build_nested_json(rfc, json_info)
    nested_json_path = output_path / f"nested_{rfc_name}.json"
    
    if logger is not None:
        logger.info(f"Saving nested JSON formatted meta info to {nested_json_path}.")
    
    with open(nested_json_path, "w") as file:
        json.dump(nested_json, file, indent=4)
    
    
    if logger is not None:
        logger.info("All processes are done.")

if __name__ == '__main__':
    run()
    
# python run.py --rfc 4271 --model deepseek-chat --verbose