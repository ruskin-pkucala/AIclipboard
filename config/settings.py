"""
配置管理模块 - 智谱AI GLM 配置
"""
import os
import json
from pathlib import Path
from typing import Optional

class Config:
    """配置管理器"""

    def __init__(self):
        self.api_key: Optional[str] = None
        self.max_records: int = 50
        self.max_text_length: int = 2000
        self.auto_correct: bool = True
        self.model: str = "glm-4-flash"  # 使用更快的 GLM-4-Flash 模型（响应速度约1-3秒）
        self.load_config()

    def load_config(self):
        """加载配置"""
        # 1. 优先从本地配置文件读取
        config_file = Path.home() / ".clipboard-polisher" / "config.json"
        if config_file.exists():
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.api_key = data.get("api_key")
                    if self.api_key:
                        return self.api_key
            except (json.JSONDecodeError, KeyError):
                pass

        # 2. 从环境变量读取
        self.api_key = os.getenv("ZHIPUAI_API_KEY")
        if self.api_key:
            return self.api_key

        # 3. 返回 None（首次运行时提示用户输入）
        return None

    def save_api_key(self, api_key: str):
        """保存 API Key 到本地配置"""
        config_dir = Path.home() / ".clipboard-polisher"
        config_dir.mkdir(exist_ok=True)
        config_file = config_dir / "config.json"

        with open(config_file, "w", encoding="utf-8") as f:
            json.dump({"api_key": api_key}, f, indent=2, ensure_ascii=False)

        self.api_key = api_key


# 全局配置实例
config = Config()
