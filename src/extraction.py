import os
import time

from tqdm import tqdm
from openai import OpenAI
from datetime import datetime
from src.model import ModelFactory

def run(model, sections, prompt, query, save_path, logger):
    
    llm_model = ModelFactory().get(model)

    for section in tqdm(sections):
        logger.info(f"Section: {section}")

        if sections[section] == "":
            continue
        
        try:
            output = llm_model.run(prompt, f"{query} Section: {section}. Content: {sections[section]}")
        except Exception as e:
            logger.error(e)
        
        logger.info(output)
        
        # store the answer in a file
        with open(save_path, "a") as file:
            file.write(f"Section: {section}\n")
            file.write(f"{output}\n\n")
        file.close()
        
        print(output)
        
        if model == "llama3.3-70b-instruct":
            time.sleep(5)
        elif model == "llama3.1-405b-instruct":
            time.sleep(5)
        elif model == "llama-3.3-70b-versatile":
            time.sleep(5)