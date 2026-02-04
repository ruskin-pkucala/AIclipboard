# -*- coding: utf-8 -*-
import sys
import json
sys.path.insert(0, '.')
from config.settings import config
from zhipuai import ZhipuAI

text = """测试文本"""

print(f'Model: {config.model}')
print(f'API Key: {config.api_key[:20]}...')

client = ZhipuAI(api_key=config.api_key)

response = client.chat.completions.create(
    model=config.model,
    messages=[
        {"role": "user", "content": "请纠正以下文本中的错别字、病句和标点错误，只输出纠错后的文本：\n测试文本"}
    ],
    temperature=0.3,
    max_tokens=2000
)

print(f'\n=== Response type ===')
print(type(response))
print(f'\n=== Response ===')
print(response)

print(f'\n=== Choices length ===')
print(len(response.choices))

print(f'\n=== First choice ===')
print(response.choices[0])

print(f'\n=== Message content ===')
print(repr(response.choices[0].message.content))

print(f'\n=== Content length ===')
content = response.choices[0].message.content
print(len(content))
print(f'Content: {content}')
