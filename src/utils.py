import inspect
# import torch
import random
# import numpy as np
import re

from types import MethodType, FunctionType
from pathlib import Path
from src.rfc import RFC

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

def split_document_by_sections(rfc : str) -> dict:
    
    rfc_4271_filter = ['10.  Each timer has a "timer" and a "time" (the initial value).']
    
    rfc_2328_filter = ["6.  Note that Router RT10 has a virtual link configured to Router",
                       "1.  Into the backbone, Router RT4 originates separate",
                       "8.  Two of the summary-LSAs originated by Router RT4",
                       "16.  There are three OSPF routers (RTA, RTB and RTC)",
                       "12.2.  The lookup process may return an LSA whose LS age is equal to",
                       "224.0.0.5.  All routers running OSPF should be prepared to",
                       "224.0.0.6.  Both the Designated Router and Backup Designated",
                       "10.9.  The reception of Link State Request packets is documented in",
                       "2178.  All differences are backward-compatible. Implementations of",
                       "16.2.  After completion of the calculation in Section 16.3, any"]
    
    if rfc == "4271":
        rfc_path = RFC().file_path(rfc)
        sections = {}
        current_section = None
        with open(rfc_path, 'r') as file:
            for line in file.readlines():
                line = line.strip()
                # 使用正则表达式匹配章节标题格式
                if re.match(r'(\d+\.)+\s{2}', line) and not re.match(r'.*\.{2,}.*', line) and line not in rfc_4271_filter:
                    current_section = line
                    sections[current_section] = ""
                elif current_section is not None:
                    sections[current_section] += line
        return sections
    elif rfc == "2328":
        rfc_path = RFC().file_path(rfc)
        sections = {}
        current_section = None
        with open(rfc_path, 'r') as file:
            for line in file.readlines():
                line = line.strip()
                # 使用正则表达式匹配章节标题格式
                if re.match(r'(\d+\.)+\s{2}', line) and not re.match(r'.*\.{2,}.*', line) and line not in rfc_2328_filter:
                    current_section = line
                    sections[current_section] = ""
                elif current_section is not None:
                    sections[current_section] += line
        return sections
    else:
        rfc_path = RFC().file_path(rfc)
        sections = {}
        current_section = None
        with open(rfc_path, 'r') as file:
            for line in file.readlines():
                line = line.strip()
                # 使用正则表达式匹配章节标题格式
                if re.match(r'(\d+\.)+\s{2}', line) and not re.match(r'.*\.{2,}.*', line):
                    current_section = line
                    sections[current_section] = ""
                elif current_section is not None:
                    sections[current_section] += line
        return sections