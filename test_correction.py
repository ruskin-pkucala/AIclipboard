# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '.')
from ai_service import ai_service

# Test with text that has errors
text = "这个文本有一些问题，比如标点符号错误，还有错别字（比如"的"和"得"用错了）。"

print('Testing AI service with error text...')
result = ai_service.correct_text(text, mode='correct')

with open('error_correction_test.txt', 'w', encoding='utf-8') as f:
    f.write('=== 原文 ===\n')
    f.write(text + '\n\n')
    f.write('=== 纠错结果 ===\n')
    f.write(result.get('corrected', 'NO RESULT') + '\n\n')
    f.write('=== 修改说明 ===\n')
    f.write(str(result.get('changes', [])) + '\n')

print('Result saved to error_correction_test.txt')
print(f'Corrected: {result.get("corrected", "NO RESULT")}')
