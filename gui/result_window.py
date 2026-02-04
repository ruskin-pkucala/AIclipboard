"""
纠错结果弹窗
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTextEdit,
                             QPushButton, QLabel, QComboBox, QSplitter)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QTextCursor
from typing import Dict
import ai_service


class CorrectionWorker(QThread):
    """后台线程执行 AI 纠错"""
    finished = pyqtSignal(dict)  # 纠错完成信号
    error = pyqtSignal(str)  # 错误信号

    def __init__(self, text: str, mode: str):
        super().__init__()
        self.text = text
        self.mode = mode

    def run(self):
        """在后台线程中执行纠错"""
        import traceback
        print(f"[DEBUG] Worker thread started, mode={self.mode}, text_length={len(self.text)}")
        with open('debug_worker.log', 'a', encoding='utf-8') as f:
            f.write(f"\n[DEBUG] Worker thread started, mode={self.mode}, text_length={len(self.text)}\n")
        try:
            result = ai_service.ai_service.correct_text(self.text, self.mode)
            corrected = result.get('corrected', '')
            print(f"[DEBUG] AI service returned, corrected_length={len(corrected)}")
            with open('debug_worker.log', 'a', encoding='utf-8') as f:
                f.write(f"[DEBUG] AI returned, corrected_length={len(corrected)}, preview={corrected[:100] if corrected else 'EMPTY'}\n")
                f.write(f"[DEBUG] About to emit signal...\n")
            self.finished.emit(result)
            with open('debug_worker.log', 'a', encoding='utf-8') as f:
                f.write(f"[DEBUG] Signal emitted\n")
        except Exception as e:
            print(f"[DEBUG] Worker thread error: {e}")
            with open('debug_worker.log', 'a', encoding='utf-8') as f:
                f.write(f"[DEBUG] Exception: {e}\n{traceback.format_exc()}\n")
            self.error.emit(str(e))


class ResultWindow(QDialog):
    """纠错结果窗口"""

    def __init__(self, record_data: Dict, parent=None):
        super().__init__(parent)
        self.record_data = record_data
        self.result_data = None
        self.worker = None  # 后台工作线程

        self.setWindowTitle("文本纠错 / 润色")
        self.setMinimumSize(900, 600)
        self.resize(1000, 700)

        self._init_ui()
        self._load_content()

    def _init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # 顶部工具栏
        toolbar = QHBoxLayout()

        # 模式选择
        self.mode_label = QLabel("处理模式:")
        self.mode_combo = QComboBox()
        # 添加选项（显示文本，数据值）
        modes = [
            ("纯纠错", "correct"),
            ("正式商务", "formal"),
            ("轻松口语", "casual"),
            ("学术专业", "academic"),
            ("简洁明了", "concise"),
            ("创意生动", "creative")
        ]
        for text, value in modes:
            self.mode_combo.addItem(text, value)
        self.mode_combo.setCurrentIndex(0)
        self.mode_combo.currentIndexChanged.connect(self._on_mode_changed)

        toolbar.addWidget(self.mode_label)
        toolbar.addWidget(self.mode_combo)
        toolbar.addStretch()

        # 重新处理按钮
        self.reprocess_btn = QPushButton("[重新处理]")
        self.reprocess_btn.clicked.connect(self._reprocess)
        toolbar.addWidget(self.reprocess_btn)

        layout.addLayout(toolbar)

        # 分割器：原文 vs 纠错后
        splitter = QSplitter(Qt.Horizontal)

        # 左侧：原文
        left_panel = QVBoxLayout()
        left_label = QLabel("[原文]")
        left_label.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        self.original_text = QTextEdit()
        self.original_text.setReadOnly(True)
        self.original_text.setFont(QFont("Microsoft YaHei", 11))
        left_panel.addWidget(left_label)
        left_panel.addWidget(self.original_text)

        # 右侧：纠错后
        right_panel = QVBoxLayout()
        right_label = QLabel("[纠错后]")
        right_label.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        self.corrected_text = QTextEdit()
        self.corrected_text.setFont(QFont("Microsoft YaHei", 11))
        right_panel.addWidget(right_label)
        right_panel.addWidget(self.corrected_text)

        # 添加到分割器
        left_widget = QWidget()
        left_widget.setLayout(left_panel)
        right_widget = QWidget()
        right_widget.setLayout(right_panel)

        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)

        layout.addWidget(splitter)

        # 修改说明（使用QLabel，不可复制）
        self.changes_label = QLabel("[修改说明]")
        self.changes_label.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        layout.addWidget(self.changes_label)

        self.changes_text = QLabel("等待纠错...")
        self.changes_text.setWordWrap(True)
        self.changes_text.setStyleSheet("""
            QLabel {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                color: #666;
            }
        """)
        self.changes_text.setFont(QFont("Microsoft YaHei", 9))
        self.changes_text.setMinimumHeight(60)
        layout.addWidget(self.changes_text)

        # 底部按钮
        btn_layout = QHBoxLayout()

        self.copy_btn = QPushButton("[复制纠错结果]")
        self.copy_btn.clicked.connect(self._copy_result)
        btn_layout.addWidget(self.copy_btn)

        self.close_btn = QPushButton("关闭")
        self.close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.close_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def _load_content(self):
        """加载内容"""
        try:
            original = self.record_data.get("content", "")
            content_type = self.record_data.get("content_type", "text")
            image_path = self.record_data.get("image_path")

            if content_type == "image" and image_path and Path(image_path).exists():
                # 显示图片
                from PyQt5.QtGui import QPixmap
                from pathlib import Path

                try:
                    pixmap = QPixmap(str(image_path))
                    if not pixmap.isNull():
                        # 缩放图片
                        scaled_pixmap = pixmap.scaled(
                            400, 300,
                            Qt.KeepAspectRatio,
                            Qt.SmoothTransformation
                        )
                        document = self.original_text.document()
                        document.clear()
                        cursor = self.original_text.textCursor()
                        cursor.insertImage(scaled_pixmap)
                        cursor.insertText(f"\n\n图片: {Path(image_path).name}")
                    else:
                        self.original_text.setPlainText(f"[图片文件损坏: {Path(image_path).name}]")
                except Exception as e:
                    self.original_text.setPlainText(f"[图片加载失败: {e}]")
            elif content_type == "text":
                # 显示文本
                self.original_text.setPlainText(original)

            # 如果已有纠错结果，直接显示
            corrected = self.record_data.get("corrected")
            if corrected:
                self.corrected_text.setPlainText(corrected)
                self.changes_text.setText("已保存的纠错结果")
            else:
                # 图片不自动执行纠错
                if content_type != "image":
                    QTimer.singleShot(100, self._auto_correct)
                else:
                    self.corrected_text.setPlainText("[图片内容无需文字纠错]")
                    self.changes_text.setText("图片已记录，可使用 Ctrl+Shift+V 粘贴")
        except Exception as e:
            print(f"加载内容错误: {e}")
            self.original_text.setPlainText(f"[加载失败: {e}]")

    def _auto_correct(self):
        """自动执行纠错"""
        mode = self.mode_combo.currentData()
        self._process_with_mode(mode)

    def _on_mode_changed(self):
        """模式改变"""
        # 不自动重新处理，让用户点击按钮
        pass

    def _reprocess(self):
        """重新处理"""
        mode = self.mode_combo.currentData()
        self._process_with_mode(mode)

    def _process_with_mode(self, mode: str):
        """使用指定模式处理"""
        original = self.original_text.toPlainText()
        original = original.replace("[图片内容]\n", "")

        print(f"[DEBUG] _process_with_mode called, mode={mode}, text_length={len(original)}")
        self.corrected_text.setPlainText("[处理中...]")
        self.changes_text.setText("正在分析文本...")

        # 停止之前的 worker（如果存在）
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()

        # 创建后台工作线程
        self.worker = CorrectionWorker(original, mode)
        self.worker.finished.connect(self._on_correction_finished)
        self.worker.error.connect(self._on_correction_error)
        self.worker.start()
        print(f"[DEBUG] Worker thread started")

    def _on_correction_finished(self, result: dict):
        """纠错完成回调"""
        print(f"[DEBUG] _on_correction_finished called")
        with open('debug_worker.log', 'a', encoding='utf-8') as f:
            f.write(f"\n[DEBUG] _on_correction_finished called!\n")
            f.write(f"[DEBUG] Result keys: {list(result.keys())}\n")
        self.result_data = result
        corrected = result.get("corrected", "")
        self.corrected_text.setPlainText(corrected)

        # 显示修改说明
        if result["changes"]:
            changes = "\n".join(f"• {c}" for c in result["changes"])
            self.changes_text.setText(changes)
        else:
            self.changes_text.setText("无需修改")

        # 更新数据库（在主线程中）
        from database import db
        db.update_correction(
            self.record_data["id"],
            corrected,
            "completed"
        )
        with open('debug_worker.log', 'a', encoding='utf-8') as f:
            f.write(f"[DEBUG] Database updated, corrected_length={len(corrected)}\n")
        print(f"[DEBUG] Database updated")

    def _on_correction_error(self, error_msg: str):
        """纠错错误回调"""
        print(f"[DEBUG] _on_correction_error called: {error_msg}")
        self.corrected_text.setPlainText(f"[X] 处理失败: {error_msg}")
        self.changes_text.setText("")

    def _copy_result(self):
        """复制纠错结果"""
        text = self.corrected_text.toPlainText()
        import pyperclip
        pyperclip.copy(text)

        self.copy_btn.setText("[已复制!]")
        QTimer.singleShot(2000, lambda: self.copy_btn.setText("[复制纠错结果]"))

    def closeEvent(self, event):
        """关闭对话框时清理后台线程"""
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
        event.accept()


from PyQt5.QtWidgets import QWidget
