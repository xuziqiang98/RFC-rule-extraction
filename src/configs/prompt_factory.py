from src.utils import split_document_by_sections
from src.rfc import RFC

def make_prompt(prompt_item):
    rfc_4271_sections = split_document_by_sections(rfc='4271')
    # print(f"一共有{len(rfc_4271_sections)}个section")
    assert rfc_4271_sections["4.1.  Message Header Format"], "The section is not found"
    prompt_dic = {"prompt-4271-1": f"You are a helpful AI Assistant. You can understand the examples \
                I gave and draw inferences from one instance. Before answering the \
                question, refer to the examples given to you first, and then analyze \
                them step by step. I will give you a part of the text from the RFC \
                and you need to extract the rules from it using this format: chk_bf(CONDITION, OPERATION), \
                it means before excute OPERATION the CONDITION should be checked. Here is the \
                text: {rfc_4271_sections["4.1.  Message Header Format"]}. From this text, we can extract some rules. \
                For example 1, chk_bf(len(Marker) == 16, use(Marker)), it means before accessing the Marker field, \
                we have to check if the length of the Marker is 16. This rule can be extracted from 'Marker:This \
                16-octet field is included for compatibility'. Example 2, \
                chk_bf(Type == 1 || Type == 2 || Type == 3 || Type == 4, use(Type)), it means Tpye has to be assigned 1 or 2 or 3 or 4 \
                before using it. This rule can be extracted from 'This document defines the following type codes:1 - \
                OPEN2 - UPDATE3 - NOTIFICATION4 - KEEPALIVE[RFC2918]'. Example 3, \
                chk_bf(len(Length) >= 19 && len(Length) <= 4096, use(Length)), which means the Length field should be greater than \
                19 octets and less than 4096 octets before using it. This rule can be extracted from 'The value of the Length \
                field MUST always be at least19 and no greater than 4096, and MAY be further constrained,depending on the message type.' \
                Example 4, chk_bf(len(Message Header) == 19, use(Message Header)), it indicates that the length of the Message Header \
                is equal to 19 octets before using it. This rule can be extracted from the whole text, because we can know Message Header is \
                consisted by Marker field, Length field and Type field, and their length is 16, 2 and 1 respectively. So the total length of \
                Message Header is 19 octets.",
                "prompt-4271-2": f"You are en expert of Netowrk Protocol. Now I need you to extract the rules from the RFC docummnets as the following \
                examples. All of rules are extracted in the format of chk_bf(CONDITION, OPERATION), where OPERATION is the field when it is used in \
                implementation and CONDITION is the condition that should be checked before excuting the OPERATION. More specifically, the format of rule \
                is like this: chk_bf(CONDITION, use(FIELD)), where CONDITION is a euqation or an inequality that should be satisfied before using the FIELD. \
                You can understand the following examples and extract the rules from the section chunk of RFCs. \
                Example 1, section 4.1.  Message Header Format, Marker: This 16-octet field is included for compatibility; it MUST be set to all ones. \
                This can be extracted two rules. First, chk_bf(len(Marker) == 16, use(Marker)), it means before accessing the Marker field, we have to \
                check if the length of the Marker is 16. Second, chk_bf(Marker == 0xFFFFFFFFFFFFFFFF, use(Marker)), it means the Marker field should be set \
                to all ones before using it. \
                Example 2, section 6.1.  Message Header Error Handling, if the Length field of the message header is less than 19 or greater than 4096. \
                This can be extracted a rule, chk_bf(len(Length) >= 19 && len(Length) <= 4096, use(Length)), which means the Length field should \
                be greater than 19 octets and less than 4096 octets before using it. \
                From above two examples, you notice that len() is used to check the octets of the field and two conditions are connected by &&. \
                Example 3, section 4.5.  NOTIFICATION Message Format, The minimum length of the NOTIFICATION message is 21 octets(including message header).\
                This can be extracted a rule, chk_bf(len(NOTIFICATION message) >= 21, use(NOTIFICATION message)). \
                Example 4, section 4.2.  OPEN Message Format, The Hold Time MUST be either zero or at least three seconds. This can be extracted a rule, \
                chk_bf(Hold Time == 0 || Hold Time >= 3, use(Hold Time)), so at least means >= in the rule. \
                Example 5, section 4.2.  OPEN Message Format, Optional Parameters Length: This 1-octet unsigned integer indicates the total length of the \
                Optional Parameters field in octets. If the value of this field is zero, no Optional Parameters are present. This can be extracted a rule, \
                chk_bf(Optional Parameters Length != 0, use(Optional Parameters)), it means the Optional Parameters Length field should be present before using it. \
                Before you extract rules, recall the examples I gave you and analyze them step by step. The format of rules is important, if you can extract some \
                information but can not be expressed in the format of chk_bf(CONDITION, use(FIELD)), please let me know and skip to extract rules. Notice that CONDITION \
                is a euqation or an inequality that should be satisfied before using the FIELD. Furthermore, RFCs have many informations related protocol, like Header Format, \
                State Machine and Error Handling, you only need to extract rules about the fields in any Header Format. Don't forget give reasons why you extract the rules."}
    
    return prompt_dic[prompt_item]

def make_query(query_item):
    query_dic = {"query-1": "Read and analyze the text, then extract the rules from it only about all of the fields in any Header Format. \
        If given text is not enough to extract the rules or is not related to the Header Format, please let me know and \
        skip to extract rules.",
        "query-2": "Read and analyze the text, then extract the rules from it only about all of the fields in any Header Format. \
        If given text is not enough to extract the rules or is not related to the Header Format, please let me know and \
        skip to extract rules. Note that, each extracted rule needs to be surrounded by <RULE> </RULE>, in the form of: <RULE>chk_bf(CONDITION, OPERATION)</RULE>."}
    return query_dic[query_item]