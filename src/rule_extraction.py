import os

from tqdm import tqdm
from openai import OpenAI
from datetime import datetime

def extraction_run(llm_model, rfc, sections, prompt, query, location, logger):
    # llm_model =  "qwen-max"
    # 获取当前时间
    now = datetime.now()
    # 按照指定格式进行格式化输出
    formatted_time = now.strftime('%Y_%m_%d_%H_%M')
    
    save_path = location / f"{rfc}_{llm_model}_{formatted_time}.txt"
    
    verbose = False
    if logger is not None:
        verbose = True
    
    client = OpenAI(
            # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )

    for section in tqdm(sections):
        if verbose:
            logger.info(f"Section: {section}")
                        
        llm = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": prompt
                },
                {
                    "role": "user",
                    "content": query + sections[section],
                }
            ],
            model = llm_model
        )
        output = llm.choices[0].message.content
        
        if verbose:
            logger.info(output)
        
        # store the answer in a file
        with open(save_path, "a") as file:
            file.write(f"Section: {section}\n")
            file.write(f"{output}\n\n")
        file.close()
        
        print(output)