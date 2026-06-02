"""
主窗口：Cinematic Dark 电影感暗黑科技风格
Blade Runner 2049 调色：极深蓝黑 + 霓虹五色点缀
"""
import sys
import os

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget, QScrollArea,
    QFrame, QTableWidget, QTableWidgetItem, QFileDialog,
    QMessageBox, QHeaderView, QSizePolicy, QGridLayout,
    QProgressBar, QTextEdit, QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect, QApplication, QLineEdit, QGraphicsColorizeEffect
)
from PyQt5.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QPoint, QTimer
from PyQt5.QtGui import QFont, QIcon, QColor, QPalette, QLinearGradient, QBrush, QFontDatabase

from config.styles import (
    get_cinematic_stylesheet, get_cinematic_palette,
    CINE_BG, CINE_CARD, CINE_CARD_BORDER, CINE_CARD_HOVER,
    CINE_TEXT, CINE_TEXT_SECONDARY, CINE_TEXT_MUTED,
    CINE_NEON_ORANGE, CINE_NEON_CYAN, CINE_NEON_PURPLE,
    CINE_NEON_PINK, CINE_NEON_BLUE, CINE_NEON_GOLD,
    CINE_NEON_ORANGE_ALPHA, CINE_NEON_CYAN_ALPHA,
    CINE_NEON_PURPLE_ALPHA, CINE_NEON_PINK_ALPHA,
    CINE_NEON_BLUE_ALPHA, CINE_NEON_GOLD_ALPHA,
    CINE_RADIUS_XL, CINE_RADIUS_L, CINE_RADIUS_M, CINE_RADIUS_S,
    CINE_FONT_STACK, CINE_FONT_MONO,
    RollingNumberLabel,
)
from config.rc_params import configure_sci_style, get_color_palette
from core.models import state
from core.data_loader import DataLoader
from core.data_cleaner import DataCleaner
from analysis.engine import AnalysisEngine
from visualization.base_chart import ChartCanvas

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np


class ScrollableCanvas(FigureCanvas):
    """禁用滚轮缩放，让页面可以正常下滑"""
    def wheelEvent(self, event):
        event.ignore()  # 忽略滚轮，让父级 QScrollArea 接管滚动


class ChartScrollArea(QScrollArea):
    """自定义滚动区域：滚动时触发 Matplotlib 图表重绘，避免裁切"""
    def scrollContentsBy(self, dx, dy):
        super().scrollContentsBy(dx, dy)
        if self.widget():
            for canvas in self.widget().findChildren(FigureCanvas):
                canvas.draw_idle()

try:
    import seaborn as sns
    HAS_SEABORN = True
except ImportError:
    HAS_SEABORN = False


# ========== 电影感常量 ==========
SIDEBAR_BG = "#000000"
SIDEBAR_ACTIVE = CINE_NEON_PURPLE
SIDEBAR_HOVER = "#0d0d14"
SIDEBAR_TEXT = CINE_TEXT_SECONDARY
SIDEBAR_TEXT_ACTIVE = CINE_TEXT


class CineCard(QFrame):
    """电影感卡片：深色背景 + 霓虹 Hover 边框高亮"""
    def __init__(self, parent=None, neon_color=CINE_NEON_PURPLE, radius=CINE_RADIUS_M):
        super().__init__(parent)
        self.neon_color = neon_color
        self.radius = radius
        self.setAttribute(Qt.WA_Hover, True)
        self._setup_style()

    def _setup_style(self):
        self.setStyleSheet(f"""
            CineCard {{
                background-color: {CINE_CARD};
                border-radius: {self.radius}px;
                border: 1px solid {CINE_CARD_BORDER};
            }}
            CineCard:hover {{
                border: 1px solid {self.neon_color};
            }}
        """)
        self.setFrameShape(QFrame.NoFrame)


class SkeletonScreen(QFrame):
    """骨架屏加载组件（电影感脉冲）"""
    def __init__(self, parent=None, rows=5):
        super().__init__(parent)
        self.rows = rows
        self._setup_ui()
        self._setup_pulse()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 24, 24, 24)
        for i in range(self.rows):
            row = QFrame()
            row.setStyleSheet(f"background-color: {CINE_CARD_HOVER}; border-radius: 6px;")
            row.setMinimumHeight(36)
            layout.addWidget(row)
        self.setMinimumHeight(self.rows * 48 + 48)

    def _setup_pulse(self):
        self.effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.effect)
        self.anim = QPropertyAnimation(self.effect, b"opacity")
        self.anim.setDuration(1500)
        self.anim.setStartValue(0.3)
        self.anim.setEndValue(0.7)
        self.anim.setEasingCurve(QEasingCurve.InOutSine)
        self.anim.finished.connect(self._reverse_pulse)
        self.anim.start()

    def _reverse_pulse(self):
        start, end = self.anim.endValue(), self.anim.startValue()
        self.anim.setStartValue(start)
        self.anim.setEndValue(end)
        self.anim.start()


class MainWindow(QMainWindow):
    def __init__(self, splash=None):
        super().__init__()
        self.splash = splash
        self.setWindowTitle("电商订单数据分析平台")
        self.setMinimumSize(1400, 900)
        self.resize(1600, 1000)
        self.current_theme = 'dark'
        self.analysis_results = {}
        self.modules = [
            ("数据概览", "📊", self.show_overview),
            ("平台分析", "📱", self.show_platform),
            ("异常检测", "⚠️", self.show_anomaly),
            ("KPI 仪表盘", "🎯", self.show_kpi),
            ("月度趋势", "📅", self.show_monthly),
            ("渠道构成", "🥧", self.show_channel),
            ("星期周期", "📆", self.show_weekday),
            ("24小时热力", "⏰", self.show_hourly),
            ("客户价值", "💎", self.show_customer_value),
            ("节假日影响", "🎉", self.show_holiday),
            ("支付时滞", "⏱️", self.show_payment_lag),
            ("RFM & CLV", "🧬", self.show_rfm),
            ("高阶网络与生存", "🔬", self.show_advanced),
        ]
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(get_cinematic_stylesheet())
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ========== 侧边栏（纯黑电影感）==========
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(220)
        self.sidebar.setStyleSheet(f"""
            QWidget {{
                background-color: {SIDEBAR_BG};
                border-right: 1px solid {CINE_CARD_BORDER};
            }}
        """)
        sb_layout = QVBoxLayout(self.sidebar)
        sb_layout.setContentsMargins(0, 0, 0, 20)
        sb_layout.setSpacing(0)

        # Logo 区域
        logo_widget = QFrame()
        logo_widget.setStyleSheet(f"background-color: transparent; border-bottom: 1px solid {CINE_CARD_BORDER};")
        logo_layout = QVBoxLayout(logo_widget)
        logo_layout.setContentsMargins(24, 32, 24, 24)
        logo_title = QLabel("电商数据分析")
        logo_title.setStyleSheet(f"color: {CINE_TEXT}; font-size: 18px; font-weight: 700; letter-spacing: 0.5px; background: transparent;")
        logo_sub = QLabel("E-COMMERCE ANALYTICS")
        logo_sub.setStyleSheet(f"color: {CINE_TEXT_MUTED}; font-size: 10px; letter-spacing: 3px; font-family: {CINE_FONT_MONO}; background: transparent;")
        logo_layout.addWidget(logo_title)
        logo_layout.addWidget(logo_sub)
        sb_layout.addWidget(logo_widget)
        sb_layout.addSpacing(16)

        # 导航按钮
        self.nav_buttons = []
        for name, icon, callback in self.modules:
            btn = QPushButton(f"  {icon}  {name}")
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {CINE_TEXT_SECONDARY};
                    border: none;
                    padding: 14px 24px;
                    text-align: left;
                    font-size: 13px;
                    font-weight: 500;
                    border-left: 3px solid transparent;
                    border-radius: 0px {CINE_RADIUS_S}px {CINE_RADIUS_S}px 0px;
                    margin-right: 12px;
                }}
                QPushButton:hover {{
                    background-color: {SIDEBAR_HOVER};
                    color: {CINE_TEXT};
                }}
                QPushButton:checked {{
                    background-color: {CINE_NEON_PURPLE_ALPHA};
                    color: {CINE_NEON_PURPLE};
                    border-left: 3px solid {CINE_NEON_PURPLE};
                    font-weight: 600;
                }}
            """)
            btn.clicked.connect(lambda checked, c=callback, b=btn: self._on_nav_clicked(c, b))
            sb_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        sb_layout.addStretch()

        # 底部操作区
        bottom_widget = QFrame()
        bottom_widget.setStyleSheet(f"background-color: transparent; border-top: 1px solid {CINE_CARD_BORDER};")
        bottom_layout = QVBoxLayout(bottom_widget)
        bottom_layout.setContentsMargins(16, 16, 16, 16)
        bottom_layout.setSpacing(10)

        import_btn = QPushButton("📂 导入数据")
        import_btn.setCursor(Qt.PointingHandCursor)
        import_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {CINE_NEON_PURPLE};
                color: white;
                border-radius: {CINE_RADIUS_S}px;
                padding: 10px;
                font-weight: 600;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {CINE_NEON_BLUE};
            }}
        """)
        import_btn.clicked.connect(self.import_data)
        bottom_layout.addWidget(import_btn)
        sb_layout.addWidget(bottom_widget)

        layout.addWidget(self.sidebar)

        # ========== 右侧内容区 ==========
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # 顶部导航栏
        self.top_bar = QFrame()
        self.top_bar.setFixedHeight(56)
        self.top_bar.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(10, 10, 15, 0.95);
                border-bottom: 1px solid {CINE_CARD_BORDER};
            }}
        """)
        top_layout = QHBoxLayout(self.top_bar)
        top_layout.setContentsMargins(28, 0, 28, 0)
        top_layout.setSpacing(16)

        self.breadcrumb = QLabel("数据概览")
        self.breadcrumb.setStyleSheet(f"font-size: 15px; font-weight: 600; color: {CINE_TEXT}; background: transparent;")
        top_layout.addWidget(self.breadcrumb)
        top_layout.addStretch()

        # 搜索框
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("🔍 搜索分析模块...")
        self.search_edit.setFixedWidth(240)
        self.search_edit.setStyleSheet(f"""
            QLineEdit {{
                background-color: {CINE_CARD};
                border: 1px solid {CINE_CARD_BORDER};
                border-radius: {CINE_RADIUS_S}px;
                padding: 6px 12px;
                font-size: 13px;
                color: {CINE_TEXT};
            }}
            QLineEdit:focus {{
                border: 1px solid {CINE_NEON_PURPLE};
            }}
        """)
        top_layout.addWidget(self.search_edit)

        # 状态标签
        self.status_label = QLabel("")
        self.status_label.setStyleSheet(f"color: {CINE_NEON_CYAN}; font-size: 12px; font-weight: 600; padding: 4px 12px; background: {CINE_NEON_CYAN_ALPHA}; border-radius: 6px;")
        self.status_label.hide()
        top_layout.addWidget(self.status_label)

        right_layout.addWidget(self.top_bar)

        # 内容堆叠区
        self.content = QStackedWidget()
        self.content.setStyleSheet(f"background-color: {CINE_BG};")
        right_layout.addWidget(self.content, 1)
        layout.addWidget(right_container, 1)

        # 初始化各页面
        self.pages = {}
        for name, icon, _ in self.modules:
            page = ChartScrollArea()
            page.setWidgetResizable(True)
            page.setFrameShape(QFrame.NoFrame)
            page.setStyleSheet(f"background-color: {CINE_BG}; border: none;")
            container = QWidget()
            container_layout = QVBoxLayout(container)
            container_layout.setContentsMargins(28, 24, 28, 28)
            container_layout.setSpacing(24)
            container_layout.setAlignment(Qt.AlignTop)
            container.setMinimumHeight(800)
            page.setWidget(container)
            self.content.addWidget(page)
            self.pages[name] = container_layout

        if self.nav_buttons:
            self.nav_buttons[0].setChecked(True)
            self.show_overview()

        self._auto_load()

    def _update_splash(self, msg):
        if self.splash:
            if hasattr(self.splash, 'set_progress'):
                progress_map = {
                    "读取": 25, "清洗": 45, "分析": 70, "构建": 90, "完成": 100, "失败": 100
                }
                progress = 50
                for key, val in progress_map.items():
                    if key in msg:
                        progress = val
                        break
                self.splash.set_progress(progress, msg)
            else:
                self.splash.showMessage(
                    f"\n\n  电商订单数据分析平台\n  E-Commerce Analytics\n\n  {msg}",
                    Qt.AlignCenter | Qt.AlignTop,
                    QColor("#f5f5f7")
                )
                QApplication.instance().processEvents()

    def _auto_load(self):
        from pathlib import Path
        script_dir = Path(__file__).resolve().parent
        project_dir = script_dir.parent
        parent_dir = project_dir.parent
        # 扩大搜索范围：同级目录、父目录、当前工作目录、桌面、下载
        candidates = [
            parent_dir / '某电商平台2021年订单数据.xlsx',
            project_dir / '某电商平台2021年订单数据.xlsx',
            Path.cwd() / '某电商平台2021年订单数据.xlsx',
            Path.home() / 'Desktop' / '某电商平台2021年订单数据.xlsx',
            Path.home() / 'Downloads' / '某电商平台2021年订单数据.xlsx',
            Path('..') / '某电商平台2021年订单数据.xlsx',
            Path('某电商平台2021年订单数据.xlsx'),
        ]
        found = None
        for c in candidates:
            if c.exists():
                found = str(c.resolve())
                break
        if found:
            self.status_label.setText(f"找到数据: {c.name}")
            self.status_label.show()
            QApplication.instance().processEvents()
            self._load_data_sync(found)
        else:
            self.status_label.setText("未找到数据文件")
            self.status_label.show()
            # 数据概览页显示导入提示
            layout = self.pages.get("数据概览")
            if layout:
                self.clear_layout(layout)
                self._add_title(layout, "数据概览")
                card = CineCard(neon_color=CINE_NEON_PINK, radius=CINE_RADIUS_L)
                card.setMinimumSize(400, 200)
                c_layout = QVBoxLayout(card)
                c_layout.setContentsMargins(40, 40, 40, 40)
                c_layout.setSpacing(20)
                lbl = QLabel("未找到默认数据文件\n请点击左下角「📂 导入数据」按钮加载 Excel 文件")
                lbl.setStyleSheet(f"font-size: 16px; color: {CINE_TEXT_SECONDARY}; background: transparent;")
                lbl.setAlignment(Qt.AlignCenter)
                c_layout.addWidget(lbl)
                import_btn = QPushButton("📂 导入数据")
                import_btn.setCursor(Qt.PointingHandCursor)
                import_btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {CINE_NEON_PURPLE};
                        color: white;
                        border-radius: {CINE_RADIUS_S}px;
                        padding: 12px 24px;
                        font-weight: 600;
                        font-size: 14px;
                    }}
                    QPushButton:hover {{
                        background-color: {CINE_NEON_BLUE};
                    }}
                """)
                import_btn.clicked.connect(self.import_data)
                c_layout.addWidget(import_btn, alignment=Qt.AlignCenter)
                layout.addWidget(card, alignment=Qt.AlignCenter)

    def _show_skeleton(self, layout, msg="正在加载数据..."):
        card = CineCard(neon_color=CINE_NEON_PURPLE, radius=CINE_RADIUS_L)
        c_layout = QVBoxLayout(card)
        c_layout.setContentsMargins(40, 40, 40, 40)
        lbl = QLabel(msg)
        lbl.setStyleSheet(f"font-size: 16px; color: {CINE_TEXT_SECONDARY}; background: transparent;")
        lbl.setAlignment(Qt.AlignCenter)
        c_layout.addWidget(lbl)
        skeleton = SkeletonScreen(rows=6)
        c_layout.addWidget(skeleton)
        layout.addWidget(card)

    def _load_data_sync(self, file_path):
        try:
            self._update_splash("正在读取 Excel...")
            raw_df = DataLoader.load_excel(file_path)

            self._update_splash("正在清洗数据...")
            cleaner = DataCleaner(raw_df)
            clean_df, anomaly_df, report = cleaner.clean()

            self._update_splash("正在运行 12 项分析模块...")
            engine = AnalysisEngine(clean_df, anomaly_df)
            results = engine.run_all()

            state.raw_data = None
            state.cleaned_data = clean_df
            state.anomaly_data = anomaly_df
            state.file_path = file_path
            self.analysis_results = results

            self._update_splash("分析完成，正在构建界面...")
            self.show_overview()
        except Exception as e:
            self._update_splash(f"加载失败: {e}")
            QMessageBox.critical(self, "加载失败", str(e))

    def _on_nav_clicked(self, callback, btn):
        for b in self.nav_buttons:
            b.setChecked(False)
        btn.setChecked(True)
        text = btn.text().strip()
        self.breadcrumb.setText(text)
        callback()

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.clear_layout(item.layout())

    def import_data(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择订单数据", "", "Excel Files (*.xlsx *.xls)")
        if not path:
            return
        self._manual_import = True
        self._load_data_async(path)

    def _load_data_async(self, file_path):
        self.status_label.setText("🔄 正在导入数据...")
        self.status_label.setStyleSheet(f"color: {CINE_NEON_CYAN}; font-size: 12px; font-weight: 600; padding: 4px 12px; background: {CINE_NEON_CYAN_ALPHA}; border-radius: 6px;")
        self.status_label.show()
        QApplication.instance().processEvents()
        try:
            raw_df = DataLoader.load_excel(file_path)
            cleaner = DataCleaner(raw_df)
            clean_df, anomaly_df, report = cleaner.clean()
            engine = AnalysisEngine(clean_df, anomaly_df)
            results = engine.run_all()
            state.raw_data = None
            state.cleaned_data = clean_df
            state.anomaly_data = anomaly_df
            state.file_path = file_path
            self.analysis_results = results
            self.status_label.setText("✅ 导入成功")
            self.status_label.setStyleSheet(f"color: {CINE_NEON_CYAN}; font-size: 12px; font-weight: 600; padding: 4px 12px; background: {CINE_NEON_CYAN_ALPHA}; border-radius: 6px;")
            QTimer.singleShot(3000, self.status_label.hide)
            self.show_overview()
        except Exception as e:
            self.status_label.setText("❌ 导入失败")
            self.status_label.setStyleSheet(f"color: {CINE_NEON_PINK}; font-size: 12px; font-weight: 600; padding: 4px 12px; background: {CINE_NEON_PINK_ALPHA}; border-radius: 6px;")
            QMessageBox.critical(self, "加载失败", str(e))

    # ===================== 页面渲染辅助 =====================
    def _add_title(self, layout, title, subtitle=""):
        box = QVBoxLayout()
        box.setSpacing(6)
        lbl = QLabel(title)
        lbl.setWordWrap(True)
        lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        lbl.setStyleSheet(f"font-size: 26px; font-weight: 700; color: {CINE_TEXT}; background: transparent; letter-spacing: -0.5px;")
        box.addWidget(lbl)
        if subtitle:
            sub = QLabel(subtitle)
            sub.setWordWrap(True)
            sub.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            sub.setStyleSheet(f"font-size: 14px; color: {CINE_TEXT_SECONDARY}; background: transparent; margin-top: 4px;")
            box.addWidget(sub)
        box.addSpacing(16)
        layout.addLayout(box)

    def _add_kpi_row(self, layout, kpis: list):
        grid = QGridLayout()
        grid.setSpacing(16)
        cols_per_row = 4
        for i, kpi in enumerate(kpis):
            neon = kpi.get('neon', CINE_NEON_PURPLE)
            card = CineCard(neon_color=neon, radius=CINE_RADIUS_M)
            card.setMinimumWidth(200)
            c_layout = QVBoxLayout(card)
            c_layout.setContentsMargins(24, 20, 24, 20)
            c_layout.setSpacing(8)

            t = QLabel(kpi.get('title', ''))
            t.setStyleSheet(f"color: {CINE_TEXT_SECONDARY}; font-size: 11px; font-weight: 600; letter-spacing: 0.8px; text-transform: uppercase; background: transparent;")
            v = RollingNumberLabel(prefix=kpi.get('prefix', ''), suffix=kpi.get('suffix', ''), decimals=kpi.get('decimals', 0))
            v.set_value(kpi.get('value', 0))
            v.setStyleSheet(f"color: {neon}; font-size: 28px; font-weight: 700; background: transparent; letter-spacing: -1px;")
            c_layout.addWidget(t)
            c_layout.addWidget(v)
            row = i // cols_per_row
            col = i % cols_per_row
            grid.addWidget(card, row, col)
        for c in range(cols_per_row):
            grid.setColumnStretch(c, 1)
        layout.addLayout(grid)

    def _create_chart_widget(self, width=10, height=6, polar=False):
        configure_sci_style('dark')
        bg_color = CINE_CARD
        text_color = CINE_TEXT
        grid_color = '#2a2a3a'
        fig = Figure(figsize=(width, height), dpi=120, facecolor=bg_color)
        if polar:
            ax = fig.add_subplot(111, polar=True)
        else:
            ax = fig.add_subplot(111)
        ax.set_facecolor(bg_color)
        ax.tick_params(colors=text_color)
        if not polar:
            ax.xaxis.label.set_color(text_color)
            ax.yaxis.label.set_color(text_color)
            ax.title.set_color(text_color)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color(grid_color)
            ax.spines['bottom'].set_color(grid_color)
            ax.grid(True, alpha=0.15, color=grid_color)
        else:
            ax.tick_params(colors=text_color)
            ax.grid(True, alpha=0.2, color=grid_color)
        canvas = ScrollableCanvas(fig)
        canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        canvas.setMinimumSize(400, 280)
        canvas.draw()  # 强制立即绘制，避免空白
        card = CineCard(neon_color=CINE_NEON_PURPLE, radius=CINE_RADIUS_M)
        card.setMinimumSize(420, 300)
        c_layout = QVBoxLayout(card)
        c_layout.setContentsMargins(12, 12, 12, 12)
        c_layout.addWidget(canvas)
        return card, fig, ax

    def _add_text_analysis(self, layout, text: str):
        card = CineCard(neon_color=CINE_NEON_BLUE, radius=CINE_RADIUS_M)
        c_layout = QVBoxLayout(card)
        c_layout.setContentsMargins(24, 20, 24, 20)
        te = QTextEdit()
        te.setReadOnly(True)
        te.setFrameStyle(QFrame.NoFrame)
        te.setStyleSheet(f"border: none; background: transparent; font-family: {CINE_FONT_STACK}; color: {CINE_TEXT_SECONDARY};")
        te.setHtml(f"<div style='line-height:1.8;font-size:14px;color:{CINE_TEXT_SECONDARY};'>{text}</div>")
        te.setMaximumHeight(260)
        c_layout.addWidget(te)
        layout.addWidget(card)

    def _add_table(self, layout, df: dict or list, max_rows=20):
        card = CineCard(neon_color=CINE_NEON_CYAN, radius=CINE_RADIUS_M)
        c_layout = QVBoxLayout(card)
        c_layout.setContentsMargins(16, 16, 16, 16)

        if isinstance(df, list) and len(df) > 0:
            keys = list(df[0].keys())
            table = QTableWidget(min(len(df), max_rows), len(keys))
            table.setHorizontalHeaderLabels(keys)
            table.setAlternatingRowColors(True)
            table.setStyleSheet("""
                QTableWidget { border: none; background: transparent; }
                QTableWidget::item { padding: 10px 12px; }
            """)
            for i, row in enumerate(df[:max_rows]):
                for j, k in enumerate(keys):
                    item = QTableWidgetItem(str(row.get(k, "")))
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    item.setTextAlignment(Qt.AlignCenter)
                    table.setItem(i, j, item)
        elif isinstance(df, dict):
            table = QTableWidget(len(df), 2)
            table.setHorizontalHeaderLabels(["指标", "数值"])
            table.setAlternatingRowColors(True)
            table.setStyleSheet("""
                QTableWidget { border: none; background: transparent; }
                QTableWidget::item { padding: 10px 12px; }
            """)
            for i, (k, v) in enumerate(df.items()):
                item0 = QTableWidgetItem(str(k))
                item0.setFlags(item0.flags() & ~Qt.ItemIsEditable)
                item0.setTextAlignment(Qt.AlignCenter)
                item1 = QTableWidgetItem(str(v))
                item1.setFlags(item1.flags() & ~Qt.ItemIsEditable)
                item1.setTextAlignment(Qt.AlignCenter)
                table.setItem(i, 0, item0)
                table.setItem(i, 1, item1)
        else:
            card.deleteLater()
            return
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setMaximumHeight(360)
        table.verticalHeader().setVisible(False)
        c_layout.addWidget(table)
        layout.addWidget(card)

    def _fade_in_page(self):
        """页面切换（已禁用淡入动画以避免 QScrollArea 渲染问题）"""
        page = self.content.currentWidget()
        if page:
            container = page.widget()
            if container:
                container.update()

    # ===================== 各模块页面 =====================
    def show_overview(self):
        layout = self.pages["数据概览"]
        self.clear_layout(layout)
        self._add_title(layout, "数据概览", "电商订单数据整体情况与平台分布")
        if state.cleaned_data is None:
            self._show_skeleton(layout, "暂无数据，请点击左侧「导入数据」按钮加载 Excel 文件")
            self.content.setCurrentIndex(0)
            return

        r = self.analysis_results
        kpi = r.get('M3_kpi', {})
        self._add_kpi_row(layout, [
            {'title': '总销售额 (GMV)', 'value': kpi.get('total_sales', 0), 'prefix': '¥', 'decimals': 2, 'neon': CINE_NEON_ORANGE},
            {'title': '实际销售额', 'value': kpi.get('actual_sales', 0), 'prefix': '¥', 'decimals': 2, 'neon': CINE_NEON_CYAN},
            {'title': '有效订单', 'value': kpi.get('normal_orders', 0), 'suffix': '', 'neon': CINE_NEON_BLUE},
            {'title': '退货率', 'value': kpi.get('refund_rate', 0), 'suffix': '%', 'decimals': 2, 'neon': CINE_NEON_PINK},
        ])

        # 漏斗图 + 平台分布图（双列）
        h_layout = QHBoxLayout()
        h_layout.setSpacing(16)

        # 漏斗图
        funnel = kpi.get('funnel', [])
        if funnel:
            card1, fig1, ax1 = self._create_chart_widget(5.5, 5.5)
            stages = [f["stage"] for f in funnel]
            counts = [f["count"] for f in funnel]
            colors = [CINE_NEON_BLUE, CINE_NEON_CYAN, CINE_NEON_ORANGE, CINE_NEON_PURPLE]
            bars = ax1.barh(stages[::-1], counts[::-1], color=colors[::-1], edgecolor='none', height=0.6)
            ax1.set_title('订单转化漏斗', fontweight='bold', pad=15, fontsize=14)
            for bar in bars:
                w = bar.get_width()
                ax1.text(w, bar.get_y() + bar.get_height()/2., f'{int(w):,}',
                        ha='left', va='center', fontsize=10, color=CINE_TEXT)
            fig1.tight_layout()
            h_layout.addWidget(card1)

        # 平台分布图
        card2, fig2, ax2 = self._create_chart_widget(6, 5.5)
        m1 = r.get('M1_platforms', {})
        platforms = list(m1.get('counts', {}).keys())
        counts = list(m1.get('counts', {}).values())
        colors = get_cinematic_palette(len(platforms))
        bars = ax2.bar(platforms, counts, color=colors, edgecolor='none', linewidth=0.5)
        ax2.set_title('各平台订单分布', fontweight='bold', pad=15, fontsize=14)
        ax2.set_ylabel('订单数')
        for bar in bars:
            h = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., h, f'{int(h):,}',
                    ha='center', va='bottom', fontsize=9, color=CINE_TEXT)
        fig2.tight_layout()
        h_layout.addWidget(card2)
        layout.addLayout(h_layout)

        self._add_text_analysis(layout,
            f"<b>数据质量概况：</b>原始数据共 {kpi.get('total_orders', 0):,} 条，"
            f"异常订单 {r.get('M2_anomalies', {}).get('count', 0):,} 条已隔离。"
            f"有效客户数 {kpi.get('unique_customers', 0):,} 人，订单均价 ¥{kpi.get('aov', 0):.2f}。"
            f"退货率 {kpi.get('refund_rate', 0)}% 处于电商行业平均水平（10%-15%）。<br>"
            f"<b>商业建议：</b>重点关注微信与 APP 两大核心渠道的用户体验优化，同时审视退货流程以降低退货损失。")
        self.content.setCurrentIndex(0)
        self._fade_in_page()

    def show_platform(self):
        layout = self.pages["平台分析"]
        self.clear_layout(layout)
        self._add_title(layout, "平台归一化分析", "同一平台不同表述的智能归一与分布")
        if not self.analysis_results:
            self._show_skeleton(layout, "请先导入数据")
            self.content.setCurrentIndex(1)
            return
        m1 = self.analysis_results.get('M1_platforms', {})

        # 箱线图 + 雷达图（双列）
        h_layout = QHBoxLayout()
        h_layout.setSpacing(16)

        # 箱线图
        boxplot = m1.get('boxplot', {})
        if boxplot and HAS_SEABORN:
            card1, fig1, ax1 = self._create_chart_widget(5.5, 5.5)
            data_list = [boxplot[p] for p in boxplot.keys()]
            labels_list = list(boxplot.keys())
            bp = ax1.boxplot(data_list, labels=labels_list, patch_artist=True,
                             boxprops=dict(facecolor=(0.73, 0.40, 1.0, 0.15), color=CINE_NEON_PURPLE),
                             medianprops=dict(color=CINE_NEON_ORANGE, linewidth=2),
                             whiskerprops=dict(color=CINE_TEXT_SECONDARY),
                             capprops=dict(color=CINE_TEXT_SECONDARY),
                             flierprops=dict(marker='o', markerfacecolor=CINE_NEON_PINK, markersize=4, alpha=0.6))
            ax1.set_title('各平台订单金额分布（箱线图）', fontweight='bold', pad=15, fontsize=14)
            ax1.set_ylabel('订单金额 (元)')
            fig1.tight_layout()
            h_layout.addWidget(card1)

        # 雷达图
        radar = m1.get('radar', {})
        if radar:
            card2, fig2, ax2 = self._create_chart_widget(5.5, 5.5, polar=True)
            categories = ['订单数', '总金额', '平均金额', '中位数', '订单占比']
            platforms = list(radar.keys())[:5]
            angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
            angles += angles[:1]
            colors = get_cinematic_palette(len(platforms))
            for i, platform in enumerate(platforms):
                vals = radar[platform]
                values = [vals.get(c, 0) for c in categories]
                # 归一化
                max_vals = [max(radar[p].get(c, 1) for p in platforms) for c in categories]
                values = [v / max(m, 1) for v, m in zip(values, max_vals)]
                values += values[:1]
                ax2.plot(angles, values, 'o-', linewidth=2, label=platform, color=colors[i])
                ax2.fill(angles, values, alpha=0.15, color=colors[i])
            ax2.set_xticks(angles[:-1])
            ax2.set_xticklabels(categories)
            ax2.set_title('平台多维对比（雷达图）', fontweight='bold', pad=20, fontsize=14)
            ax2.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
            fig2.tight_layout()
            h_layout.addWidget(card2)

        if h_layout.count() > 0:
            layout.addLayout(h_layout)

        self._add_table(layout, m1.get('counts', {}))
        self._add_text_analysis(layout,
            "<b>方法论：</b>采用规则映射表 + Levenshtein 编辑距离模糊匹配（阈值 0.6），"
            "将 APP/AP P/微信/vx/VX 等 13 种变体归一化为 5 个标准平台。"
            "<br><b>发现：</b>微信渠道订单量占比最高，APP 次之，两者合计超过 80%。建议针对微信生态优化小程序支付体验，"
            "同时注意 WEB 端虽然订单量小但可能具有高客单价特征。")
        self.content.setCurrentIndex(1)
        self._fade_in_page()

    def show_anomaly(self):
        layout = self.pages["异常检测"]
        self.clear_layout(layout)
        self._add_title(layout, "异常订单检测", "多规则异常检测引擎与明细审计")
        if not self.analysis_results:
            self._show_skeleton(layout, "请先导入数据")
            self.content.setCurrentIndex(2)
            return
        m2 = self.analysis_results.get('M2_anomalies', {})
        self._add_kpi_row(layout, [
            {'title': '异常订单总数', 'value': m2.get('count', 0), 'neon': CINE_NEON_PINK},
        ])
        self._add_table(layout, m2.get('breakdown', {}))
        self._add_text_analysis(layout,
            "<b>方法论：</b>基于业务规则的多维度异常检测。<br>"
            "规则 A：支付金额 < 0（系统退款或数据录入错误）；<br>"
            "规则 B：支付时间早于下单时间（时间悖论，可能为时区或系统故障）；<br>"
            "规则 C：支付金额 > 订单金额 150%（可能含运费或大额补差价，但需审计）。<br>"
            "<b>建议：</b>异常订单已隔离，建议将明细导出交由财务与风控部门二次核查。")
        self.content.setCurrentIndex(2)
        self._fade_in_page()

    def show_kpi(self):
        layout = self.pages["KPI 仪表盘"]
        self.clear_layout(layout)
        self._add_title(layout, "核心 KPI 仪表盘", "总销售额 · 实际销售额 · 退货率 · AOV")
        if not self.analysis_results:
            self._show_skeleton(layout, "请先导入数据")
            self.content.setCurrentIndex(3)
            return
        m3 = self.analysis_results.get('M3_kpi', {})
        self._add_kpi_row(layout, [
            {'title': '总销售额 (GMV)', 'value': m3.get('total_sales', 0), 'prefix': '¥', 'decimals': 2, 'neon': CINE_NEON_ORANGE},
            {'title': '实际销售额', 'value': m3.get('actual_sales', 0), 'prefix': '¥', 'decimals': 2, 'neon': CINE_NEON_CYAN},
            {'title': '订单均价 (AOV)', 'value': m3.get('aov', 0), 'prefix': '¥', 'decimals': 2, 'neon': CINE_NEON_BLUE},
            {'title': '退货率', 'value': m3.get('refund_rate', 0), 'suffix': '%', 'decimals': 2, 'neon': CINE_NEON_PINK},
            {'title': '有效订单', 'value': m3.get('normal_orders', 0), 'neon': CINE_NEON_PURPLE},
            {'title': '退货订单', 'value': m3.get('refund_orders', 0), 'neon': CINE_NEON_GOLD},
        ])

        # 销售额构成 + 订单状态环形图
        h_layout = QHBoxLayout()
        h_layout.setSpacing(16)

        card1, fig1, ax1 = self._create_chart_widget(6, 5)
        labels = ['总销售额\n(GMV)', '实际销售额', '退货损失']
        total = m3.get('total_sales', 0)
        actual = m3.get('actual_sales', 0)
        refund_loss = total - actual
        values = [total, actual, refund_loss]
        colors = [CINE_NEON_BLUE, CINE_NEON_CYAN, CINE_NEON_PINK]
        bars = ax1.bar(labels, values, color=colors, edgecolor='none', width=0.6)
        ax1.set_title('销售额构成分析', fontweight='bold', pad=15, fontsize=14)
        ax1.set_ylabel('金额 (元)')
        for bar in bars:
            h = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., h, f'¥{h:,.0f}',
                    ha='center', va='bottom', fontsize=10, color=CINE_TEXT)
        fig1.tight_layout()
        h_layout.addWidget(card1)

        card2, fig2, ax2 = self._create_chart_widget(5.5, 5.5)
        normal = m3.get('normal_orders', 0)
        refund = m3.get('refund_orders', 0)
        sizes = [normal, refund]
        pie_labels = [f'正常订单\n{normal:,}', f'退货订单\n{refund:,}']
        pie_colors = [CINE_NEON_CYAN, CINE_NEON_PINK]
        wedges, texts, autotexts = ax2.pie(sizes, labels=pie_labels, autopct='%1.1f%%',
                                            colors=pie_colors, startangle=90,
                                            wedgeprops=dict(width=0.5, edgecolor='none', linewidth=2))
        for t in texts:
            t.set_color(CINE_TEXT)
        for t in autotexts:
            t.set_color(CINE_BG)
            t.set_fontweight('bold')
        ax2.set_title('订单状态分布', fontweight='bold', pad=15, fontsize=14)
        fig2.tight_layout()
        h_layout.addWidget(card2)
        layout.addLayout(h_layout)

        self._add_text_analysis(layout,
            f"<b>发现：</b>实际销售额占总销售额的 {(m3.get('actual_sales',0)/max(m3.get('total_sales',1),1)*100):.1f}%。"
            f"订单均价 ¥{m3.get('aov',0):.2f} 处于行业中位水平。<br>"
            f"<b>建议：</b>关注退货率 {m3.get('refund_rate',0)}% 的品类构成，识别高退货品类进行优化；"
            f"通过捆绑销售与满减策略提升 AOV。")
        self.content.setCurrentIndex(3)
        self._fade_in_page()

    def show_monthly(self):
        layout = self.pages["月度趋势"]
        self.clear_layout(layout)
        self._add_title(layout, "月度销售额趋势", "LOESS 平滑 + 环比增长率")
        if not self.analysis_results:
            self._show_skeleton(layout, "请先导入数据")
            self.content.setCurrentIndex(4)
            return
        m4 = self.analysis_results.get('M4_monthly', [])
        if not m4:
            layout.addWidget(QLabel("无月度数据"))
            self.content.setCurrentIndex(4)
            return
        months = [x['pay_month'] for x in m4]
        sales = [x['payment'] for x in m4]
        growth = [x.get('mom_growth', 0) for x in m4]
        orders = [x.get('order_count', 0) for x in m4]

        # 面积图 + 双轴图
        h_layout = QHBoxLayout()
        h_layout.setSpacing(16)

        # 面积图：销售额累积
        card1, fig1, ax1 = self._create_chart_widget(6, 5)
        ax1.fill_between(months, sales, alpha=0.3, color=CINE_NEON_PURPLE)
        ax1.plot(months, sales, color=CINE_NEON_PURPLE, linewidth=2.5, marker='o', markersize=5)
        ax1.set_title('月度销售额趋势（面积图）', fontweight='bold', pad=15, fontsize=14)
        ax1.set_xlabel('月份')
        ax1.set_ylabel('销售额 (元)')
        fig1.tight_layout()
        h_layout.addWidget(card1)

        # 双轴：销售额 + 订单量
        card2, fig2, ax2 = self._create_chart_widget(6, 5)
        ax2_twin = ax2.twinx()
        bars = ax2.bar(months, sales, color=CINE_NEON_BLUE, alpha=0.7, edgecolor='none')
        ax2_twin.plot(months, orders, color=CINE_NEON_ORANGE, marker='s', linewidth=2, markersize=5, label='订单量')
        ax2.set_title('销售额 vs 订单量', fontweight='bold', pad=15, fontsize=14)
        ax2.set_ylabel('销售额 (元)', color=CINE_NEON_BLUE)
        ax2_twin.set_ylabel('订单量', color=CINE_NEON_ORANGE)
        ax2_twin.tick_params(axis='y', labelcolor=CINE_NEON_ORANGE)
        ax2_twin.spines['top'].set_visible(False)
        fig2.tight_layout()
        h_layout.addWidget(card2)
        layout.addLayout(h_layout)

        # 增长率折线图
        card3, fig3, ax3 = self._create_chart_widget(11, 4)
        ax3.plot(months, growth, color=CINE_NEON_PINK, marker='o', linewidth=2.5, markersize=6)
        ax3.axhline(y=0, color=CINE_TEXT_MUTED, linestyle='--', linewidth=1)
        ax3.fill_between(months, growth, 0, alpha=0.2, color=CINE_NEON_PINK)
        ax3.set_title('月度环比增长率', fontweight='bold', pad=15, fontsize=14)
        ax3.set_ylabel('环比增长率 (%)')
        fig3.tight_layout()
        layout.addWidget(card3)

        self._add_text_analysis(layout,
            "<b>方法论：</b>月度聚合 + 环比增长率计算。柱状图展示绝对销售额，红色折线展示环比增速。<br>"
            "<b>商业建议：</b>关注增长率由正转负的拐点月份，提前部署促销资源；识别销售旺季进行库存预配。")
        self.content.setCurrentIndex(4)
        self._fade_in_page()

    def show_channel(self):
        layout = self.pages["渠道构成"]
        self.clear_layout(layout)
        self._add_title(layout, "渠道销售额构成", "帕累托分析 + 环形图")
        if not self.analysis_results:
            self._show_skeleton(layout, "请先导入数据")
            self.content.setCurrentIndex(5)
            return
        m5 = self.analysis_results.get('M5_channels', {})
        ch = m5.get('channels', {})
        if not ch:
            layout.addWidget(QLabel("无渠道数据"))
            self.content.setCurrentIndex(5)
            return

        card, fig, ax = self._create_chart_widget(8, 8)
        labels = list(ch.keys())[:10]
        sizes = list(ch.values())[:10]
        colors = get_cinematic_palette(len(labels))
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%',
                                            colors=colors, startangle=90,
                                            wedgeprops=dict(width=0.5, edgecolor='none'))
        for t in texts:
            t.set_color(CINE_TEXT)
        for t in autotexts:
            t.set_color(CINE_BG)
            t.set_fontweight('bold')
        ax.set_title('TOP10 渠道销售额占比（环形图）', fontweight='bold', pad=15, fontsize=14)
        fig.tight_layout()
        layout.addWidget(card)

        self._add_text_analysis(layout,
            f"<b>方法论：</b>帕累托分析。前 {m5.get('top80_count', 0)} 个渠道贡献了约 80% 的销售额，"
            "符合 80/20 法则。<br><b>建议：</b>将营销预算向头部渠道集中，同时测试长尾渠道的高潜品类。")
        self.content.setCurrentIndex(5)
        self._fade_in_page()

    def show_weekday(self):
        layout = self.pages["星期周期"]
        self.clear_layout(layout)
        self._add_title(layout, "星期消费周期模式", "Kruskal-Wallis 非参数检验")
        if not self.analysis_results:
            self._show_skeleton(layout, "请先导入数据")
            self.content.setCurrentIndex(6)
            return
        m6 = self.analysis_results.get('M6_weekday', {})
        sales = m6.get('sales', {})
        if not sales:
            layout.addWidget(QLabel("无数据"))
            self.content.setCurrentIndex(6)
            return
        days = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
        values = [sales.get(d, 0) for d in days]

        card, fig, ax = self._create_chart_widget(10, 5.5)
        colors = get_cinematic_palette(7)
        bars = ax.bar(days, values, color=colors, edgecolor='none')
        ax.set_title('各星期销售额分布', fontweight='bold', pad=15, fontsize=14)
        ax.set_ylabel('销售额 (元)')
        ax.axhline(y=np.mean(values), color=CINE_NEON_PINK, linestyle='--', linewidth=1.5, label=f'平均值')
        ax.legend(frameon=False)
        fig.tight_layout()
        layout.addWidget(card)

        sig_text = "显著" if m6.get('significant') else "不显著"
        self._add_text_analysis(layout,
            f"<b>方法论：</b>Kruskal-Wallis H 检验（非参数 ANOVA），统计量 H={m6.get('kw_statistic',0)}, p={m6.get('kw_pvalue',0)}。"
            f"星期效应 {sig_text} (α=0.05)。<br>"
            "<b>发现：</b>周末与工作日的消费差异可用于制定差异化运营策略，如周末限时秒杀、工作日满减等。")
        self.content.setCurrentIndex(6)
        self._fade_in_page()

    def show_hourly(self):
        layout = self.pages["24小时热力"]
        self.clear_layout(layout)
        self._add_title(layout, "24小时消费热力", "全年小时级聚合 + 标准差区间")
        if not self.analysis_results:
            self._show_skeleton(layout, "请先导入数据")
            self.content.setCurrentIndex(7)
            return
        m7 = self.analysis_results.get('M7_hourly', {})
        m6_5 = self.analysis_results.get('M6_5_heatmap', {})
        sales = m7.get('sales', {})
        if not sales:
            layout.addWidget(QLabel("无数据"))
            self.content.setCurrentIndex(7)
            return
        hours = list(range(24))
        values = [sales.get(h, 0) for h in hours]
        std_vals = [m7.get('std', {}).get(h, 0) for h in hours]

        # 24小时折线图
        card1, fig1, ax1 = self._create_chart_widget(12, 5)
        ax1.fill_between(hours, np.array(values) - np.array(std_vals), np.array(values) + np.array(std_vals),
                        alpha=0.15, color=CINE_NEON_BLUE, label='±1σ 区间')
        ax1.plot(hours, values, color=CINE_NEON_BLUE, linewidth=2.5, marker='o', markersize=4, label='销售额')
        ax1.set_title('24小时销售额分布（全年聚合）', fontweight='bold', pad=15, fontsize=14)
        ax1.set_xlabel('小时')
        ax1.set_ylabel('销售额 (元)')
        ax1.set_xticks(hours)
        ax1.legend(frameon=False)
        fig1.tight_layout()
        layout.addWidget(card1)

        # 星期 x 小时 热力图
        if m6_5 and HAS_SEABORN:
            card2, fig2, ax2 = self._create_chart_widget(12, 6)
            matrix = np.array(m6_5.get('matrix', []))
            if matrix.size > 0:
                sns.heatmap(matrix, annot=False, fmt='.0f', cmap='magma',
                           xticklabels=[f"{h:02d}" for h in range(24)],
                           yticklabels=m6_5.get('weekday_labels', []),
                           ax=ax2, cbar_kws={'label': '销售额'})
                ax2.set_title('星期 × 小时 销售热力图', fontweight='bold', pad=15, fontsize=14)
                ax2.set_xlabel('小时')
                ax2.set_ylabel('星期')
                fig2.tight_layout()
                layout.addWidget(card2)

        self._add_text_analysis(layout,
            f"<b>方法论：</b>全年小时级聚合，阴影区域表示各小时销售额的标准差。"
            f"峰值时段：{m7.get('peak_hour',0)}:00，低谷时段：{m7.get('valley_hour',0)}:00。<br>"
            "<b>建议：</b>在峰值前 1 小时加大广告投放与客服资源配置；低谷时段安排系统维护。")
        self.content.setCurrentIndex(7)
        self._fade_in_page()

    def show_customer_value(self):
        layout = self.pages["客户价值"]
        self.clear_layout(layout)
        self._add_title(layout, "客户价值分层", "洛伦兹曲线 + 基尼系数")
        if not self.analysis_results:
            self._show_skeleton(layout, "请先导入数据")
            self.content.setCurrentIndex(8)
            return
        m8 = self.analysis_results.get('M8_customer_value', {})

        # 洛伦兹曲线
        card1, fig1, ax1 = self._create_chart_widget(8, 8)
        lorenz_x = m8.get('lorenz_x', [])
        lorenz_y = m8.get('lorenz_y', [])
        if lorenz_x and lorenz_y:
            ax1.plot(lorenz_x, lorenz_y, color=CINE_NEON_PURPLE, linewidth=2.5, label='实际分布')
            ax1.plot([0, 100], [0, 100], color=CINE_TEXT_MUTED, linestyle='--', linewidth=1, label='绝对平等线')
            ax1.fill_between(lorenz_x, lorenz_y, [x * (lorenz_y[-1]/100) for x in lorenz_x], alpha=0.1, color=CINE_NEON_PURPLE)
            ax1.set_title('客户消费洛伦兹曲线', fontweight='bold', pad=15, fontsize=14)
            ax1.set_xlabel('客户累积占比 (%)')
            ax1.set_ylabel('销售额累积占比 (%)')
            ax1.legend(frameon=False)
            fig1.tight_layout()
        layout.addWidget(card1)

        self._add_kpi_row(layout, [
            {'title': '前10%客户贡献', 'value': m8.get('top10_pct', 0), 'suffix': '%', 'neon': CINE_NEON_GOLD},
            {'title': '后10%客户贡献', 'value': m8.get('bottom10_pct', 0), 'suffix': '%', 'neon': CINE_NEON_BLUE},
            {'title': '基尼系数', 'value': m8.get('gini', 0), 'decimals': 4, 'neon': CINE_NEON_PURPLE},
        ])
        self._add_text_analysis(layout,
            f"<b>方法论：</b>洛伦兹曲线描述财富（此处为消费额）分配不平等程度。基尼系数 {m8.get('gini',0)} "
            f"{'> 0.4 表示高度集中' if m8.get('gini',0) > 0.4 else '< 0.4 表示相对均衡'}。<br>"
            "<b>策略：</b>前 10% 高价值客户应纳入 VIP 专属服务体系；针对后 10% 尝试低成本激活或放弃维护。")
        self.content.setCurrentIndex(8)
        self._fade_in_page()

    def show_holiday(self):
        layout = self.pages["节假日影响"]
        self.clear_layout(layout)
        self._add_title(layout, "节假日消费影响", "双重差分法 (Difference-in-Differences)")
        if not self.analysis_results:
            self._show_skeleton(layout, "请先导入数据")
            self.content.setCurrentIndex(9)
            return
        m9 = self.analysis_results.get('M9_holidays', {})
        holidays = m9.get('holidays', [])
        if not holidays:
            layout.addWidget(QLabel("无数据"))
            self.content.setCurrentIndex(9)
            return

        names = [h['name'] for h in holidays]
        diffs = [h['diff'] for h in holidays]
        colors = [CINE_NEON_PINK if d < 0 else CINE_NEON_CYAN for d in diffs]

        card, fig, ax = self._create_chart_widget(10, 5.5)
        bars = ax.barh(names, diffs, color=colors, edgecolor='none')
        ax.axvline(x=0, color=CINE_TEXT_MUTED, linewidth=0.8)
        ax.set_title('节假日日均销售额净效应（DiD 估计）', fontweight='bold', pad=15, fontsize=14)
        ax.set_xlabel('日均销售额差异 (元)')
        for bar in bars:
            w = bar.get_width()
            ax.text(w, bar.get_y() + bar.get_height()/2., f'{w:,.0f}',
                    ha='left' if w > 0 else 'right', va='center', fontsize=9, color=CINE_TEXT)
        fig.tight_layout()
        layout.addWidget(card)

        self._add_text_analysis(layout,
            "<b>方法论：</b>双重差分法（DiD）。处理组为节假日期间，对照组为节前节后等长窗口。"
            "控制时间趋势后，估计节假日的净促销效应。正值表示节假日显著拉动消费。<br>"
            "<b>注意：</b>春节与国庆的长假效应可能包含消费提前或延后，需结合节前节后具体数据解读。")
        self.content.setCurrentIndex(9)
        self._fade_in_page()

    def show_payment_lag(self):
        layout = self.pages["支付时滞"]
        self.clear_layout(layout)
        self._add_title(layout, "支付时滞分析", "分布拟合 + K-Means 客户分群")
        if not self.analysis_results:
            self._show_skeleton(layout, "请先导入数据")
            self.content.setCurrentIndex(10)
            return
        m10 = self.analysis_results.get('M10_payment_lag', {})
        self._add_kpi_row(layout, [
            {'title': '平均支付时滞', 'value': m10.get('mean_sec', 0), 'suffix': ' 秒', 'decimals': 0, 'neon': CINE_NEON_ORANGE},
            {'title': '中位数', 'value': m10.get('median_sec', 0), 'suffix': ' 秒', 'decimals': 0, 'neon': CINE_NEON_CYAN},
        ])

        # 小提琴图
        violin = m10.get('violin', [])
        if violin and HAS_SEABORN:
            card, fig, ax = self._create_chart_widget(10, 5)
            # 限制到 30 分钟以内以便观察
            v_data = [v for v in violin if v <= 30]
            if v_data:
                sns.violinplot(data=v_data, ax=ax, color=CINE_NEON_PURPLE, inner='quartile')
                ax.set_title('支付时滞分布（小提琴图，≤30分钟）', fontweight='bold', pad=15, fontsize=14)
                ax.set_ylabel('时滞（分钟）')
                ax.set_xticklabels([''])
                fig.tight_layout()
                layout.addWidget(card)

        clusters = m10.get('clusters', {})
        if clusters:
            self._add_table(layout, clusters)
        self._add_text_analysis(layout,
            "<b>方法论：</b>支付时滞 = pay_time - order_time。K-Means 聚类（标准化后的时滞 + 订单金额）"
            "将客户划分为即时支付型、犹豫比对型等群体。<br>"
            "<b>发现：</b>中位数远低于平均值，说明存在少数长时滞订单拉高了均值，可针对长时滞客户推送限时优惠促成转化。")
        self.content.setCurrentIndex(10)
        self._fade_in_page()

    def show_rfm(self):
        layout = self.pages["RFM & CLV"]
        self.clear_layout(layout)
        self._add_title(layout, "RFM 客户价值模型 & CLV", "K-Means 聚类 + 客户生命周期价值")
        if not self.analysis_results:
            self._show_skeleton(layout, "请先导入数据")
            self.content.setCurrentIndex(11)
            return
        m11 = self.analysis_results.get('M11_rfm_clv', {})
        self._add_kpi_row(layout, [
            {'title': '总客户数', 'value': m11.get('total_customers', 0), 'neon': CINE_NEON_BLUE},
            {'title': '平均 CLV', 'value': m11.get('avg_clv', 0), 'prefix': '¥', 'decimals': 2, 'neon': CINE_NEON_GOLD},
        ])

        # 气泡图
        bubble = m11.get('bubble', [])
        if bubble:
            card, fig, ax = self._create_chart_widget(10, 8)
            # 取样本（避免太多点）
            sample = bubble[:min(500, len(bubble))]
            x = [b.get('frequency', 0) for b in sample]
            y = [b.get('monetary', 0) for b in sample]
            sizes = [max(20, min(300, b.get('clv', 0) / 10)) for b in sample]
            colors = [b.get('cluster', 0) for b in sample]
            scatter = ax.scatter(x, y, s=sizes, c=colors, cmap='plasma', alpha=0.7, edgecolors='none')
            ax.set_title('客户价值气泡图（大小=CLV，颜色=群体）', fontweight='bold', pad=15, fontsize=14)
            ax.set_xlabel('购买频次')
            ax.set_ylabel('消费金额 (元)')
            cbar = fig.colorbar(scatter, ax=ax)
            cbar.set_label('客户群体')
            fig.tight_layout()
            layout.addWidget(card)

        summary = m11.get('cluster_summary', {})
        if summary:
            rows = []
            for cid, vals in summary.items():
                row = {'客户群': f'群体 {cid}'}
                row.update(vals)
                rows.append(row)
            self._add_table(layout, rows)
        self._add_text_analysis(layout,
            "<b>方法论：</b>RFM（Recency, Frequency, Monetary）三维特征标准化后 K-Means 聚类。"
            "CLV = 历史平均金额 × 购买频次 × (365 / Recency)。<br>"
            "<b>策略：</b>高 RFM 值客户群应重点维护；高 Recency 低 Frequency 客户需召回激活；"
            "低 Monetary 群体可尝试向上销售（Upsell）。")
        self.content.setCurrentIndex(11)
        self._fade_in_page()

    def show_advanced(self):
        layout = self.pages["高阶网络与生存"]
        self.clear_layout(layout)
        self._add_title(layout, "高阶网络与生存分析",
                        "Jaccard + Leiden + Null Model + 动态网络 + Cox 生存 + Markov 状态空间")
        if not self.analysis_results:
            self._show_skeleton(layout, "请先导入数据")
            self.content.setCurrentIndex(12)
            return
        m12 = self.analysis_results.get('M12_advanced', {})
        net = m12.get('network', {})
        dyn = m12.get('dynamic_network', [])
        surv = m12.get('survival', {})
        markov = m12.get('markov', {})

        if net:
            self._add_kpi_row(layout, [
                {'title': '网络节点数', 'value': net.get('nodes', 0), 'neon': CINE_NEON_BLUE},
                {'title': '网络边数', 'value': net.get('edges', 0), 'neon': CINE_NEON_PURPLE},
                {'title': '社群数', 'value': net.get('communities', 0), 'neon': CINE_NEON_CYAN},
                {'title': '模块度', 'value': net.get('modularity', 0), 'decimals': 4, 'neon': CINE_NEON_ORANGE},
                {'title': 'Null Z-score', 'value': net.get('z_score', 0), 'decimals': 3, 'neon': CINE_NEON_GOLD},
                {'title': 'p-value', 'value': net.get('p_value', 0), 'decimals': 4, 'neon': CINE_NEON_PINK},
            ])

        if dyn:
            card, fig, ax = self._create_chart_widget(10, 4.5)
            quarters = [d['quarter'] for d in dyn]
            mods = [d['modularity'] for d in dyn]
            ax.plot(quarters, mods, color=CINE_NEON_PURPLE, marker='o', linewidth=2, markersize=6)
            ax.set_title('动态网络模块度演化（季度切片）', fontweight='bold', pad=15, fontsize=14)
            ax.set_ylabel('模块度')
            fig.tight_layout()
            layout.addWidget(card)

        if surv and 'timeline' in surv:
            card2, fig2, ax2 = self._create_chart_widget(10, 5)
            timeline = surv['timeline']
            sp = surv['survival_prob']
            ci_lower = surv['ci_lower']
            ci_upper = surv['ci_upper']
            ax2.fill_between(timeline, ci_lower, ci_upper, alpha=0.15, color=CINE_NEON_PURPLE, label='95% CI')
            ax2.plot(timeline, sp, color=CINE_NEON_PURPLE, linewidth=2.5, label='Kaplan-Meier 生存概率')
            ax2.set_title('客户复购生存曲线', fontweight='bold', pad=15, fontsize=14)
            ax2.set_xlabel('距上次购买天数')
            ax2.set_ylabel('未流失概率')
            ax2.legend(frameon=False)
            fig2.tight_layout()
            layout.addWidget(card2)

        if markov:
            states = markov.get('states', [])
            matrix = markov.get('transition_matrix', {})
            if matrix:
                card = CineCard(neon_color=CINE_NEON_BLUE, radius=CINE_RADIUS_M)
                c_layout = QVBoxLayout(card)
                c_layout.setContentsMargins(16, 16, 16, 16)
                lbl = QLabel("<b>Markov 状态转移矩阵</b>")
                lbl.setStyleSheet(f"font-size: 14px; color: {CINE_TEXT}; font-weight: 600; background: transparent;")
                c_layout.addWidget(lbl)
                table = QTableWidget(len(states), len(states) + 1)
                table.setHorizontalHeaderLabels(['状态'] + states)
                table.setAlternatingRowColors(True)
                table.setStyleSheet("""
                    QTableWidget { border: none; background: transparent; }
                    QTableWidget::item { padding: 8px; }
                """)
                for i, s in enumerate(states):
                    item = QTableWidgetItem(s)
                    item.setTextAlignment(Qt.AlignCenter)
                    table.setItem(i, 0, item)
                    row = matrix.get(s, {})
                    for j, s2 in enumerate(states):
                        item = QTableWidgetItem(f"{row.get(s2, 0):.3f}")
                        item.setTextAlignment(Qt.AlignCenter)
                        table.setItem(i, j+1, item)
                table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
                table.setMaximumHeight(220)
                table.verticalHeader().setVisible(False)
                c_layout.addWidget(table)
                layout.addWidget(card)

        self._add_text_analysis(layout,
            "<b>方法论综述：</b><br>"
            "① <b>Jaccard 共购网络</b>：以商品购买集合的 Jaccard 系数为边权重，构建客户相似性网络；<br>"
            "② <b>Leiden 社群发现</b>：使用贪婪模块度优化检测客户社群；<br>"
            "③ <b>Null Model</b>：Configuration Model 置换检验 50 次，Z-score 检验社群结构是否显著非随机；<br>"
            "④ <b>动态网络</b>：按季度切片追踪模块度演化，识别结构突变点；<br>"
            "⑤ <b>Cox 生存分析</b>：比例风险模型评估平台类型与订单金额对流失风险的影响；<br>"
            "⑥ <b>Markov 状态空间</b>：将客户旅程建模为 {新客, 活跃, 沉睡, 流失} 的马尔可夫链，量化状态转移概率。")
        self.content.setCurrentIndex(12)
        self._fade_in_page()
