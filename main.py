"""
剪贴板智能纠错工具 - 主程序入口
"""
import sys
import os
from PyQt5.QtWidgets import QApplication, QSplashScreen
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont
from pathlib import Path

# 添加项目根目录到路径
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

from config.settings import config
from clipboard_watcher import ClipboardWatcher
from gui import MainWindow, SystemTray
from global_hotkey import global_hotkey
import database


class ClipboardPolisherApp:
    """主应用程序"""

    def __init__(self):
        # 创建应用
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("剪贴板智能纠错工具")
        self.app.setQuitOnLastWindowClosed(False)  # 关闭窗口不退出

        # 设置字体
        font = QFont("Microsoft YaHei", 10)
        self.app.setFont(font)

        # 检查 API Key
        if not config.api_key:
            self._setup_api_key()

        # 创建主窗口
        self.main_window = MainWindow()

        # 创建系统托盘
        self.tray = SystemTray(self.main_window)
        self.tray.setup()
        self.tray.show_requested.connect(self.main_window.show)
        self.tray.quit_requested.connect(self._quit)

        # 创建剪贴板监听器
        self.clipboard_watcher = ClipboardWatcher(self._on_clipboard_change)

        # 设置热键管理器的主窗口引用
        global_hotkey.set_main_window(self.main_window)

        # 显示主窗口
        self.main_window.show()

    def _setup_api_key(self):
        """首次设置 API Key"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton

        dialog = QDialog()
        dialog.setWindowTitle("设置智谱 AI API Key")
        dialog.setMinimumWidth(500)

        layout = QVBoxLayout()

        info = QLabel(
            "欢迎使用剪贴板智能纠错工具！\n\n"
            "未检测到智谱 AI API Key 配置。\n"
            "请输入您的智谱 AI API Key："
        )
        layout.addWidget(info)

        input_field = QLineEdit()
        input_field.setPlaceholderText("7497c5ae5c6c493eba36c24aa1e50a38.xxx...")
        layout.addWidget(input_field)

        def save_key():
            key = input_field.text().strip()
            if key:
                config.save_api_key(key)
                dialog.accept()
            else:
                input_field.setStyleSheet("border: 1px solid red;")

        save_btn = QPushButton("保存")
        save_btn.clicked.connect(save_key)
        layout.addWidget(save_btn)

        dialog.setLayout(layout)
        dialog.exec_()

    def _on_clipboard_change(self, content_type: str, content: str, image_path: str = None):
        """剪贴板内容变化回调"""
        log_path = Path.home() / ".clipboard-polisher" / "main.log"
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(f"\n[DEBUG] _on_clipboard_change called: type={content_type}, len={len(content) if content else 0}\n")

        if not content or len(content) < 2:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(f"[DEBUG] Content too short or empty, returning\n")
            return  # 忽略太短的内容

        print(f"[DEBUG] 剪贴板变化: 类型={content_type}, 内容长度={len(content)}")

        # 保存到数据库
        record_id = database.db.add_record(content_type, content, image_path)
        print(f"[DEBUG] 调用主窗口刷新, record_id={record_id}")
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(f"[DEBUG] Record saved with id={record_id}\n")

        # 通知主窗口
        self.main_window.add_new_record(record_id)
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(f"[DEBUG] add_new_record called\n")

        # 注释掉托盘提示，避免频繁打扰
        # # 显示托盘提示
        # if content_type == "text":
        #     preview = content[:30] + "..." if len(content) > 30 else content
        # else:
        #     preview = "图片内容"
        # self.tray.show_message("已记录剪贴板内容", preview, 0)

    def run(self):
        """运行应用"""
        # 启动剪贴板监听
        self.clipboard_watcher.start()

        # 启动全局热键
        global_hotkey.start()

        # 运行事件循环
        exit_code = self.app.exec_()

        # 停止监听
        self.clipboard_watcher.stop()
        global_hotkey.stop()

        sys.exit(exit_code)

    def _quit(self):
        """退出应用"""
        self.clipboard_watcher.stop()
        self.app.quit()


def main():
    """主函数"""
    app = ClipboardPolisherApp()
    app.run()


if __name__ == "__main__":
    main()
