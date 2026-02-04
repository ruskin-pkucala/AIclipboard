"""
AI 服务模块 - 调用智谱 GLM-4.7 进行文本纠错和润色
"""
import time
import threading
from zhipuai import ZhipuAI
from typing import Literal, Optional
from config.settings import config


class AIService:
    """智谱 GLM API 服务"""

    def __init__(self):
        self.client = None
        self.last_request_time = 0
        self.min_request_interval = 1.0  # 请求间隔至少1秒
        self.lock = threading.Lock()
        self._init_client()

    def _init_client(self):
        """初始化智谱 AI 客户端"""
        api_key = config.api_key

        if not api_key:
            raise ValueError(
                "未找到智谱 AI API Key！\n"
                "请确保：\n"
                "1. 首次运行时输入 API Key\n"
                "2. 或设置环境变量 ZHIPUAI_API_KEY"
            )

        self.client = ZhipuAI(api_key=api_key)

    def _wait_for_rate_limit(self):
        """等待以确保不超过请求速率限制"""
        with self.lock:
            current_time = time.time()
            time_since_last_request = current_time - self.last_request_time

            if time_since_last_request < self.min_request_interval:
                wait_time = self.min_request_interval - time_since_last_request
                time.sleep(wait_time)

            self.last_request_time = time.time()

    def correct_text(
        self,
        text: str,
        mode: Literal["correct", "formal", "casual", "academic", "concise", "creative"] = "correct"
    ) -> dict:
        """
        纠错/润色文本

        Args:
            text: 待处理文本
            mode: 处理模式
                - correct: 纯纠错（错字、病句、标点）
                - formal: 正式商务风格
                - casual: 轻松口语风格
                - academic: 学术专业风格
                - concise: 简洁明了风格
                - creative: 创意生动风格

        Returns:
            dict: {
                "original": 原文,
                "corrected": 纠错后文本,
                "changes": 修改说明,
                "mode": 使用模式
            }
        """
        # 构建提示词
        mode_names = {
            "correct": "文本校对",
            "formal": "正式商务风格改写",
            "casual": "轻松口语风格改写",
            "academic": "学术专业风格改写",
            "concise": "简洁明了风格改写",
            "creative": "创意生动风格改写"
        }

        # 提示词：先输出纠错后文本，再输出修改说明
        prompts = {
            "correct": """你是中文输入法纠错专家。请仔细检查并纠正以下文本中的错误。

**重点检查输入法导致的错误：**
1. 同音字错误（如："在"→"再"、"已"→"己"、"的"→"得"、"做"→"作"）
2. 形近字错误（如："未"→"末"、"候"→"侯"、"戊"→"戌"）
3. 全角/半角符号错误（如："，"→"，"、"。"→"。"、"("→"（"）
4. 英文输入法导致的中文错误
5. 键盘位置相邻导致的错误
6. 多字或少字（如:"一一下"→"一下子"）

**不要修改的内容：**
- 专有名词、人名、地名
- 专业术语
- 有意使用的口语、网络用语或方言
- 原本正确的表达方式

**输出格式（严格遵守）：**
第一行：直接输出纠错后的完整文本（不要任何解释）
如有修改：第二行输出"---"
第三行开始：列出具体修改，格式：原词→新词：原因

如果没有错误，第一行直接输出原文即可。

待处理文本：
{text}""",

            "formal": """请将以下文本改写为正式商务风格，保持原意不变。

先直接输出改写后的完整文本，然后另起一行输出"---"分隔符，再列出主要的修改要点。

待处理文本：
{text}""",

            "casual": """请将以下文本改写为轻松自然的口语风格，保持原意不变。

先直接输出改写后的完整文本，然后另起一行输出"---"分隔符，再列出主要的修改要点。

待处理文本：
{text}""",

            "academic": """请将以下文本改写为学术专业风格，保持原意不变。

先直接输出改写后的完整文本，然后另起一行输出"---"分隔符，再列出主要的修改要点。

待处理文本：
{text}""",

            "concise": """请将以下文本改写为简洁明了的风格，保持原意不变。

先直接输出改写后的完整文本，然后另起一行输出"---"分隔符，再列出主要的修改要点。

待处理文本：
{text}""",

            "creative": """请将以下文本改写为生动有趣的表达，保持原意不变。

先直接输出改写后的完整文本，然后另起一行输出"---"分隔符，再列出主要的修改要点。

待处理文本：
{text}"""
        }

        prompt = prompts.get(mode, prompts["correct"]).format(text=text)

        # 重试机制
        max_retries = 3
        retry_delay = 2  # 秒

        for attempt in range(max_retries):
            try:
                # 限流
                self._wait_for_rate_limit()

                response = self.client.chat.completions.create(
                    model=config.model,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3 if mode == "correct" else 0.7,
                    max_tokens=3000
                )

                # 获取回复内容
                result_text = response.choices[0].message.content

                # 清理可能的markdown代码块标记
                if result_text.startswith("```"):
                    lines = result_text.split("\n")
                    if lines[0].startswith("```"):
                        result_text = "\n".join(lines[1:])
                    if result_text.endswith("```"):
                        result_text = result_text[:-3]
                    result_text = result_text.strip()

                # 解析结果：分离纠错文本和修改说明
                corrected_text = result_text
                changes = []

                if "---" in result_text:
                    parts = result_text.split("---", 1)
                    corrected_text = parts[0].strip()
                    changes_text = parts[1].strip() if len(parts) > 1 else ""

                    # 解析修改说明
                    if changes_text:
                        # 按行分割，过滤空行
                        change_lines = [line.strip() for line in changes_text.split("\n") if line.strip()]
                        changes = change_lines[:5]  # 最多显示5条

                # 如果没有提取到修改说明，使用默认消息
                if not changes:
                    if corrected_text == text:
                        changes = ["文本正确，无需修改"]
                    else:
                        changes = [f"已使用{mode_names.get(mode, mode)}处理"]

                return {
                    "original": text,
                    "corrected": corrected_text,
                    "changes": changes,
                    "mode": mode
                }

            except Exception as e:
                error_str = str(e)

                # 检查是否是速率限制错误
                if "429" in error_str or "1302" in error_str or "并发" in error_str:
                    if attempt < max_retries - 1:
                        # 指数退避重试
                        wait = retry_delay * (2 ** attempt)
                        print(f"API限流，等待 {wait} 秒后重试...")
                        time.sleep(wait)
                        continue
                    else:
                        return {
                            "original": text,
                            "corrected": text,
                            "changes": [f"API请求过于频繁，请稍后再试"],
                            "mode": mode,
                            "error": "rate_limit"
                        }
                else:
                    # 其他错误直接返回
                    return {
                        "original": text,
                        "corrected": text,
                        "changes": [f"处理失败: {error_str}"],
                        "mode": mode,
                        "error": error_str
                    }

        # 不应该到这里
        return {
            "original": text,
            "corrected": text,
            "changes": ["未知错误"],
            "mode": mode
        }


# 全局 AI 服务实例
ai_service = AIService()
