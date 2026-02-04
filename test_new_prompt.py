# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '.')
from config.settings import config
from zhipuai import ZhipuAI

text = "1、现在的框图很好，云侧和端侧的画像向量输出是有道理的。"

print(f'Model: {config.model}')

client = ZhipuAI(api_key=config.api_key)

# Test with new prompt
response = client.chat.completions.create(
    model=config.model,
    messages=[
        {"role": "user", "content": f"直接输出纠错后的文本，不要任何解释说明：\n{text}"}
    ],
    temperature=0.3,
    max_tokens=2000
)

with open('new_prompt_test.txt', 'w', encoding='utf-8') as f:
    f.write('=== Prompt ===\n')
    f.write(f"直接输出纠错后的文本，不要任何解释说明：\n{text}\n\n")
    f.write('=== Response ===\n')
    f.write(response.choices[0].message.content)

print('Result saved to new_prompt_test.txt')
print(f'Content length: {len(response.choices[0].message.content)}')
