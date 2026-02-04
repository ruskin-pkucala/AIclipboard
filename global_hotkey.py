"""
全局热键管理 - 使用 keyboard 库
"""
from pathlib import Path
from typing import Optional


class GlobalHotkeyManager:
    """全局热键管理器"""

    def __init__(self):
        self.last_image_path: Optional[str] = None
        self.running = False
        self.log_path = Path.home() / ".clipboard-polisher" / "hotkey.log"
        self.main_window = None  # 主窗口引用

    def set_main_window(self, main_window):
        """设置主窗口引用"""
        self.main_window = main_window
        self._log("主窗口引用已设置")

    def _log(self, message):
        """写入日志"""
        with open(self.log_path, 'a', encoding='utf-8') as f:
            f.write(f"{message}\n")
        print(f"[热键] {message}")

    def set_last_image(self, image_path: str):
        """设置最近的图片路径"""
        self.last_image_path = image_path
        self._log(f"图片路径已更新: {image_path}")

    def _show_image_float(self):
        """显示图片浮窗 - 通过信号"""
        if not self.last_image_path:
            self._log("没有可显示的图片")
            return

        if not Path(self.last_image_path).exists():
            self._log(f"图片文件不存在: {self.last_image_path}")
            return

        if self.main_window:
            # 通过信号在主线程中创建窗口
            self.main_window.show_float_window_requested.emit(self.last_image_path)
            self._log(f"触发显示浮窗信号: {Path(self.last_image_path).name}")
        else:
            self._log("主窗口引用未设置，无法显示浮窗")

    def start(self):
        """启动热键监听"""
        try:
            import keyboard

            # 注册全局热键
            keyboard.add_hotkey('ctrl+shift+v', self._show_image_float)
            self.running = True
            self._log("全局热键已注册: Ctrl+Shift+V (显示图片浮窗)")
        except ImportError:
            self._log("keyboard 库未安装，尝试使用 pynput...")
            self._start_with_pynput()
        except Exception as e:
            self._log(f"注册热键失败: {e}")
            import traceback
            self._log(traceback.format_exc())

    def _start_with_pynput(self):
        """使用 pynput 作为备用方案"""
        try:
            from pynput import keyboard

            def on_activate():
                self._log("热键触发 (pynput)")
                self._show_image_float()

            # 创建热键监听器
            hotkey = keyboard.HotKey(
                keyboard.HotKey.parse('<ctrl>+<shift>+v'),
                on_activate
            )

            # 启动监听
            listener = keyboard.Listener(
                on_press=hotkey.press,
                on_release=hotkey.release
            )
            listener.start()
            self.running = True
            self._log("热键监听器已启动 (使用 pynput)")
        except Exception as e:
            self._log(f"pynput 也失败了: {e}")

    def stop(self):
        """停止热键监听"""
        if self.running:
            try:
                import keyboard
                keyboard.remove_hotkey('ctrl+shift+v')
            except:
                pass
            self.running = False


# 全局热键管理器实例
global_hotkey = GlobalHotkeyManager()
