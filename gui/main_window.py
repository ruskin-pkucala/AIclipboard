"""
主窗口界面
"""
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QListWidget, QListWidgetItem, QPushButton, QLabel,
                             QMenu, QAction, QInputDialog, QMessageBox, QSplitter,
                             QTextEdit, QSystemTrayIcon, QStyle)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QPixmap, QTextDocumentFragment
from typing import List, Dict
from datetime import datetime
from pathlib import Path
import database
from gui.result_window import ResultWindow


class MainWindow(QMainWindow):
    """主窗口"""

    record_added = pyqtSignal()  # 记录添加信号
    refresh_requested = pyqtSignal()  # 刷新请求信号
    show_float_window_requested = pyqtSignal(str)  # 显示浮窗信号

    def __init__(self):
        super().__init__()
        self.records: List[Dict] = []
        self.auto_correct_enabled = True

        self._init_ui()
        self._load_records()

        # 连接信号
        self.record_added.connect(self._on_record_added)
        self.refresh_requested.connect(self._do_refresh)
        self.show_float_window_requested.connect(self._show_float_window_from_signal)

    def _init_ui(self):
        """初始化界面"""
        self.setWindowTitle(" 剪贴板智能纠错工具")
        self.setMinimumSize(800, 600)
        self.resize(1000, 700)

        # 中心部件
        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)

        # 顶部工具栏
        toolbar = QHBoxLayout()

        title = QLabel("剪贴板记录")
        title.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        toolbar.addWidget(title)

        toolbar.addStretch()

        # 清空按钮
        self.clear_btn = QPushButton(" 清空记录")
        self.clear_btn.clicked.connect(self._clear_all)
        toolbar.addWidget(self.clear_btn)

        # 显示浮窗按钮
        self.float_btn = QPushButton(" 📷 显示浮窗")
        self.float_btn.clicked.connect(self._show_float_window)
        self.float_btn.setToolTip("显示最后复制的图片浮窗 (Ctrl+Shift+V)")
        toolbar.addWidget(self.float_btn)

        layout.addLayout(toolbar)

        # 主内容区域（使用分割器）
        splitter = QSplitter(Qt.Horizontal)

        # 左侧：记录列表
        left_panel = QVBoxLayout()
        self.record_list = QListWidget()
        self.record_list.setFont(QFont("Microsoft YaHei", 10))
        self.record_list.itemDoubleClicked.connect(self._open_record)
        self.record_list.itemClicked.connect(self._on_item_clicked)  # 添加单击预览
        self.record_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.record_list.customContextMenuRequested.connect(self._show_context_menu)

        left_panel.addWidget(QLabel("双击查看/纠错:"))
        left_panel.addWidget(self.record_list)

        # 右侧：预览
        right_panel = QVBoxLayout()
        self.preview_label = QLabel("[预览]")
        self.preview_label.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setFont(QFont("Microsoft YaHei", 10))

        right_panel.addWidget(self.preview_label)
        right_panel.addWidget(self.preview_text)

        # 添加到分割器
        left_widget = QWidget()
        left_widget.setLayout(left_panel)
        right_widget = QWidget()
        right_widget.setLayout(right_panel)

        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)

        layout.addWidget(splitter)

        # 底部状态栏
        status_bar = QHBoxLayout()
        self.status_label = QLabel("就绪")
        self.auto_correct_label = QLabel(" 自动纠错: 开启")
        self.auto_correct_btn = QPushButton("切换")
        self.auto_correct_btn.clicked.connect(self._toggle_auto_correct)

        status_bar.addWidget(self.status_label)
        status_bar.addStretch()
        status_bar.addWidget(self.auto_correct_label)
        status_bar.addWidget(self.auto_correct_btn)

        layout.addLayout(status_bar)

        central.setLayout(layout)

    def _load_records(self):
        """加载记录"""
        self.records = database.db.get_recent_records()
        self._refresh_list()

    def _refresh_list(self):
        """刷新列表"""
        self.record_list.clear()

        for i, record in enumerate(self.records):
            content_type = record["content_type"]
            content = record["content"]
            timestamp = record["timestamp"]

            # 格式化时间
            try:
                dt = datetime.fromisoformat(timestamp)
                time_str = dt.strftime("%H:%M:%S")
            except:
                time_str = timestamp

            # 格式化内容
            if content_type == "text":
                preview = content[:50].replace("\n", " ")
                if len(content) > 50:
                    preview += "..."
                icon = "📝"
            else:
                preview = content[:50]
                icon = ""

            # 检查是否已纠错
            status = ""
            if record.get("corrected"):
                status = " "

            item_text = f"[{time_str}] {icon} {preview}{status}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, i)
            self.record_list.addItem(item)

        self.status_label.setText(f"共 {len(self.records)} 条记录")

    def _on_record_added(self):
        """新记录添加"""
        self._load_records()

    def add_new_record(self, record_id: int):
        """添加新记录（由剪贴板监听器调用）"""
        print(f"[DEBUG] 主窗口收到刷新请求, record_id={record_id}")
        # 使用信号触发刷新（线程安全）
        self.refresh_requested.emit()

    def _do_refresh(self):
        """执行刷新"""
        print(f"[DEBUG] 刷新记录列表...")
        self._load_records()
        print(f"[DEBUG] 刷新完成，共 {len(self.records)} 条记录")

    def _on_item_clicked(self, item):
        """列表项单击 - 显示预览"""
        try:
            index = item.data(Qt.UserRole)
            if 0 <= index < len(self.records):
                record = self.records[index]
                content_type = record.get("content_type", "text")
                image_path = record.get("image_path")

                if content_type == "text":
                    # 显示文本预览
                    self.preview_text.setPlainText(record.get("content", ""))
                elif image_path and Path(image_path).exists():
                    # 显示图片预览
                    try:
                        pixmap = QPixmap(str(image_path))
                        if not pixmap.isNull():
                            # 缩放图片以适应预览区域
                            scaled_pixmap = pixmap.scaled(
                                300, 200,
                                Qt.KeepAspectRatio,
                                Qt.SmoothTransformation
                            )
                            # 使用文档片段插入图片
                            document = self.preview_text.document()
                            document.clear()
                            cursor = self.preview_text.textCursor()
                            cursor.insertImage(scaled_pixmap.toImage())
                            # 添加图片路径说明
                            cursor.insertText(f"\n\n图片: {Path(image_path).name}")
                        else:
                            self.preview_text.setPlainText(f"[图片文件已删除: {Path(image_path).name}]")
                    except Exception as e:
                        self.preview_text.setPlainText(f"[图片加载失败: {e}]")
                else:
                    self.preview_text.setPlainText(f"[图片]\n{record.get('content', '')}")
        except Exception as e:
            print(f"预览错误: {e}")
            self.preview_text.setPlainText(f"[预览错误: {e}]")

    def _open_record(self, item):
        """打开记录"""
        index = item.data(Qt.UserRole)
        record = self.records[index]

        window = ResultWindow(record, self)
        window.exec_()

    def _show_context_menu(self, pos):
        """右键菜单"""
        item = self.record_list.itemAt(pos)
        if not item:
            return

        index = item.data(Qt.UserRole)
        record = self.records[index]

        menu = QMenu(self)

        open_action = QAction(" 查看详情", self)
        open_action.triggered.connect(lambda: self._open_record(item))
        menu.addAction(open_action)

        menu.addSeparator()

        delete_action = QAction(" 删除", self)
        delete_action.triggered.connect(lambda: self._delete_record(record["id"]))
        menu.addAction(delete_action)

        menu.exec_(self.record_list.mapToGlobal(pos))

    def _delete_record(self, record_id: int):
        """删除记录"""
        reply = QMessageBox.question(
            self, "确认删除", "确定要删除这条记录吗？",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            database.db.delete_record(record_id)
            self._load_records()

    def _clear_all(self):
        """清空所有记录"""
        reply = QMessageBox.question(
            self, "确认清空", "确定要清空所有记录吗？此操作不可恢复。",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            database.db.clear_all()
            self._load_records()

    def _toggle_auto_correct(self):
        """切换自动纠错"""
        self.auto_correct_enabled = not self.auto_correct_enabled

        if self.auto_correct_enabled:
            self.auto_correct_label.setText(" 自动纠错: 开启")
        else:
            self.auto_correct_label.setText(" 自动纠错: 关闭")

    def _show_float_window(self):
        """显示图片浮窗"""
        # 查找最后一张图片
        last_image_path = None
        for record in reversed(self.records):
            if record.get("content_type") == "image" and record.get("image_path"):
                last_image_path = record.get("image_path")
                break

        if not last_image_path:
            QMessageBox.information(self, "提示", "没有找到图片记录。请先复制一张图片。")
            return

        try:
            from gui.image_float_window import ImageFloatWindow
            window = ImageFloatWindow(last_image_path)
            window.show()
            print(f"[主窗口] 显示浮窗: {last_image_path}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法显示浮窗: {e}")

    def _show_float_window_from_signal(self, image_path: str):
        """从信号显示图片浮窗（在主线程中执行）"""
        try:
            from gui.image_float_window import ImageFloatWindow
            from pathlib import Path
            if Path(image_path).exists():
                window = ImageFloatWindow(image_path)
                window.show()
                print(f"[主窗口] 通过信号显示浮窗: {image_path}")
            else:
                print(f"[主窗口] 图片文件不存在: {image_path}")
        except Exception as e:
            print(f"[主窗口] 显示浮窗失败: {e}")

    def show_preview(self, index: int):
        """显示预览"""
        if 0 <= index < len(self.records):
            record = self.records[index]
            content_type = record["content_type"]

            if content_type == "text":
                self.preview_text.setPlainText(record["content"])
            else:
                self.preview_text.setPlainText(f"[图片]\n{record['content']}")
