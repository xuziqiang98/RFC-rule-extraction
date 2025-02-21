import json
import re

from src.utils import find_key_in_json, insert_into_json 
from tqdm import tqdm
from src.model import ModelFactory

def extract_meta_info(log_path) -> list[str]:
    """从日志文件中提取元信息。
    """
    # 读取日志文件
    with open(log_path, 'r') as file:
        log = file.read()
        file.close()
    # 使用正则表达式匹配规则
    pattern = r'<META_INFO>(.*?)<\/META_INFO>'
    
    raw_info = list(set(re.findall(pattern, log, re.DOTALL)))
    info = []
    
    # 如果文本中不存在struct_name，说明这个元信息是无效的
    for item in raw_info:
        if "struct_name" in item:
            info.append(item)   
    
    return info

def merge_meta_info(meta_info: list) -> dict:
    """废弃的函数，不再使用
    """
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

def build_nested_json(rfc, json_raw):
    """废弃的函数，不再使用
    """
    # struct_list是dict类型
    struct_list = json_raw["Struct_list"]
    value_list = json_raw["Value_list"]
    # print(f'value_list: {value_list.keys()}')
    result = {}
    key_path = []
    # done = {}
    # for item in struct_list:
    #     # print(item['struct_name'])
    #     struct_name = item['struct_name']
    #     done[struct_name] = False
    #     fieldname = item['fieldname']
    #     for field in fieldname:
    #         done[field] = False
    
    # for item in value_list:
    #     done[item] = False
    
    # print(done)
    
    # 先处理Message_Header
    for item in struct_list:
        if item['struct_name'] == "Message_Header":
            struct_name = item['struct_name']
            value = item['value']
            fieldname = item['fieldname']
            result[struct_name] = {"info": {"rfc": rfc,
                                            "chapter": ""}, 
                                   "bitwidth": {}, 
                                   "struct": {}}
            key_path.append(find_key_in_json(result, struct_name)[1])
            for pos, key in enumerate(fieldname):
                result[struct_name]["struct"].update({key: {"info": {"rfc": rfc,
                                                                 "chapter": ""}, 
                                                        "bitwidth": {"len": value[pos],
                                                                     "type": ""}, 
                                                        "struct": {}
                                                        }})
                key_path.append(find_key_in_json(result, key)[1])
                if key in value_list:
                    for v_k in value_list[key]:
                        result[struct_name]["struct"][key]["struct"].update({v_k: {}})
                        key_path.append(find_key_in_json(result, v_k)[1])
            break
    
    # 处理剩下的struct_list
    for item in struct_list:
        struct_name = item['struct_name']
        value = item['value']
        fieldname = item['fieldname']
        
        if struct_name == "Message_Header":
            continue
        
        # 处理struct_name歧义问题
        if key_path:
            struct_name = struct_name.split(".")[-1]
                    
            for item in key_path:
                if item[-1].lower() in struct_name.lower() or struct_name.lower() in item[-1].lower():
                    struct_name = item[-1]
                    break
        
        
        # 如果result中没有这个struct_name
        if not find_key_in_json(result, struct_name)[0]:
            result[struct_name] = {"info": {"rfc": rfc,
                                            "chapter": ""}, 
                                   "bitwidth": {}, 
                                   "struct": {}}
            key_path.append(find_key_in_json(result, struct_name)[1])
            # 将这个struct_name的所有fieldname都加入到result中
            for pos, key in enumerate(fieldname):
                result[struct_name]["struct"].update({key: {"info": {"rfc": rfc,
                                                                     "chapter": ""}, 
                                                            "bitwidth": {"len": value[pos],
                                                                         "type": ""}, 
                                                            "struct": {}
                                                            }})
                key_path.append(find_key_in_json(result, key)[1])
                # 如果某个字段在value_list中有对应的值
                # 说明这个字段还存在进一步的嵌套结构
                if key in value_list:
                    for v_k in value_list[key]:
                        # 这里只添加了字段名，并没有处理具体的嵌套结构
                        result[struct_name]["struct"][key]["struct"].update({v_k: {}})
                        key_path.append(find_key_in_json(result, v_k)[1])
        else:
            # 在struct_list中又能找到path
            # 说明这个字段是一个嵌套结构，在之前被加入到result中
            # 但是没有更新过这个字段具体的信息
            
            _, path = find_key_in_json(result, struct_name)
            insert_into_json(result, path, {"info": {"rfc": rfc,
                                                     "chapter": ""}, 
                                            "bitwidth": {}, 
                                            "struct": {}})   
            # 处理子字段的嵌套结构
            if find_key_in_json(value_list, struct_name)[0]:
                for pos, key in enumerate(fieldname):
                    insert_into_json(result, path + ["struct"], {key: {"info": {"rfc": rfc,
                                                                                "chapter": ""}, 
                                                                "bitwidth": {"len": value[pos],
                                                                             "type": ""}, 
                                                                "struct": {}
                                                                }}) 
                    key_path.append(find_key_in_json(result, key)[1])
    
    # 获取Error_Code和Error_Subcode路径
    code_counter = 0
    subcode_counter = 0
    if key_path:
        for item in key_path:
            if "Error_Code" in item[-1]:
                code_path = item
            if "Error_Subcode" in item[-1]:
                subcode_path = item
    
    code_path += ["struct"]
    subcode_path += ["struct"]
    
    # print(f'code_path: {code_path}')
    # print(f'subcode_path: {subcode_path}')
    
    # for item in value_list:
    #     print(item)
        
    for value_name in value_list:
        if value_name.split(".")[-1] == "Error_Code":
            insert_into_json(result, code_path, {value_name: {"info": {},
                                                              "bitwidth": {},
                                                              "struct": {},
                                                              "value": code_counter
                                                              }})
            code_counter += 1
        elif value_name.split(".")[-1] == "Error_Subcode":
            insert_into_json(result, subcode_path, {value_name: {"info": {},
                                                              "bitwidth": {},
                                                              "struct": {},
                                                              "value": subcode_counter
                                                              }})
            subcode_counter += 1
            
    # for item in key_path:
    #     print(item)
    
    return result

def fix_mti_json(logger, meta_info: list, api, model, sections, prompt, query, save_path) -> None:
    """修复提取的元信息。
    """
    # 按照chapter检索需要的章节，将具体的章节和对应的元信息json文本发送给大模型进行修复。
    # meta_info转成字典，key是strcut_name，value是list保存meta_info
    # 可能会有多个相同的struct_name
    
    logger.info("Convert meta info to dict.")
    
    meta_info_dict = mti2dict(meta_info)
    # for item_raw in meta_info:  # 遍历原始数据列表
    #     if not item_raw.strip():  # 跳过空字符串或纯空白字符
    #         continue
        
    #     try:
    #         # 解析JSON（自动处理单对象和列表）
    #         parsed_data = json.loads(item_raw)
            
    #         # 统一转换为列表处理（无论原始是单个对象还是列表）
    #         if isinstance(parsed_data, dict):
    #             json_list = [parsed_data]  # 单个对象转列表
    #         elif isinstance(parsed_data, list):
    #             json_list = parsed_data  # 已经是列表直接使用
    #         else:
    #             continue  # 跳过非字典/列表的无效数据
            
    #         # 处理每个JSON对象
    #         for info_json in json_list:
    #             # 确保结构包含必要字段
    #             if "struct_name" not in info_json:
    #                 continue
                
    #             struct_name = info_json["struct_name"]
                
    #             # 按struct_name分类存储
    #             if struct_name in meta_info_dict:
    #                 meta_info_dict[struct_name].append(info_json)
    #             else:
    #                 meta_info_dict[struct_name] = [info_json]
    #     except json.JSONDecodeError as e:
    #         logger.error(f"JSON decode failed: {e.msg}\nraw json：{item_raw}")
    #         continue
    #     except Exception as e:
    #         logger.error(f"Unkown error: {str(e)}")
    #         continue
    
    llm_model = ModelFactory().get(api, model)
    
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

def mti2dict(meta_info: list) -> dict[str, list[dict]]:
    """将元信息转换为字典。
    """
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
            print(f"JSON decode failed: {e.msg}, raw json: {item_raw[:50]}...")  # 打印前50字符辅助调试
        except Exception as e:
            print(f"未知错误: {str(e)}")
    
    return meta_info_dict

def merge_reduntant_mti(
    mti_dict:dict[str,list[dict]], 
    logger, api, model, prompt, query, save_path
) -> dict[str, dict]:
    """合并多余的元信息
    Args:
        mti_dict (dict[str, list[dict]]): 元信息字典
        logger (Logger): 日志记录器
        api (str): API提供商
        model (str): 模型名称
        prompt (str): 模型输入的prompt
        query (str): 模型输入的query
    Returns:
        new_mti_dict (dict[str, dict]): 合并之后的字典
    """
    new_mti_dict = {}
    llm_model = ModelFactory().get(api, model)
    for key in tqdm(mti_dict):
        if len(mti_dict[key]) == 1:
            new_mti_dict[key] = mti_dict[key][0]
            
        else: # 需要合并的情况
            logger.info(f"Merge redundant meta info for {key}.")
            
            try:
                output = llm_model.run(prompt, f"{query} JSON_Obj: {mti_dict[key]}")
                
                logger.info(output)
                
                # with open(save_path, "a") as file:
                #     file.write(f"Merge redundant meta info for {key}.\n")
                #     file.write(f"{output}\n\n")
                # file.close()
            
                pattern = r'<META_INFO>(.*?)<\/META_INFO>'
            
                single_mti = re.findall(pattern, output, re.DOTALL)
                
                if len(single_mti) > 1:
                    logger.error(f"Merge failed for {key}.")
                    continue
                else:
                    new_mti_dict[key] = json.loads(single_mti[0])
                    
            except Exception as e:
                logger.error(e)
                continue
    # 保存合并后的元信息
    with open(save_path, "w") as file:
        file.write(f"{json.dumps(new_mti_dict, indent=4)}")
    file.close()        
                
    logger.info("Merged meta info is saved in {save_path}.")
    
    return new_mti_dict

def read_mti(file_path: str) -> dict[str, dict]:
    """读取MTI文件并将其内容解析为字典。

    Args:
        file_path (str): MTI文件的路径。

    Returns:
        dict: 解析后的字典，键是struct_name，值是对应的字典。
    """
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    mti_dict = {}
    for key, value in data.items():
        mti_dict[key] = value
    
    return mti_dict

def nest_mti(meta_info: list[str, dict]) -> dict:
    """嵌套处理元信息
    """
    nested_mti = {}
    
    # 用一个栈来存储nested_mti中还未嵌套的字段
    field_stack = []
    
    # 处理两个字段互相嵌套，无限循环的问题
    done_fields = []
    
    # 找到Message_Header的位置
    for item in meta_info:
        if "header" in item.lower():
            header = item
            break
    # 处理Message_Header
    nested_mti[header] = {}
    insert_into_json(nested_mti, [header], {"info": meta_info[header]["info"]})
    insert_into_json(nested_mti, [header], {"bitwidth": meta_info[header]["bitwidth"]})
    # 如果存在valid，需要处理
    if "valid" in meta_info[header]:
        insert_into_json(nested_mti, [header], {"valid": meta_info[header]["valid"]})
    # 处理fieldname
    insert_into_json(nested_mti, [header], {"struct": {}})
    
    try:
        for field in meta_info[header]["fieldname"]:
            field_stack.append(field)
            insert_into_json(nested_mti, [header, "struct"], {field: {}})
    except KeyError as e:
        pass
    # 处理完之后将header从meta_info中删除
    meta_info.pop(header)
    done_fields.append(header)
    
    # 处理剩下的字段
    while meta_info:
        # 如果field_stack为空，meta_info不为空，从meta_info中取出一个字段继续处理
        if not field_stack:
            # 为了更深层次的嵌套，还不能随便取出一个字段
            # 这里优先处理存在extend_from的字段且extend_from已经处理过的字段
            # 其次处理存在extend_from的字段但是extend_from还没有处理过的字段
            # 最后处理没有extend_from的字段
            
            process_field = ""
            
            for field in meta_info:
                try:
                    extend_from = meta_info[field]["info"]["extend_from"]
                    if extend_from in done_fields:
                        process_field = field
                        break
                except KeyError as e:
                    continue
            
            if not process_field:
                process_field = list(meta_info.keys())[0]
            
            field_stack.append(process_field)
            
        while field_stack:
            field = field_stack.pop()
            
            # 如果这个字段已经处理过了，处理下一个字段
            if field in done_fields:
                try:
                    meta_info.pop(field)
                except KeyError as e:
                    continue
                continue
            
            # 如果这个字段不在meta_info中，处理下一个字段
            if field not in meta_info:
                done_fields.append(field)
                continue
            
            # 获取这个字段的路径
            path = find_key_in_json(nested_mti, field)[1]
            
            # 如果path为空，尝试通过extend_from找到这个字段的路径
            if not path:
                try:
                    extend_from = meta_info[field]["info"]["extend_from"]
                    path = find_key_in_json(nested_mti, extend_from)[1]
                    insert_into_json(nested_mti, path + ["struct"], {field: {}})
                    path = find_key_in_json(nested_mti, field)[1] 
                except KeyError as e:
                    pass
                
            # 此时path为空，说明这个字段是一个新的字段
            if not path:
                insert_into_json(nested_mti, path, {field: {}})
                path = find_key_in_json(nested_mti, field)[1]   
            
            insert_into_json(nested_mti, path, {"info": meta_info[field]["info"]})
            insert_into_json(nested_mti, path, {"bitwidth": meta_info[field]["bitwidth"]})
            if "valid" in meta_info[field]:
                insert_into_json(nested_mti, path, {"valid": meta_info[field]["valid"]})
            insert_into_json(nested_mti, path, {"struct": {}})
            
            # 存在fieldname才需要处理
            try:
                for subfield in meta_info[field]["fieldname"]:
                    # 有些字段会和自己互相嵌套，这里需要处理
                    if subfield == field:
                        continue
                    if subfield in done_fields:
                        continue
                    field_stack.append(subfield)
                    subpath = path + ["struct"]
                    insert_into_json(nested_mti, subpath, {subfield: {}})
            except KeyError as e:
                # meta_info.pop(field)
                # done_fields.append(field)  
                # continue
                pass
            
            try:
                meta_info.pop(field)
                done_fields.append(field)
            except KeyError as e:
                continue
                
    return nested_mti
    