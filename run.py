import click 
import scripts.path_setup
import json

from datetime import datetime
from pathlib import Path
from src.configs.common_configs import PathConfig
from src.rfc import RFC
from src.mti import extract_meta_info, fix_mti_json, mti2dict, merge_reduntant_mti, nest_mti
from src.utils import split_document_by_sections, insert2excel
from src.configs.prompt_factory import make_prompt, make_query
from src.extraction import run as extraction_run
from src.logger import Logger, NullLogger
from src.utils import get_script_name
from src.configs.common_configs import LoggerConfig
from src.model import ModelFactory

def rfc2chucks(logger, rfc_name, rfc):
    logger.info(f"Splitting the document {rfc_name} into sections.")
    
    sections = split_document_by_sections(rfc)
    return sections

def pkt_rules_extraction(logger,rfc_name, pkt_prompt_item, pkt_query_item, api, model, sections, pkt_prompt, pkt_query, output_path):
    # pkt rule的日志
    pktrule_log = f"pktrule_{rfc_name}_{pkt_prompt_item}_{pkt_query_item}.txt"
    pktrule_log_path = output_path / pktrule_log
    
    logger.info(f"Extracting pkt rules from {rfc_name} using LLM model {model}.")
    
    # LLMs提取规则的输出保存在pktrule_log_path中
    extraction_run(api, model, sections, pkt_prompt, pkt_query, pktrule_log_path, logger)
    
    logger.info("Inserting extracted rules into Excel file.")
    
    # 将提取的规则插入到Excel文件中
    # 这里只是用来确认提取的规则是否正确
    insert2excel(rfc_name, pktrule_log, output_path)
    
    logger.info(f"Extracted rules are saved to {output_path}.")
        
def meta_info_extraction(logger, rfc, rfc_name, mti_prompt_item, mti_query_item, api, model, sections, mti_prompt, mti_query, output_path):
    # meta info的日志
    meta_info_log = f"meta-info_{rfc_name}_{mti_prompt_item}_{mti_query_item}.txt"
    meta_info_log_path = output_path / meta_info_log
    
    logger.info(f"Extracting meta info from {rfc_name} using LLM model {model}.")
    
    extraction_run(api, model, sections, mti_prompt, mti_query, meta_info_log_path, logger)
    
    logger.info(f"Extracting JSON formatted meta info from {meta_info_log_path}.")
    
    meta_info = extract_meta_info(meta_info_log_path)
    
    #############################
    # Fix Meta Info             #
    #############################
    
    logger.info(f"Start to fix the extracted meta info.")
    
    fix_prompt_item = "prompt-mti-fix-1"
    fix_query_item = "query-5"
    
    fix_prompt = make_prompt(fix_prompt_item)
    fix_query = make_query(fix_query_item)
    
    fix_mti_path = output_path / f"fixed_meta_info_{model}_{fix_prompt_item}_{fix_query_item}.txt"
    
    fix_mti_json(logger, meta_info, api, model, sections, fix_prompt, fix_query, fix_mti_path)
    
    logger.info(f"Fixed meta info is saved to {fix_mti_path}.")
    
    #############################
    # Merge Reduntant Meta Info #
    #############################
    
    logger.info(f"Start to merge the fixed meta info.")
    
    fix_mti = extract_meta_info(fix_mti_path)
    
    mti_dict = mti2dict(fix_mti)
    
    merge_prompt_item = "prompt-mti-merge-1"
    merge_query_item = "query-5"
    merge_prompt = make_prompt(merge_prompt_item)
    merge_query = make_query(merge_query_item)
    merged_mti_path = output_path / f"merged_meta_info_{model}_{merge_prompt_item}_{merge_query_item}.txt"

    new_mti_dict = merge_reduntant_mti(mti_dict, logger, api, model,  merge_prompt, merge_query, merged_mti_path)

    #############################
    # Nest Meta Info            #
    #############################
    
    nested_mti_path = output_path / f"nested_meta_info.txt"
    
    nested_mti = nest_mti(new_mti_dict)

    with open(nested_mti_path, "w") as file:
        file.write(f"{json.dumps(nested_mti, indent=4)}")
    file.close() 
    

@click.command()
@click.option('--rfc', required = True, type = str, default="4271", help="The path to the RFC document.")
@click.option('--api', required = True, type = str, default="ollama", help="The API used to submit the LLM model.")
@click.option('--model', required = True, type = str, default="deepseek-r1:32b", help="The LLM model used to extract rules.")
@click.option('--verbose', is_flag = True, help="Save exhausted log.")
def run(rfc, api, model, verbose):
    
    #############################
    # Set Variables             #
    #############################
    
    logger = NullLogger()
    
    if verbose:
        logger_config = LoggerConfig()
        logger = Logger(get_script_name(), **logger_config)
        
    rfc_name = f"rfc{rfc}"
    
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
    
    sections = rfc2chucks(logger, rfc_name, rfc)
    
    #############################
    # Extract PKT Rules         #
    #############################
    
    # 设置提示词和查询词
    pkt_prompt_item = "prompt-4271-pkt-3"
    pkt_query_item = "query-2"
    
    pkt_prompt = make_prompt(pkt_prompt_item)
    pkt_query = make_query(pkt_query_item)
    
    # pkt_rules_extraction(logger, rfc_name, pkt_prompt_item, pkt_query_item, api, model, sections, pkt_prompt, pkt_query, output_path)
    
    #############################
    # Extract Meta Info         #
    #############################
    
    mti_prompt_item = "prompt-4271-mti-2"
    mti_query_item = "query-4"
    
    mti_prompt = make_prompt(mti_prompt_item)
    mti_query = make_query(mti_query_item)
    
    meta_info_extraction(logger, rfc, rfc_name, mti_prompt_item, mti_query_item, api, model, sections, mti_prompt, mti_query, output_path)
    
    logger.info("All processes are done.")

if __name__ == '__main__':
    run()
    
# python run.py --rfc 4271 --api qwen --model deepseek-r1 --verbose