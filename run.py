import click 
import scripts.path_setup

from pathlib import Path
from src.configs.common_configs import PathConfig
from src.rfc import RFC
from src.utils import split_document_by_sections
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
    rfc_name = f"RFC{rfc}"
    rfc_path = RFC().file_path(rfc)
    # print(f"RFC Folder Path: {rfc_path}")
    sections = split_document_by_sections(rfc_path)
    prompt_item = "prompt_4217_1"
    query_item = "query_1"
    prompt = make_prompt(sections, prompt_item)
    query = make_query(query_item)
    location = PathConfig().data
    logger = None
    
    if verbose:
        logger_config = LoggerConfig()
        logger = Logger(get_script_name(), **logger_config)
        
    extraction_run(model, rfc_name, sections, prompt, query, location, logger)


if __name__ == '__main__':
    run()