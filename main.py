#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
电商订单数据分析平台 — 入口文件
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication, QSplashScreen
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap, QColor

from ui.main_window import MainWindow


def main():
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setFont(QFont("Microsoft YaHei", 10))

    # 启动画面
    splash_pix = QPixmap(400, 300)
    splash_pix.fill(QColor("#0f172a"))
    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    splash.showMessage(
        "\n\n  电商订单数据分析平台\n  E-Commerce Analytics\n\n  正在加载数据...",
        Qt.AlignCenter | Qt.AlignTop,
        QColor("#f8fafc")
    )
    splash.show()
    app.processEvents()

    # 构建主窗口（内部会同步加载数据）
    window = MainWindow(splash=splash)
    window.show()
    splash.finish(window)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
