import os
import ollama

from groq import Groq
from openai import OpenAI
from abc import ABC, abstractmethod

model_list = {"qwen-max": "QwenModel",
              "qwen-plus": "QwenModel",
              "qwen-turbo": "QwenModel",
              "qwen-long": "QwenModel",
              "llama-3.3-70b-versatile": "GroqModel",
              "llama-3.1-8b-instant": "GroqModel",
              "mixtral-8x7b-32768": "GroqModel",
              "llama3-70b-8192": "GroqModel",
              "llama3.3-70b-instruct": "QwenModel",
              "llama3.1-405b-instruct": "QwenModel",
              "llama3.1": "OllamaModel"}

class ModelFactory:
    def get(self, model):
        assert model in model_list, f"LLM model{model} is not supported!"
        model_class = globals().get(model_list[model])
        return model_class(model)


class ModelBase(ABC):
    def __init__(self, model):
        self.model = model
    
    @abstractmethod
    def run(self):
        pass

class QwenModel(ModelBase):
    def __init__(self, model):
        super().__init__(model)
        self.client = OpenAI(
            # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
    
    def run(self, prompt, query) -> str:
        llm = self.client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": prompt
                },
                {
                    "role": "user",
                    "content": query
                }
            ],
            model = self.model
        )
        return llm.choices[0].message.content

class GroqModel(ModelBase):
    def __init__(self, model):
        super().__init__(model)
        self.client = Groq(
            api_key=os.environ.get("GROQ_API_KEY"),
        )
    
    def run(self, prompt, query):
        llm = self.client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": prompt
                },
                {
                    "role": "user",
                    "content": query
                }
            ],
            model = self.model
        )
        return llm.choices[0].message.content

class OllamaModel(ModelBase):
    def __init__(self, model):
        super().__init__(model)
    
    def run(self, prompt, query):
        llm = ollama.chat(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": prompt
                },
                {
                    "role": "user",
                    "content": query
                }
            ]
        )
        return llm["message"]["content"]