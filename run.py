import click 
import scripts.path_setup

from datetime import datetime
from pathlib import Path
from src.configs.common_configs import PathConfig
from src.rfc import RFC
from src.utils import split_document_by_sections, extract_formatted_rules, insert2excel
from src.configs.prompt_factory import make_prompt, make_query
from src.rule_extraction import extraction_run
from src.logger import Logger
from src.utils import get_script_name
from src.configs.common_configs import LoggerConfig
from src.model import ModelFactory

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
        
    rfc_name = f"RFC{rfc}"
    # rfc_path = RFC().file_path(rfc)
    # print(f"RFC Folder Path: {rfc_path}")
    
    if logger is not None:
        logger.info(f"Splitting the document {rfc_name} into sections.")
    
    sections = split_document_by_sections(rfc)
    
    # prompt_item = "prompt-4271-1"
    prompt_item = "prompt-4271-2"
    
    # query_item = "query-1"
    query_item = "query-2"
    
    prompt = make_prompt(prompt_item)
    query = make_query(query_item)
    
    # 获取当前时间
    now = datetime.now()
    # 按照指定格式进行格式化输出
    formatted_time = now.strftime('%Y_%m_%d_%H_%M_%S')
    location = PathConfig().data
    log_name = f"{rfc_name}_{model}_{prompt_item}_{formatted_time}.txt"
    save_path = location / log_name
    
    #############################
    # Extract Rules             #
    #############################
    
    if logger is not None:
        logger.info(f"Extracting rules from {rfc_name} using LLM model {model}")
    
    extraction_run(model, sections, prompt, query, save_path, logger)
    
    if logger is not None:
        logger.info(f"Extracted rules are saved to {save_path}")
    
    if logger is not None:
        logger.info("Inserting extracted rules into Excel file.")
    
    insert2excel(rfc_name, log_name)
    
    if logger is not None:
        logger.info("All processes are done.")

if __name__ == '__main__':
    run()