#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
电商订单数据分析平台 — 入口文件
Apple Glassmorphism 启动画面
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication, QSplashScreen, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar
from PyQt5.QtCore import Qt, QTimer, QRect, QPoint
from PyQt5.QtGui import QFont, QPixmap, QColor, QPainter, QLinearGradient, QRadialGradient, QFontDatabase, QPen, QBrush

from ui.main_window import MainWindow


class GlassSplashScreen(QSplashScreen):
    """Apple 毛玻璃风格启动画面"""
    def __init__(self):
        self.pixmap = QPixmap(480, 360)
        self.pixmap.fill(Qt.transparent)
        super().__init__(self.pixmap, Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.progress = 0
        self._draw_frame()
        self._setup_widgets()

    def _draw_frame(self):
        """绘制电影感暗黑科技背景"""
        painter = QPainter(self.pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # 背景渐变（深紫→深青→极黑，电影感）
        gradient = QLinearGradient(0, 0, 480, 360)
        gradient.setColorAt(0.0, QColor("#0a0a0f"))
        gradient.setColorAt(0.4, QColor("#1a0a2e"))
        gradient.setColorAt(0.7, QColor("#0d1f2d"))
        gradient.setColorAt(1.0, QColor("#0a0a0f"))
        painter.fillRect(self.pixmap.rect(), gradient)

        # 霓虹光晕装饰（左上角紫，右下角青）
        glow1 = QRadialGradient(100, 80, 180)
        glow1.setColorAt(0.0, QColor("#b967ff"))
        glow1.setColorAt(1.0, QColor("#b967ff"))
        glow1.setColorAt(0.0, QColor(185, 103, 255, 40))
        glow1.setColorAt(1.0, QColor(185, 103, 255, 0))
        painter.setBrush(QBrush(glow1))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, 360, 360)

        glow2 = QRadialGradient(400, 300, 200)
        glow2.setColorAt(0.0, QColor(0, 212, 170, 35))
        glow2.setColorAt(1.0, QColor(0, 212, 170, 0))
        painter.setBrush(QBrush(glow2))
        painter.drawEllipse(240, 160, 360, 360)

        # 毛玻璃卡片层
        card_rect = QRect(40, 40, 400, 280)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(20, 20, 31, 180)))
        painter.drawRoundedRect(card_rect, 24, 24)

        # 卡片边框霓虹高光
        pen = QPen(QColor(185, 103, 255, 60))
        pen.setWidth(1)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(card_rect, 24, 24)

        # 装饰粒子（霓虹色）
        for i, (x, y, size, color, alpha) in enumerate([
            (60, 70, 8, "#b967ff", 120), (420, 90, 6, "#00d4aa", 80),
            (80, 300, 5, "#ff6b35", 60), (400, 280, 7, "#4facfe", 100),
            (200, 50, 4, "#ff2e63", 70), (350, 320, 5, "#ffd700", 90),
        ]):
            c = QColor(color)
            c.setAlpha(alpha)
            painter.setBrush(QBrush(c))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(x, y, size, size)

        painter.end()
        self.setPixmap(self.pixmap)

    def _setup_widgets(self):
        self.container = QWidget(self)
        self.container.setGeometry(40, 40, 400, 280)
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(16)
        layout.setAlignment(Qt.AlignCenter)

        # 图标/Logo 区域
        icon_label = QLabel("📊")
        icon_label.setStyleSheet("font-size: 48px; background: transparent;")
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)

        # 标题
        title = QLabel("电商订单数据分析平台")
        title.setStyleSheet("""
            color: #e8e8ec;
            font-size: 20px;
            font-weight: 700;
            background: transparent;
            letter-spacing: 0.5px;
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # 副标题
        subtitle = QLabel("E-COMMERCE ANALYTICS PLATFORM")
        subtitle.setStyleSheet("""
            color: #6b6b7b;
            font-size: 10px;
            font-weight: 500;
            background: transparent;
            letter-spacing: 3px;
            font-family: 'SF Mono', 'Courier New', monospace;
        """)
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)

        layout.addSpacing(20)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(4)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: rgba(255, 255, 255, 0.08);
                border-radius: 2px;
            }
            QProgressBar::chunk {
                background-color: #b967ff;
                border-radius: 2px;
            }
        """)
        layout.addWidget(self.progress_bar)

        # 状态文字
        self.status_label = QLabel("正在初始化...")
        self.status_label.setStyleSheet("""
            color: #6b6b7b;
            font-size: 12px;
            font-weight: 500;
            background: transparent;
        """)
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

    def set_progress(self, value, msg=""):
        self.progress = min(value, 100)
        self.progress_bar.setValue(self.progress)
        if msg:
            self.status_label.setText(msg)
        QApplication.instance().processEvents()

    def showMessage(self, message, alignment=Qt.AlignLeft, color=QColor("#ffffff")):
        """重写 showMessage：禁止在 pixmap 上直接绘制，改为更新自定义控件"""
        # 提取消息内容（去除前缀换行和固定标题）
        lines = [line.strip() for line in message.split('\n') if line.strip()]
        # 过滤掉固定标题行
        skip = {"电商订单数据分析平台", "E-Commerce Analytics", "E-Commerce Analytics Platform"}
        state_lines = [l for l in lines if l not in skip]
        if state_lines:
            msg = state_lines[-1]
            # 根据关键词更新进度
            progress_map = {
                "读取": 25, "清洗": 45, "分析": 70, "构建": 90, "完成": 100, "失败": 100
            }
            for key, val in progress_map.items():
                if key in msg:
                    self.set_progress(val, msg)
                    return
            self.status_label.setText(msg)
            QApplication.instance().processEvents()


def main():
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setFont(QFont("-apple-system, BlinkMacSystemFont, SF Pro Text, Microsoft YaHei", 10))

    # 启动画面
    splash = GlassSplashScreen()
    splash.show()
    app.processEvents()

    # 模拟加载进度
    splash.set_progress(20, "正在加载核心模块...")
    QTimer.singleShot(300, lambda: splash.set_progress(45, "正在读取数据..."))
    QTimer.singleShot(600, lambda: splash.set_progress(70, "正在运行分析引擎..."))
    QTimer.singleShot(900, lambda: splash.set_progress(90, "正在构建界面..."))

    # 构建主窗口（内部会同步加载数据）
    window = MainWindow(splash=splash)
    splash.set_progress(100, "就绪")
    window.show()
    splash.finish(window)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
