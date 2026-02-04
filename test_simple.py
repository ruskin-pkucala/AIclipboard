# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '.')
from zhipuai import ZhipuAI
from config.settings import config

print('Testing simple API call...')
client = ZhipuAI(api_key=config.api_key)

# Simple test
r = client.chat.completions.create(
    model='glm-4',
    messages=[{'role': 'user', 'content': '请纠正这句话：这个文本有一些问题'}]
)

with open('simple_test_result.txt', 'w', encoding='utf-8') as f:
    f.write('Response:\n')
    f.write(r.choices[0].message.content)

print('Result saved to simple_test_result.txt')
print(f'Content length: {len(r.choices[0].message.content)}')
