"""
剪贴板监听模块 - 最简化版本
"""
import threading
import time
import win32clipboard
import win32con
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional
from PIL import Image
import hashlib
import io


class ClipboardWatcher:
    """剪贴板监听器"""

    def __init__(self, callback: Callable):
        """
        Args:
            callback: 剪贴板变化时的回调函数，接收 (content_type, content, image_path)
        """
        self.callback = callback
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.last_hash = None
        self.image_dir = Path.home() / ".clipboard-polisher" / "images"
        self.image_dir.mkdir(parents=True, exist_ok=True)
        self.last_call_time = 0  # 上次回调时间
        self.call_cooldown = 2.0  # 回调冷却时间（秒）
        self.log_path = Path.home() / ".clipboard-polisher" / "watcher.log"

    def _log(self, message):
        """写入日志"""
        with open(self.log_path, 'a', encoding='utf-8') as f:
            f.write(f"{datetime.now().strftime('%H:%M:%S')} {message}\n")
        print(message)

    def _get_hash(self):
        """获取剪贴板内容的哈希"""
        try:
            win32clipboard.OpenClipboard()

            # 检查格式
            has_text = win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT)
            has_dib = win32clipboard.IsClipboardFormatAvailable(win32con.CF_DIB)

            if has_text:
                content = win32clipboard.GetClipboardData()
                win32clipboard.CloseClipboard()
                return f"text:{hash(content)}", "text", content

            elif has_dib:
                # 获取 DIB 数据
                dib_data = win32clipboard.GetClipboardData(win32con.CF_DIB)
                win32clipboard.CloseClipboard()

                if dib_data:
                    # 使用简单哈希：只取数据长度和前100字节
                    hash_part = dib_data[:100] if len(dib_data) > 100 else dib_data
                    h = f"image:{len(dib_data)}:{hash(hash_part)}"
                    return h, "image", dib_data

            win32clipboard.CloseClipboard()
            return None, None, None

        except Exception as e:
            try:
                win32clipboard.CloseClipboard()
            except:
                pass
            return None, None, None

    def _save_image(self, dib_data):
        """保存图片"""
        try:
            import struct

            # BMP 文件头
            bmp_header = b'BM'
            bmp_header += struct.pack('<I', 0)
            bmp_header += struct.pack('<H', 0)
            bmp_header += struct.pack('<H', 0)
            bmp_header += struct.pack('<I', 54)

            bmp_data = bmp_header + dib_data
            image = Image.open(io.BytesIO(bmp_data))

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            image_path = self.image_dir / f"clip_{timestamp}.png"
            image.save(str(image_path), "PNG")

            return str(image_path)
        except Exception as e:
            self._log(f"保存图片失败: {e}")
            return None

    def _watch_loop(self):
        """监听循环"""
        self._log("剪贴板监听已启动")

        while self.running:
            try:
                current_hash, content_type, content = self._get_hash()

                if not current_hash:
                    time.sleep(0.5)
                    continue

                # 检查哈希是否相同
                if current_hash == self.last_hash:
                    time.sleep(0.5)
                    continue

                # 新内容
                self._log(f"[新内容] 类型={content_type}, 哈希={current_hash[:20]}")
                self.last_hash = current_hash

                # 处理图片
                image_path = None
                if content_type == "image":
                    image_path = self._save_image(content)
                    if image_path:
                        try:
                            from global_hotkey import global_hotkey
                            global_hotkey.set_last_image(image_path)
                            content = f"[图片: {Path(image_path).name}]"
                        except:
                            content = "[图片]"
                else:
                    content = str(content)

                # 检查冷却时间
                current_time = time.time()
                if current_time - self.last_call_time < self.call_cooldown:
                    self._log(f"[冷却] 跳过回调，剩余 {self.call_cooldown - (current_time - self.last_call_time):.1f} 秒")
                    time.sleep(self.call_cooldown - (current_time - self.last_call_time))
                    continue

                # 调用回调
                self._log(f"[回调] 调用回调函数")
                self.last_call_time = time.time()
                self.callback(content_type, content, image_path)

                # 冷却
                time.sleep(0.5)

            except Exception as e:
                self._log(f"监听错误: {e}")
                import traceback
                self._log(traceback.format_exc())
                time.sleep(1)

    def start(self):
        """启动监听"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._watch_loop, daemon=True)
            self.thread.start()
            self._log("剪贴板监听已启动")

    def stop(self):
        """停止监听"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        self._log("剪贴板监听已停止")
