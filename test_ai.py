"""
测试脚本 - 验证 AI 服务是否正常工作
"""
import sys
import os
from pathlib import Path

# 设置控制台编码为 UTF-8
if os.name == 'nt':  # Windows
    os.system('chcp 65001 > nul')

# 添加项目根目录到路径
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

from config.settings import config
from ai_service import ai_service

print("=" * 50)
print("剪贴板智能纠错工具 - 测试")
print("=" * 50)

# 检查配置
print(f"\n1. 配置检查:")
print(f"   API Key: {'已配置' if config.api_key else '未配置'}")
print(f"   模型: {config.model}")
print(f"   最大记录数: {config.max_records}")

if not config.api_key:
    print("\n[X] 未配置 API Key，无法继续测试")
    sys.exit(1)

# 测试 AI 服务
test_text = "这个文本有一些问题，比如标点符号错误，还有错别字（比如\"的\"和\"得\"用错了）。"

print(f"\n2. AI 服务测试:")
print(f"   原文: {test_text}")

try:
    print(f"\n   正在调用智谱 GLM-4.7 进行文本纠错...")
    result = ai_service.correct_text(test_text, mode="correct")

    print(f"\n   [OK] 纠错成功!")
    print(f"   纠错后: {result['corrected']}")
    print(f"   说明: {result['changes']}")

except Exception as e:
    print(f"\n   [ERROR] 纠错失败: {e}")
    import traceback
    traceback.print_exc()

# 测试其他模式
print(f"\n3. 测试其他润色模式:")
modes = {
    "formal": "正式商务",
    "casual": "轻松口语",
    "concise": "简洁明了"
}

for mode, name in modes.items():
    try:
        print(f"   测试 {name} 模式...", end=" ")
        result = ai_service.correct_text("你好，我想要咨询一下产品信息", mode=mode)
        print(f"[OK]")
        print(f"      结果: {result['corrected'][:50]}...")
    except Exception as e:
        print(f"[ERROR] {e}")

print("\n" + "=" * 50)
print("测试完成！")
print("=" * 50)
