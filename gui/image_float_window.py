"""
图片浮窗 - Snippaste 风格
"""
from PyQt5.QtWidgets import QWidget, QLabel, QApplication, QGraphicsDropShadowEffect, QVBoxLayout
from PyQt5.QtCore import Qt, QPoint, QRect, QSize
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen, QColor, QCursor
from pathlib import Path
from typing import Optional


# 全局窗口列表，防止被垃圾回收
_active_windows = []


class ImageFloatWindow(QWidget):
    """图片浮窗 - Snippaste 风格"""

    # 边缘检测范围
    EDGE_THRESHOLD = 10

    def __init__(self, image_path: str, parent=None):
        super().__init__(parent)

        self.image_path = image_path
        self.drag_start_pos: Optional[QPoint] = None
        self.resize_edge = None
        self.original_pixmap: Optional[QPixmap] = None

        self._init_ui()
        self._load_image()

        # 将窗口添加到全局列表
        _active_windows.append(self)

        print(f"[浮窗] 创建浮窗: {image_path}")

    def _init_ui(self):
        """初始化界面"""
        # 窗口属性 - 不使用透明背景
        self.setWindowFlags(
            Qt.FramelessWindowHint |  # 无边框
            Qt.WindowStaysOnTopHint |  # 置顶
            Qt.Tool  # 工具窗口，不显示在任务栏
        )

        # 设置白色背景
        self.setStyleSheet("background-color: white;")

        # 布局
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # 图片标签
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("border: 2px solid #ccc; background-color: white;")

        layout.addWidget(self.image_label)
        self.setLayout(layout)

    def _load_image(self):
        """加载图片"""
        if Path(self.image_path).exists():
            self.original_pixmap = QPixmap(self.image_path)
            if not self.original_pixmap.isNull():
                # 初始大小
                screen = QApplication.primaryScreen()
                screen_size = screen.availableSize()
                max_size = QSize(int(screen_size.width() * 0.5), int(screen_size.height() * 0.7))

                scaled = self.original_pixmap.scaled(
                    max_size,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.setPixmap(scaled)
                self.resize(scaled.size())

                # 移动到屏幕中心
                self.moveToCenter()
                print(f"[浮窗] 图片加载成功，大小: {scaled.size().width()}x{scaled.size().height()}")
            else:
                self.image_label.setText("图片加载失败")
                print(f"[浮窗] 图片加载失败")
        else:
            self.image_label.setText("图片文件不存在")
            print(f"[浮窗] 图片文件不存在: {self.image_path}")

    def moveToCenter(self):
        """移动窗口到屏幕中心"""
        screen = QApplication.primaryScreen().availableGeometry()
        x = (screen.width() - self.width()) // 2 + screen.x()
        y = (screen.height() - self.height()) // 2 + screen.y()
        self.move(x, y)
        print(f"[浮窗] 窗口位置: ({x}, {y})")

    def setPixmap(self, pixmap: QPixmap):
        """设置图片"""
        self.image_label.setPixmap(pixmap)
        self.image_label.setGeometry(0, 0, pixmap.width(), pixmap.height())

    def mousePressEvent(self, event):
        """鼠标按下"""
        if event.button() == Qt.LeftButton:
            self.drag_start_pos = event.pos()
            self.resize_edge = self._get_resize_edge(event.pos())
            print(f"[浮窗] 鼠标按下: {event.pos()}, 边缘: {self.resize_edge}")

    def mouseMoveEvent(self, event):
        """鼠标移动"""
        if event.buttons() & Qt.LeftButton and self.drag_start_pos:
            if self.resize_edge:
                self._handle_resize(event.pos())
            else:
                # 拖动窗口
                delta = event.pos() - self.drag_start_pos
                new_pos = self.pos() + delta
                self.move(new_pos)

    def mouseReleaseEvent(self, event):
        """鼠标释放"""
        self.drag_start_pos = None
        self.resize_edge = None

    def mouseDoubleClickEvent(self, event):
        """双击关闭"""
        if event.button() == Qt.LeftButton:
            print(f"[浮窗] 双击关闭")
            self.close()
            if self in _active_windows:
                _active_windows.remove(self)

    def _get_resize_edge(self, pos: QPoint) -> Optional[str]:
        """获取鼠标在哪个边缘"""
        x, y = pos.x(), pos.y()
        w, h = self.width(), self.height()

        on_left = x < self.EDGE_THRESHOLD
        on_right = x > w - self.EDGE_THRESHOLD
        on_top = y < self.EDGE_THRESHOLD
        on_bottom = y > h - self.EDGE_THRESHOLD

        if on_top and on_left:
            return 'topleft'
        elif on_top and on_right:
            return 'topright'
        elif on_bottom and on_left:
            return 'bottomleft'
        elif on_bottom and on_right:
            return 'bottomright'
        elif on_top:
            return 'top'
        elif on_bottom:
            return 'bottom'
        elif on_left:
            return 'left'
        elif on_right:
            return 'right'
        return None

    def _handle_resize(self, pos: QPoint):
        """处理调整大小"""
        if not self.original_pixmap:
            return

        x, y = pos.x(), pos.y()
        geometry = self.geometry()

        if 'left' in self.resize_edge:
            new_width = self.width() - (x - self.drag_start_pos.x())
            if new_width > 50:
                new_x = geometry.x() + (x - self.drag_start_pos.x())
                geometry.setX(new_x)
                geometry.setWidth(new_width)

        if 'right' in self.resize_edge:
            new_width = x
            if new_width > 50:
                geometry.setWidth(new_width)

        if 'top' in self.resize_edge:
            new_height = self.height() - (y - self.drag_start_pos.y())
            if new_height > 50:
                new_y = geometry.y() + (y - self.drag_start_pos.y())
                geometry.setY(new_y)
                geometry.setHeight(new_height)

        if 'bottom' in self.resize_edge:
            new_height = y
            if new_height > 50:
                geometry.setHeight(new_height)

        if geometry != self.geometry():
            self.setGeometry(geometry)
            scaled = self.original_pixmap.scaled(
                self.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.setPixmap(scaled)

    def _update_cursor(self, pos: QPoint):
        """更新鼠标样式"""
        edge = self._get_resize_edge(pos)

        if edge in ('topleft', 'bottomright'):
            self.setCursor(Qt.SizeFDiagCursor)
        elif edge in ('topright', 'bottomleft'):
            self.setCursor(Qt.SizeBDiagCursor)
        elif edge in ('top', 'bottom'):
            self.setCursor(Qt.SizeVerCursor)
        elif edge in ('left', 'right'):
            self.setCursor(Qt.SizeHorCursor)
        else:
            self.setCursor(Qt.OpenHandCursor)

    def enterEvent(self, event):
        """鼠标进入"""
        self._update_cursor(self.mapFromGlobal(QCursor.pos()))

    def leaveEvent(self, event):
        """鼠标离开"""
        self.setCursor(Qt.ArrowCursor)

    def showEvent(self, event):
        """显示事件"""
        super().showEvent(event)
        print(f"[浮窗] 窗口已显示，几何信息: {self.geometry()}")
        self.raise_()
        self.activateWindow()


class FloatWindowManager:
    """浮窗管理器"""

    def __init__(self):
        self.windows = []

    def show_image(self, image_path: str):
        """显示图片浮窗"""
        print(f"[浮窗管理器] 显示图片: {image_path}")
        window = ImageFloatWindow(image_path)
        window.show()
        window.raise_()
        window.activateWindow()
        self.windows.append(window)

    def close_all(self):
        """关闭所有浮窗"""
        for window in self.windows:
            window.close()
        self.windows.clear()
        _active_windows.clear()


# 全局管理器实例
float_window_manager = FloatWindowManager()
