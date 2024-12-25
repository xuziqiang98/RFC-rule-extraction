import inspect
# import torch
import random
# import numpy as np
import re

from types import MethodType, FunctionType
from pathlib import Path

def enable_grad_for_hf_llm(func: MethodType | FunctionType) -> MethodType | FunctionType:
    return func.__closure__[1].cell_contents


def get_script_name() -> str:
    caller_frame_record = inspect.stack()[1]
    module_path = caller_frame_record.filename
    return Path(module_path).stem


def set_seed(seed: int) -> None:
    random.seed(seed)
    # np.random.seed(seed)
    # torch.manual_seed(seed)
    # if torch.cuda.is_available():
    #     torch.cuda.manual_seed(seed)
    #     torch.cuda.manual_seed_all(seed)
    #     torch.backends.cudnn.deterministic = True
    #     torch.backends.cudnn.benchmark = False

def split_document_by_sections(file_path : str) -> dict:
    sections = {}
    current_section = None
    with open(file_path, 'r') as file:
        for line in file.readlines():
            line = line.strip()
            # 使用正则表达式匹配章节标题格式
            if re.match(r'(\d+\.)+\s{2}', line) and not re.match(r'.*\.{2,}.*', line):
                current_section = line
                sections[current_section] = ""
            elif current_section is not None:
                sections[current_section] += line
    return sections