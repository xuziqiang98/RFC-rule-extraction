from src.utils import split_document_by_sections
from src.rfc import RFC

def make_prompt(prompt_item):
    
    rfc_4271_sections = split_document_by_sections(rfc='4271')
    # print(f"一共有{len(rfc_4271_sections)}个section")
    assert rfc_4271_sections["4.1.  Message Header Format"], "The section is not found"
    
    prompt_dic = {"prompt-4271-pkt-1": f'''
                You are a helpful AI Assistant. You can understand the examples I gave and draw inferences from one instance. Before answering the question, \
                refer to the examples given to you first, and then analyze them step by step. I will give you a part of the text from the RFC and you need \
                to extract the rules from it using this format: chk_bf(CONDITION, OPERATION), it means before excute OPERATION the CONDITION should be checked. \
                Here is the text: {rfc_4271_sections["4.1.  Message Header Format"]}. From this text, we can extract some rules.
                For example 1, chk_bf(len(Marker) == 16, use(Marker)), it means before accessing the Marker field, \
                we have to check if the length of the Marker is 16. This rule can be extracted from 'Marker:This \
                16-octet field is included for compatibility'. 
                Example 2, chk_bf(Type == 1 || Type == 2 || Type == 3 || Type == 4, use(Type)), it means Tpye has to be assigned 1 or 2 or 3 or 4 \
                before using it. This rule can be extracted from 'This document defines the following type codes:1-OPEN 2-UPDATE 3-NOTIFICATION 4-KEEPALIVE[RFC2918]'. 
                Example 3, chk_bf(len(Length) >= 19 && len(Length) <= 4096, use(Length)), which means the Length field should be greater than \
                19 octets and less than 4096 octets before using it. This rule can be extracted from 'The value of the Length \
                field MUST always be at least19 and no greater than 4096, and MAY be further constrained,depending on the message type.'
                Example 4, chk_bf(len(Message Header) == 19, use(Message Header)), it indicates that the length of the Message Header \
                is equal to 19 octets before using it. This rule can be extracted from the whole text, because we can know Message Header is \
                consisted by Marker field, Length field and Type field, and their length is 16, 2 and 1 respectively. So the total length of Message Header is 19 octets.
                ''',
                "prompt-4271-pkt-2": f'''
                You are an expert of Netowrk Protocol. Now I need you to extract the rules from the RFC docummnets as the following \
                examples. All of rules are extracted in the format of chk_bf(CONDITION, OPERATION), where OPERATION is the field when it is used in \
                implementation and CONDITION is the condition that should be checked before excuting the OPERATION. More specifically, the format of rule \
                is like this: chk_bf(CONDITION, use(FIELD)), where CONDITION is a euqation or an inequality that should be satisfied before using the FIELD. \
                You can understand the following examples and extract the rules from the section chunk of RFCs.
                Example 1, section 4.1.  Message Header Format, Marker: This 16-octet field is included for compatibility; it MUST be set to all ones. \
                This can be extracted two rules. First, chk_bf(len(Marker) == 16, use(Marker)), it means before accessing the Marker field, we have to \
                check if the length of the Marker is 16. Second, chk_bf(Marker == 0xFFFFFFFFFFFFFFFF, use(Marker)), it means the Marker field should be set \
                to all ones before using it.
                Example 2, section 6.1.  Message Header Error Handling, if the Length field of the message header is less than 19 or greater than 4096. \
                This can be extracted a rule, chk_bf(len(Length) >= 19 && len(Length) <= 4096, use(Length)), which means the Length field should \
                be greater than 19 octets and less than 4096 octets before using it.
                From above two examples, you notice that len() is used to check the octets of the field and two conditions are connected by &&.
                Example 3, section 4.5.  NOTIFICATION Message Format, The minimum length of the NOTIFICATION message is 21 octets(including message header).\
                This can be extracted a rule, chk_bf(len(NOTIFICATION message) >= 21, use(NOTIFICATION message)).
                Example 4, section 4.2.  OPEN Message Format, The Hold Time MUST be either zero or at least three seconds. This can be extracted a rule, \
                chk_bf(Hold Time == 0 || Hold Time >= 3, use(Hold Time)), so at least means >= in the rule.
                Example 5, section 4.2.  OPEN Message Format, Optional Parameters Length: This 1-octet unsigned integer indicates the total length of the \
                Optional Parameters field in octets. If the value of this field is zero, no Optional Parameters are present. This can be extracted a rule, \
                chk_bf(Optional Parameters Length != 0, use(Optional Parameters)), it means the Optional Parameters Length field should be present before using it.
                Before you extract rules, recall the examples I gave you and analyze them step by step. The format of rules is important, if you can extract some \
                information but can not be expressed in the format of chk_bf(CONDITION, use(FIELD)), please let me know and skip to extract rules. Notice that CONDITION \
                is a euqation or an inequality that should be satisfied before using the FIELD. Furthermore, RFCs have many informations related protocol, like Header Format, \
                State Machine and Error Handling, you only need to extract rules about the fields in any Header Format. Don't forget give reasons why you extract the rules.
                ''',
                "prompt-4271-pkt-3": f'''
                You are a professional AI Assistant and experted in Network Protocol. You have already know many information about network protocols and RFC ducuments. \
                You can correctly distinguish what a message is, what a field is, and what a variable is. \
                Your task is to extract the rules from the RFC documents. You can undersand the examples I gave and draw inferences from one instance. Before answering \
                the question, refer to the examples given to you first, and then analyze them step by step. 
                The extraction of the rules from RFC documents using specific format. Here are rules format's template: \
                * chk_bf(CONDITION, use(MESSAGE_TYPE.FIELD)): It means before accessing the field in the message type, we have to check if the condition is satisfied. \
                CONDITION is represented by equations or inequalities, sometimes it is a combination of them.
                Note that, if you find out a rule but can not express it in the format of chk_bf(CONDITION, use(MESSAGE_TYPE.FIELD)), please let me know and skip to extract rules. \
                Furthermore, each extracted rule needs to be surrounded by <RULE></RULE>.
                Following, I will give you some specific examples including parts of the RFCs and the rules extracted from them. You can refer to those examples. 
                * Example 1, Section: "4.2.  OPEN Message Format", Content: "The Hold Time MUST be either zero or at least three seconds.". This can be extracted a rule, \
                <RULE>chk_bf(OPEN_Message.Hold_Time == 0 || OPEN_Message.Hold_Time >= 3, use(OPEN_Message.Hold_Time))</RULE>, where OPEN_Message is a type of message and \
                Hold_Time is a field in the message. It means the Hold Time field should be either zero or at least three seconds before using it.
                From this example, you can learn that extrected rules should be included in specific messages' type and the field. Moreover, accessing a specific field is \
                denoted by use(FIELD). Furthermore, 0 and 3 are the values of the Hold Time field, so if checking the value of the field, you can use the value directly. \
                If one field has multiple parallel conditions, use || to present OR relationship and use && to present AND relationship.
                * Example 2, Section: "4.1.  Message Header Format", Content: "Marker: This 16-octet field is included for compatibility; it MUST be set to all ones.". \
                This can be extracted two rules. First, <RULE>chk_bf(len(Message_Header.Marker) == 16, use(Message_Header.Marker))</RULE>, it indicates that representing \
                the length of a field is denoted by len(FIELD). Second, <RULE>chk_bf(Message_Header.Marker == 0xFFFFFFFFFFFFFFFF, use(Message_Header.Marker))</RULE>, \
                this rule needs you to combine the length of the field and the value of the field. Specific, 16 octets means 16*8 bits and all of them are assigned to 1, so \
                the value of the Marker field is 0xFFFFFFFFFFFFFFFF.
                Note that, above examples are related to the packet format including message's type, field's name and the value of the field. You only need to extract rules about \
                packet format. If given text is not enough to extract the rules or is not related to the packet format, please let me know and skip to extract rules.
                ''',
                "prompt-4271-mti-1": f'''
                You are a professional AI Assistant and experted in Network Protocol. You have already know many information about network protocols and RFC ducuments. \
                You can correctly distinguish what a message is, what a field is, and what a variable is. Your task is to extract meta information from the RFC documents and \
                conclude them with JSON format. You can undersand the examples I gave and draw inferences from one instance. Before answering the question, refer to the \
                examples given to you first, and then analyze them step by step. 
                For example, I will give you a part of the text from the RFCs. Section: "4.1.  Message Header Format", Content: {rfc_4271_sections["4.1.  Message Header Format"]}. \
                From this text, we can extract the following meta information:
                <META_INFO>
                {{
                    "Struct_list": [
                        {{
                            "struct_name": "Message_Header",
                            "value": [
                                128,
                                16,
                                8
                            ],
                            "fieldname": [
                                "Marker",
                                "Length",
                                "Type"
                            ]
                        }}
                    ],
                    "Value_list": {{
                        "Type": {{
                            "OPEN": "1",
                            "UPDATE": "2",
                            "NOTIFICATION": "3",
                            "KEEPALIVE": "4"
                        }}
                    }}
                }}
                </META_INFO>
                * Struct_list is a list of structures in the packet structure, which includes struct_name, value and fieldname. 'struct_name' is the name of the structure, like Message Header, \
                OPEN Message, UPDATE Message, etc. 'fieldname' is the name of the field in the structure, in this case, we can know the Message Header is consisted by three fields: Marker, Length and Type. \
                'value' is the corresponding length of the field in bits, for example, Marker is 16 octets, so the first element in 'value' is 16*8=128 bits. If the field is a fixed length, you can directly give the value of the field. \
                If the field is a variable length, you can give 0 to the value of the field.
                * Value_list is a dictionary, each item in it is a key-value pair. From the text, we can know the Type field has four values: 1, 2, 3, 4, which represent OPEN, UPDATE, NOTIFICATION and KEEPALIVE respectively. \
                So if a field has multiple values, you can conclude them in the format of "value's meaning": "value".
                Sometimes you can only extract Struct_list or Value_list, it should be ok. If you can not extract any information or the given text is not enough to extract the meta information, \
                please let me know and skip to extract meta information, but do not output empty meta information.
                * You have to notice that the item in 'Struct_list' has and only has three keys: 'struct_name', 'value' and 'fieldname'. The key of item in 'Value_list' is the name of the field(if the field belongs to one specific \
                message type, you can add the message type before the field name, like OPEN Message Error and UPDATE Message Error), \
                and the value of the item is a dictionary, which includes the value of the field and the meaning of the value, they connected by ':', and value is a string at the right side of ':'. \
                If the right side of ':' is not a number or a number in string format, it's not a valid value, you don't need to extract it.
                ** For example, "Time in seconds": "Time in seconds" is not a valid value, because the right side of ':' is not a number or a number in string format. \
                "TRUE": "TRUE", is not a valid value, because the right side of ':' is not a number or a number in string format. \
                If you meet the above situation, you can skip to extract the value. 
                * In addition, when you extract the value and you put somethins to the key position of JSON, you have to make sure they are not implicit. \
                ** For example, 'Error subcode' is implicit, you have to point out this error subcode belongs to which message type, like OPEN Message Error subcode, it can be written as "OPEN_Message.Error_Subcode". \
                * Also, the string in struct_name should be explicit, you can not use the abbreviation or the acronym, you have to use the full name of the structure and the field. \
                ** For example, "struct_name": "Open_Message" is implicit, you have to use "struct_name": "Message_Header.OPEN_Message".
                ''',
                "prompt-4271-mti-2": f'''
                任务：
                    - 从给定的RFC文档章节中提取字段信息，然后用给定的JSON格式输出。
                    - 提取信息之前，请参考我给你的例子，然后逐步分析，搞清楚应该提取什么信息。
                    - 如果给定的文本不足以提取字段信息，直接跳过，不要用JSON输出错误信息或者说明性的信息，此时也不用输出<META_INFO></META_INFO>标签。
                任务说明：
                    - 字段信息是指RFC文档中的字段名称、字段大小（字节）、字段取值、出自哪个RFC文档、文档的哪一章。
                    - 字段和字段之间可能存在嵌套关系，要在JSON中体现出来。
                    - 协议的实例一般由消息头、消息体和可选参数组成，每一部分都要提取字段信息。
                    - 确保最后<META_INFO></META_INFO>包裹的JSON格式是正确的。
                    - 输出的JSON需要用<META_INFO></META_INFO>包裹。
                例子1：
                {{
                    "struct_name": "Message_Header",
                    "info": {{
                        "rfc": "rfc4271",
                        "chapter": "4.1."
                    }},
                    "bitwidth": {{}},
                    "fieldname": [
                        "Marker",
                        "Length",
                        "Type"
                    ]
                }}
                例子1说明：
                    - Message_Header并不是字段，这里用于标识消息头。
                    - rfc4271是RFC文档的编号，4.1.是文档的章节。
                    - bitwidth是字段的大小，单位是比特。由于Message_Header是消息头，没有字段大小，这里为空。
                    - fieldname是消息头包含的字段，体现出了嵌套关系，这里有三个字段：Marker、Length和Type。
                例子2：
                {{
                    "struct_name": "Marker",
                    "info": {{
                        "rfc": "rfc4271",
                        "chapter": "4.1.",
                        "mutable": false
                    }},
                    "bitwidth": {{
                        "len": 16,
                        "type": "bytes"
                    }},
                    "valid": [
                        "0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF"
                    ]
                }}
                例子2说明：
                    - Maker是一个字段名。
                    - rfc4271是RFC文档的编号，4.1.是文档的章节。
                    - mutable表示字段是否可变，这里是false，表示Marker字段不可变。
                    - 注意，只有固定值的字段才需要mutable属性，如果字段的值不是固定的，不需要写"mutable":true。
                    - bitwidth是字段的大小，单位是比特，这里是16字节。
                    - valid是字段的有效值，这里是16个字节的全1。
                    - 注意，valid列表里的一定是一个字符串表示的值，可以转成某个数，而不是一个描述。
                例子3：
                {{
                    "struct_name": "Type",
                    "info": {{
                        "rfc": "rfc4271",
                        "chapter": "4.1."
                        "extend_from": "Message_Header"
                    }},
                    "bitwidth": {{
                        "len": 1,
                        "type": "byte"
                    }},
                    "fieldname": [
                        "OPEN",
                        "UPDATE",
                        "TNOTIFICATION",
                        "KEEPALIVE"
                    ]
                }}
                例子3说明：
                    - Type是一个字段名。
                    - rfc4271是RFC文档的编号，4.1.是文档的章节。
                    - extend_from表示字段的嵌套关系，这里表明该字段是Message_Header的一部分。
                    - bitwidth是字段的大小，单位是比特，这里是1字节。
                    - fieldname体现了嵌套关系，这里有四个字段：OPEN、UPDATE、TNOTIFICATION和KEEPALIVE，说明根据TYPE的取值可以对应这四个消息体。
                ''',
                "prompt-mti-fix-1": f'''
                任务：
                    - 修复给定的JSON格式的文本，使其符合所有的要求。
                    - JSON文本的内容是从RFC文档中提取的字段信息。
                    - 修复时需要参考任务说明，逐步修复JSON对象。
                    - 只要原有的格式上修改，不要新增或删除字段
                    - 修复时不要凭空捏造，要根据给定的文本进行修复。
                    - 确保修复后的JSON对象格式正确，且必须被<META_INFO></META_INFO>包裹。
                    - 除了JSON对象以及<META_INFO></META_INFO>，不要输出其他信息。
                任务说明：
                    - 第一步，检查JSON对象的个数，如果有多个对象，需要按照struct_name合并成一个对象。
                    - 第二步，检查struct_name。
                        - "struct_name"的值要么是消息头Message_Header，要么是字段名，不能是其他的。
                        - "struct_name"的值不能使用缩写或首字母缩写。
                        - "struct_name"的值如果由多个单词组成，单词之间用下划线分隔。
                    - 第三步，检查info中的键和值。
                        - "rfc"的值表示struct_name所在的RFC文档编号。
                        - "rfc"的值的格式是rfc+RFC文档编号，如rfc4271。
                        - 如果"rfc"的值不确定，应该用""表示。
                        - "chapter"的值表示struct_name所在的章节。
                        - "chapter"的值的格式是数字+点，如4.1.。
                        - 如果"chapter"的值不确定，应该用""表示。
                        - "extend_from"的值表示struct_name的父结构，体现了字段的嵌套关系。
                        - 如果"extend_from"的值不确定，不需要添加"extend_from"这个键。
                    - 第四步，检查bitwidth。
                        - "bitwidth"的值是一个字典，包含"len"和"type"两个键。
                        - "len"的值表示字段的长度，单位是比特。
                        - 消息头Message_Header的"bitwidth"的值为空字典。
                        - 如果"bitwidth"的值不确定，应该用{{}}表示。
                    - 第五步，检查字段的值是否是固定的。
                        - 如果字段的值是固定的，需要在"info"中添加"mutable": false，否则不需要添加。
                        - 如果字段的值是固定的，需要添加"valid"，该键与"bitwidth"同级，否则不需要添加。
                    - 第六步，检查valid。
                        - "valid"的值是一个列表，包含字段的有效值，这个值必须用十六进制的字符串表示。
                        - 十六进制的字符串格式是0x开头，后面跟着若干个十六进制数字，如果是英文字母要大写。
                        - 除此之外，不要添加任何其他信息。
                    - 第七步，检查fieldname。
                        - "fieldname"的值是一个列表，只包含字段的名称，不要添加其他的信息。
                        - "fieldname"列表中的字段如果由多个单词组成，单词之间用下划线分隔。
                    - 第八步，确保没有新增其他的键。
                        - JSON对象的第一层除了"struct_name"、"info"、"bitwidth"、"valid"、"fieldname"这几个键，不要新增其他的键。
                        - "info"中的键可能有"rfc"、"chapter"、"mutable"、"extend_from"这些键，不要新增其他的键。
                        - "bitwidth"中的键可能有"len"、"type"这两个键，不要新增其他的键。
                    - 第九步，确保输出的JSON对象格式正确。
                        - 确保修复后的JSON对象中只包含上述提到的键。
                        - 如果JSON对象不需要修复，输出原JSON对象，且必须用<META_INFO></META_INFO>包裹JSON对象。
                        - 如果JSON对象需要修复，只输出修复后的JSON对象，且必须用<META_INFO></META_INFO>包裹JSON对象。
                '''}
    
    return prompt_dic[prompt_item]

def make_query(query_item):
    query_dic = {"query-1": f'''
        Read and analyze the text, then extract the rules from it only about all of the fields in any Header Format. \
        If given text is not enough to extract the rules or is not related to the Header Format, please let me know and \
        skip to extract rules.
        ''',
        "query-2": f'''
        Read and analyze the text, then extract the rules from it only about Packet Format. If given text is not enough \
        to extract the rules or is not related to the Header Format, please let me know and skip to extract rules. \
        Note that, each extracted rule needs to be surrounded by <RULE></RULE>, in the form of: <RULE>chk_bf(CONDITION, OPERATION)</RULE>.
        ''',
        "query-3": f'''
        Read and analyze the text, then extract the meta information from it with given JSON format. If given text is not enough \
        to extract the meta information, please let me know and skip to extract meta information. Note that, the extracted meta information \
        should be surrounded by <META_INFO></META_INFO> like example. DO NOT output empty meta information, if you just can extract Struct_list, \
        only output Struct_list, if you just can extract Value_list, only output Value_list. If you can not extract any information, do not output \
        empty meta information using <META_INFO></META_INFO>. Before extracting, recall the examples I gave you and analyze them step by step.
        ''',
        "query-4": f'''
        仔细阅读和分析给定的文本，参考给你的例子，然后提取字段信息，用给定的JSON格式输出。注意，只要给出包含<META_INFO></META_INFO>的JSON格式即可，不需要输出其他信息。
        ''',
        "query-5": f'''
        仔细阅读和分析任务，用给定的JSON格式输出。注意，只要给出包含<META_INFO></META_INFO>的JSON格式即可，不需要输出其他信息。
        '''}
    return query_dic[query_item]