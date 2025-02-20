import inspect
# import torch
import random
# import numpy as np
import re
import openpyxl
import regex
import json
import time
import spacy

from types import MethodType, FunctionType
from pathlib import Path
from src.rfc import RFC
from src.configs.common_configs import PathConfig
from openpyxl.utils import get_column_letter
from openpyxl.styles import Font
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity as cos_sim
from src.extraction import run
from src.model import ModelFactory
from tqdm import tqdm


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

def extract_formatted_rules(log_path) -> list:
    # 读取日志文件
    with open(log_path, 'r') as file:
        log = file.read()
        file.close()
    # 使用正则表达式匹配规则
    # pattern = r'chk_bf\([^)]*\)\)'
    # pattern = r'chk_bf\([^)]*,[^)]*\)\)'
    # pattern = r'chk_bf\(([^()]|(?R))*\)'
    pattern = r'<RULE>(.*?)<\/RULE>'
    
    rules = list(set(re.findall(pattern, log)))
    # rules = list(set(regex.findall(pattern, log)))
    return rules

def insert2excel(rfc, log_name, log_path):
    '''
    args:
        log_name: 日志文件名，保存的是从RFC文档中提取的规则
        log_path: 日志文件所在的路径
    '''
    
    is_new = False
    
    # log_path = PathConfig().data / log_name
    
    # full_path = log_path / log_name
    
    # 提取格式化的规则
    rules = extract_formatted_rules(log_path / log_name)
    
    # excel保存在日志同级目录下
    excel_name = "extracted_rules.xlsx"
    excel_path = log_path / excel_name
    
    try:
        # 尝试打开已有的Excel文件
        workbook = openpyxl.load_workbook(excel_path)
    except FileNotFoundError:
        # 如果文件不存在，则创建新的工作簿，并删除默认的'Sheet'工作表
        workbook = openpyxl.Workbook()
        default_sheet = workbook.active
        workbook.remove(default_sheet)
    
    table_name = f"{rfc}_PKF"
    
    try:
        worksheet = workbook[table_name]
    except KeyError:
        is_new = True
        worksheet = workbook.create_sheet(table_name)
    
    # workbook = openpyxl.load_workbook(excel_path)
    # worksheet = workbook["RFC4217_PK"]
    
    column_count = worksheet.max_column
    
    if is_new:
        current_column = 1
    else:
        current_column = column_count + 1
    
    for index, value in enumerate(rules):
        if index == 0:
            worksheet.cell(row = index + 1, column = current_column).value = log_name
            bold_font = Font(bold=True)
            worksheet.cell(row = index + 1, column = current_column).font = bold_font
        else:
            worksheet.cell(row = index + 1, column = current_column).value = value
    
    workbook.save(excel_path)
    
def extract_meta_info(log_path) -> list:
    # 读取日志文件
    with open(log_path, 'r') as file:
        log = file.read()
        file.close()
    # 使用正则表达式匹配规则
    pattern = r'<META_INFO>(.*?)<\/META_INFO>'
    
    raw_info = list(set(re.findall(pattern, log, re.DOTALL)))
    info = []
    
    for item in raw_info:
        if "struct_name" in item:
            info.append(item)   
    return info

def merge_meta_info(meta_info: list) -> dict:
    template = f'''
    {{
        "Struct_list": [],
        "Value_list": {{}}
    }}
    '''
    data = json.loads(template)
    for info in meta_info:
        if info == "":
            continue
        try:
            info_json = json.loads(info)
            if "Struct_list" in info_json:
                try:
                    for item in info_json["Struct_list"]:
                        data["Struct_list"].append(item)
                except TypeError as e:
                    continue
            if "Value_list" in info_json:
                pop_list = []
                for item in info_json["Value_list"]:
                    if all(info_json["Value_list"][item][key].isdigit() for key in info_json["Value_list"][item]):
                        continue
                    else:
                        # 有些Value_list中的值不是数字，需要排除
                        pop_list.append(item)
                for item in pop_list:
                    info_json["Value_list"].pop(item)
                try:
                    data["Value_list"].update(info_json["Value_list"])
                except TypeError as e:
                    continue
        except json.JSONDecodeError as e:
            continue
    return data

def cosine_similarity(str1, str2):
    # nlp = spacy.load('en_core_web_md')
    # doc1 = nlp(str1)
    # doc2 = nlp(str2)
    # return doc1.similarity(doc2)
    
    vectorizer = CountVectorizer().fit_transform([str1, str2])
    vectors = vectorizer.toarray()
    return cos_sim([vectors[0]], [vectors[1]])[0][0]

def merge_mti(meta_info: list):
    # mti_pool是一个缓冲池，用来存放JSON格式的meta info，以便后续合并
    # key是字段名，value是meta info
    mti_pool = {}
    
def fix_mti_json(logger, meta_info: list, model, sections, prompt, query, save_path):
    # 按照chapter检索需要的章节，将具体的章节和对应的元信息json文本发送给大模型进行修复。
    # meta_info转成字典，key是strcut_name，value是list保存meta_info
    # 可能会有多个相同的struct_name
    
    logger.info("Convert meta info to dict.")
    
    meta_info_dict = {}
    for item_raw in meta_info:  # 遍历原始数据列表
        if not item_raw.strip():  # 跳过空字符串或纯空白字符
            continue
        
        try:
            # 解析JSON（自动处理单对象和列表）
            parsed_data = json.loads(item_raw)
            
            # 统一转换为列表处理（无论原始是单个对象还是列表）
            if isinstance(parsed_data, dict):
                json_list = [parsed_data]  # 单个对象转列表
            elif isinstance(parsed_data, list):
                json_list = parsed_data  # 已经是列表直接使用
            else:
                continue  # 跳过非字典/列表的无效数据
            
            # 处理每个JSON对象
            for info_json in json_list:
                # 确保结构包含必要字段
                if "struct_name" not in info_json:
                    continue
                
                struct_name = info_json["struct_name"]
                
                # 按struct_name分类存储
                if struct_name in meta_info_dict:
                    meta_info_dict[struct_name].append(info_json)
                else:
                    meta_info_dict[struct_name] = [info_json]
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode failed: {e.msg}\nraw json：{item_raw}")
            continue
        except Exception as e:
            logger.error(f"Unkown error: {str(e)}")
            continue
    
    llm_model = ModelFactory().get(model)
    
    for field in tqdm(meta_info_dict):
        # 取出chapter
        chapter = meta_info_dict[field][0]["info"]["chapter"]
        # print(f"Chapter: {chapter}")
        # 取出section
        section = ""
        for s in sections:
            if chapter in s:
                section = s
                break
        # print(f"Section: {section}")
        if section == "":
            logger.error(f"Section not found for {field}.")
            continue
        
        logger.info(f"Fixing meta info for {field} based on {section}.")
        
        try:
            output = llm_model.run(prompt, f"{query} Meta_info_JSON: {meta_info_dict[field]} Section: {section}. Content: {sections[section]}")
        except Exception as e:
            logger.error(e)
            
        logger.info(output)
        
        with open(save_path, "a") as file:
            file.write(f"Fix extracted meta info of: {field}\n")
            file.write(f"{output}\n\n")
        file.close()