"""
系统托盘图标
"""
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QObject, pyqtSignal


class SystemTray(QObject):
    """系统托盘管理"""

    show_requested = pyqtSignal()
    quit_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tray_icon = None

    def setup(self, icon_path=None):
        """设置托盘图标"""
        self.tray_icon = QSystemTrayIcon(parent=self.parent())

        if icon_path:
            self.tray_icon.setIcon(QIcon(icon_path))
        else:
            # 使用默认图标
            from PyQt5.QtWidgets import QApplication
            app = QApplication.instance()
            style = app.style()
            icon = style.standardIcon(style.SP_FileIcon)
            self.tray_icon.setIcon(icon)

        # 创建菜单
        menu = QMenu()

        show_action = QAction("📋 打开主窗口", self.parent())
        show_action.triggered.connect(self.show_requested.emit)
        menu.addAction(show_action)

        menu.addSeparator()

        quit_action = QAction("❌ 退出", self.parent())
        quit_action.triggered.connect(self.quit_requested.emit)
        menu.addAction(quit_action)

        self.tray_icon.setContextMenu(menu)

        # 双击打开
        self.tray_icon.activated.connect(self._on_activated)

        self.tray_icon.show()

    def _on_activated(self, reason):
        """托盘图标激活"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_requested.emit()

    def show_message(self, title, message, icon=QSystemTrayIcon.Information):
        """显示托盘消息"""
        if self.tray_icon:
            self.tray_icon.showMessage(title, message, icon, 3000)
