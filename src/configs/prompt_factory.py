from src.utils import split_document_by_sections
from src.rfc import RFC

def make_prompt(sections, prompt_item):
    assert sections["4.1.  Message Header Format"], "The section is not found"
    prompt_dic = {"prompt_4217_1": f"You are a helpful AI Assistant. You can understand the examples \
                I gave and draw inferences from one instance. Before answering the \
                question, refer to the examples given to you first, and then analyze \
                them step by step. I will give you a part of the text from the RFC \
                and you need to extract the rules from it using this format: chk_bf(CONDITION, OPERATION), \
                it means before excute OPERATION the CONDITION should be checked. Here is the \
                text: {sections["4.1.  Message Header Format"]}. From this text, we can extract some rules. \
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
                Message Header is 19 octets."}
    return prompt_dic[prompt_item]

def make_query(query_item):
    query_dic = {"query_1": "Read and analyze the text, then extract the rules from it only about all of the fields in any Header Format. \
        If given text is not enough to extract the rules or is not related to the Header Format, please let me know and \
        skip to extract rules."}
    return query_dic[query_item]