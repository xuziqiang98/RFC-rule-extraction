import json

from src.utils import cosine_similarity

def find_key_in_json(data, target_key, path=None):
    if path is None:
        path = []
    if isinstance(data, dict):
        for key, value in data.items():
            if key == target_key:
                return True, path + [key]
            found, sub_path = find_key_in_json(value, target_key, path + [key])
            if found:
                return found, sub_path
    elif isinstance(data, list):
        for index, item in enumerate(data):
            found, sub_path = find_key_in_json(item, target_key, path + [index])
            if found:
                return found, sub_path
    return False, []

def insert_into_json(data, path, new_data):
    def helper(sub_data, sub_path):
        if len(sub_path) == 1:
            if isinstance(sub_data, dict) and sub_path[0] in sub_data:
                if isinstance(sub_data[sub_path[0]], dict):
                    sub_data[sub_path[0]].update(new_data)
                else:
                    sub_data[sub_path[0]] = {}
                    sub_data[sub_path[0]].update(new_data)
        else:
            if isinstance(sub_data, dict) and sub_path[0] in sub_data:
                helper(sub_data[sub_path[0]], sub_path[1:])
            elif isinstance(sub_data, list) and isinstance(sub_path[0], int) and len(sub_data) > sub_path[0]:
                helper(sub_data[sub_path[0]], sub_path[1:])

    helper(data, path)

def build_nested_json(rfc, json_raw):
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