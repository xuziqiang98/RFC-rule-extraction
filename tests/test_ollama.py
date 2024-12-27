import path_setup
import ollama

response = ollama.chat(
    model='llama3.1', 
    messages=[
    {
    'role': 'system',
    'content': 'you are a helpful assistant',
    },
    {
        'role': 'user',
        'content': '为什么天空是蓝色的？',
    }
])
print(response['message']['content'])

# print(f"Model List: {ollama.list()}")