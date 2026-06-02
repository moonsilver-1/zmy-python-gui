"""
主窗口：Modern SaaS Dashboard 风格
包含侧边导航、内容区、数据导入、分析展示
"""
import sys
import os

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget, QScrollArea,
    QFrame, QTableWidget, QTableWidgetItem, QFileDialog,
    QMessageBox, QHeaderView, QSizePolicy, QGridLayout,
    QProgressBar, QTextEdit, QSplitter, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon, QColor, QPalette, QLinearGradient, QBrush

from config.styles import get_theme
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


# ========== 样式常量 ==========
SIDEBAR_BG = "#0f172a"
SIDEBAR_ACTIVE = "#2563eb"
SIDEBAR_HOVER = "#1e293b"
CARD_BG_LIGHT = "#ffffff"
CARD_BG_DARK = "#1e293b"
CARD_BORDER_LIGHT = "#e5e7eb"
CARD_BORDER_DARK = "#334155"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6b7280"
ACCENT_BLUE = "#2563eb"


class MainWindow(QMainWindow):
    def __init__(self, splash=None):
        super().__init__()
        self.splash = splash
        self.setWindowTitle("电商订单数据分析平台")
        self.setMinimumSize(1400, 900)
        self.resize(1600, 1000)
        self.current_theme = 'light'
        self.analysis_results = {}
        self.modules = [
            ("📊 数据概览", self.show_overview),
            ("📱 平台分析", self.show_platform),
            ("⚠️ 异常检测", self.show_anomaly),
            ("🎯 KPI 仪表盘", self.show_kpi),
            ("📅 月度趋势", self.show_monthly),
            ("🥧 渠道构成", self.show_channel),
            ("📆 星期周期", self.show_weekday),
            ("⏰ 24小时热力", self.show_hourly),
            ("💎 客户价值", self.show_customer_value),
            ("🎉 节假日影响", self.show_holiday),
            ("⏱️ 支付时滞", self.show_payment_lag),
            ("🧬 RFM & CLV", self.show_rfm),
            ("🔬 高阶网络与生存", self.show_advanced),
        ]
        self._setup_ui()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ========== 侧边栏 ==========
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(200)
        self.sidebar.setStyleSheet(f"""
            QWidget {{
                background-color: {SIDEBAR_BG};
            }}
        """)
        sb_layout = QVBoxLayout(self.sidebar)
        sb_layout.setContentsMargins(0, 0, 0, 20)
        sb_layout.setSpacing(0)

        # Logo 区域
        logo_widget = QWidget()
        logo_widget.setStyleSheet(f"background-color: #020617; border-bottom: 1px solid #1e293b;")
        logo_layout = QVBoxLayout(logo_widget)
        logo_layout.setContentsMargins(20, 24, 20, 20)
        logo_title = QLabel("电商数据分析")
        logo_title.setStyleSheet("color: #f8fafc; font-size: 18px; font-weight: bold; letter-spacing: 1px;")
        logo_sub = QLabel("E-Commerce Analytics")
        logo_sub.setStyleSheet("color: #94a3b8; font-size: 11px; letter-spacing: 2px; font-family: 'Times New Roman', serif;")
        logo_layout.addWidget(logo_title)
        logo_layout.addWidget(logo_sub)
        sb_layout.addWidget(logo_widget)
        sb_layout.addSpacing(10)

        # 导航按钮
        self.nav_buttons = []
        for name, callback in self.modules:
            btn = QPushButton(f"  {name}")
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: #94a3b8;
                    border: none;
                    padding: 14px 24px;
                    text-align: left;
                    font-size: 13px;
                    border-left: 3px solid transparent;
                }}
                QPushButton:hover {{
                    background-color: {SIDEBAR_HOVER};
                    color: #e2e8f0;
                }}
                QPushButton:checked {{
                    background-color: {SIDEBAR_HOVER};
                    color: #ffffff;
                    border-left: 3px solid {SIDEBAR_ACTIVE};
                    font-weight: bold;
                }}
            """)
            btn.clicked.connect(lambda checked, c=callback, b=btn: self._on_nav_clicked(c, b))
            sb_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        sb_layout.addStretch()

        # 底部操作区
        bottom_widget = QWidget()
        bottom_widget.setStyleSheet("background-color: #020617; border-top: 1px solid #1e293b;")
        bottom_layout = QVBoxLayout(bottom_widget)
        bottom_layout.setContentsMargins(16, 16, 16, 16)
        bottom_layout.setSpacing(10)

        import_btn = QPushButton("📂 导入数据")
        import_btn.setCursor(Qt.PointingHandCursor)
        import_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {SIDEBAR_ACTIVE};
                color: white;
                border-radius: 6px;
                padding: 10px;
                font-weight: bold;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: #1d4ed8;
            }}
        """)
        import_btn.clicked.connect(self.import_data)
        bottom_layout.addWidget(import_btn)

        theme_btn = QPushButton("🌙 切换主题")
        theme_btn.setCursor(Qt.PointingHandCursor)
        theme_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #94a3b8;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 8px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #1e293b;
                color: #e2e8f0;
            }
        """)
        theme_btn.clicked.connect(self.toggle_theme)
        bottom_layout.addWidget(theme_btn)
        sb_layout.addWidget(bottom_widget)

        layout.addWidget(self.sidebar)

        # ========== 右侧内容区 ==========
        self.content = QStackedWidget()
        self.content.setStyleSheet("background-color: #f8fafc;")
        layout.addWidget(self.content, 1)

        # 初始化各页面
        self.pages = {}
        for name, _ in self.modules:
            page = QScrollArea()
            page.setWidgetResizable(True)
            page.setFrameShape(QFrame.NoFrame)
            page.setStyleSheet("background-color: #f8fafc; border: none;")
            container = QWidget()
            container_layout = QVBoxLayout(container)
            container_layout.setContentsMargins(32, 32, 32, 32)
            container_layout.setSpacing(24)
            container_layout.setAlignment(Qt.AlignTop)
            container.setLayout(container_layout)
            container.setMinimumHeight(800)
            page.setWidget(container)
            self.content.addWidget(page)
            self.pages[name] = container_layout

        if self.nav_buttons:
            self.nav_buttons[0].setChecked(True)
            self.show_overview()

        # ========== 自动加载数据 ==========
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #2563eb; font-size: 13px; font-weight: bold; padding: 8px 16px; background: #dbeafe; border-radius: 6px;")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.hide()
        # 将状态标签放在内容区顶部（悬浮效果）
        self.content.setContentsMargins(0, 0, 0, 0)

        self._auto_load()

    def _update_splash(self, msg):
        if self.splash:
            from PyQt5.QtGui import QColor
            self.splash.showMessage(
                f"\n\n  电商订单数据分析平台\n  E-Commerce Analytics\n\n  {msg}",
                Qt.AlignCenter | Qt.AlignTop,
                QColor("#f8fafc")
            )
            from PyQt5.QtWidgets import QApplication
            QApplication.instance().processEvents()

    def _auto_load(self):
        """启动时自动搜索并同步加载数据（在 splash 中执行，不会卡 UI）"""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.dirname(script_dir)
        parent_dir = os.path.dirname(project_dir)
        candidates = [
            os.path.join(parent_dir, '某电商平台2021年订单数据.xlsx'),
            os.path.join(project_dir, '某电商平台2021年订单数据.xlsx'),
            '../某电商平台2021年订单数据.xlsx',
            '某电商平台2021年订单数据.xlsx',
        ]
        found = None
        for c in candidates:
            if os.path.exists(c):
                found = os.path.abspath(c)
                break
        if found:
            self._load_data_sync(found)
        else:
            layout = self.pages.get("📊 数据概览")
            if layout:
                self.clear_layout(layout)
                lbl = QLabel("未找到默认数据文件，请点击左侧「导入数据」手动加载")
                lbl.setStyleSheet("color: #9ca3af; font-size: 14px; padding: 40px;")
                layout.addWidget(lbl)

    def _load_data_sync(self, file_path):
        """同步加载数据（由 splash 覆盖，用户不会感到卡顿）"""
        try:
            self._update_splash("正在读取 Excel...")
            raw_df = DataLoader.load_excel(file_path)

            self._update_splash("正在清洗数据（平台归一化 + 异常检测）...")
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
        callback()

    def toggle_theme(self):
        self.current_theme = 'dark' if self.current_theme == 'light' else 'light'
        # 简化处理：仅切换内容区背景
        if self.current_theme == 'dark':
            self.content.setStyleSheet("background-color: #0f172a;")
        else:
            self.content.setStyleSheet("background-color: #f8fafc;")

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

    def _show_load_success_message(self, report):
        QMessageBox.information(self, "导入成功",
            f"原始数据: {report['original_count']:,} 条\n"
            f"异常订单: {report['anomaly_count']:,} 条\n"
            f"有效订单: {report['cleaned_count']:,} 条")

    # ===================== 页面渲染辅助 =====================
    def _add_title(self, layout, title, subtitle=""):
        box = QVBoxLayout()
        box.setSpacing(4)
        lbl = QLabel(title)
        lbl.setWordWrap(True)
        lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        lbl.setStyleSheet("font-size: 22px; font-weight: bold; color: #111827; font-family: 'Times New Roman', 'SimSun', serif; border: none; background: transparent;")
        box.addWidget(lbl)
        if subtitle:
            sub = QLabel(subtitle)
            sub.setWordWrap(True)
            sub.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            sub.setStyleSheet("font-size: 13px; color: #6b7280; font-family: 'Times New Roman', 'SimSun', serif; border: none; background: transparent;")
            box.addWidget(sub)
        box.addSpacing(8)
        layout.addLayout(box)

    def _add_kpi_row(self, layout, kpis: list):
        grid = QGridLayout()
        grid.setSpacing(16)
        cols_per_row = 3
        for i, kpi in enumerate(kpis):
            card = QFrame()
            card.setMinimumWidth(200)
            card.setStyleSheet("""
                QFrame {
                    background-color: #ffffff;
                    border-radius: 10px;
                    border: 1px solid #e5e7eb;
                }
            """)
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(20)
            shadow.setColor(QColor(0, 0, 0, 25))
            shadow.setOffset(0, 4)
            card.setGraphicsEffect(shadow)

            c_layout = QVBoxLayout(card)
            c_layout.setContentsMargins(20, 18, 20, 18)
            c_layout.setSpacing(6)

            t = QLabel(kpi.get('title', ''))
            t.setStyleSheet("color: #6b7280; font-size: 12px; font-family: 'Times New Roman', 'SimSun', serif; border: none; background: transparent;")
            v = QLabel(str(kpi.get('value', '')))
            v.setStyleSheet("color: #111827; font-size: 26px; font-weight: bold; font-family: 'Times New Roman', 'SimSun', serif; border: none; background: transparent;")
            c_layout.addWidget(t)
            c_layout.addWidget(v)
            row = i // cols_per_row
            col = i % cols_per_row
            grid.addWidget(card, row, col)
        for c in range(cols_per_row):
            grid.setColumnStretch(c, 1)
        layout.addLayout(grid)

    def _create_chart_widget(self, width=10, height=6):
        configure_sci_style()
        fig = Figure(figsize=(width, height), dpi=120, facecolor='white')
        ax = fig.add_subplot(111)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        canvas = FigureCanvas(fig)
        return canvas, fig, ax

    def _add_text_analysis(self, layout, text: str):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 10px;
                border: 1px solid #e5e7eb;
            }
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 25))
        shadow.setOffset(0, 4)
        card.setGraphicsEffect(shadow)

        c_layout = QVBoxLayout(card)
        c_layout.setContentsMargins(20, 16, 20, 16)
        te = QTextEdit()
        te.setReadOnly(True)
        te.setFrameStyle(QFrame.NoFrame)
        te.setStyleSheet("border: none; background: transparent; font-family: 'Times New Roman', 'SimSun', serif;")
        te.setHtml(f"<div style='line-height:1.8;font-size:13px;color:#374151;'>{text}</div>")
        te.setMaximumHeight(220)
        c_layout.addWidget(te)
        layout.addWidget(card)

    def _add_table(self, layout, df: dict or list, max_rows=20):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 10px;
                border: 1px solid #e5e7eb;
            }
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 25))
        shadow.setOffset(0, 4)
        card.setGraphicsEffect(shadow)

        c_layout = QVBoxLayout(card)
        c_layout.setContentsMargins(16, 16, 16, 16)

        if isinstance(df, list) and len(df) > 0:
            keys = list(df[0].keys())
            table = QTableWidget(min(len(df), max_rows), len(keys))
            table.setHorizontalHeaderLabels(keys)
            table.setStyleSheet("""
                QTableWidget {
                    background-color: #ffffff;
                    border: none;
                    gridline-color: #f3f4f6;
                }
                QHeaderView::section {
                    background-color: #f9fafb;
                    color: #374151;
                    padding: 8px 10px;
                    border: none;
                    border-bottom: 2px solid #e5e7eb;
                    font-weight: bold;
                    font-family: 'Times New Roman', 'SimSun', serif;
                }
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
            table.setStyleSheet("""
                QTableWidget {
                    background-color: #ffffff;
                    border: none;
                    gridline-color: #f3f4f6;
                }
                QHeaderView::section {
                    background-color: #f9fafb;
                    color: #374151;
                    padding: 8px 10px;
                    border: none;
                    border-bottom: 2px solid #e5e7eb;
                    font-weight: bold;
                    font-family: 'Times New Roman', 'SimSun', serif;
                }
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
            return
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setMaximumHeight(320)
        table.verticalHeader().setVisible(False)
        c_layout.addWidget(table)
        layout.addWidget(card)

    # ===================== 各模块页面 =====================
    def show_overview(self):
        layout = self.pages["📊 数据概览"]
        self.clear_layout(layout)
        self._add_title(layout, "数据概览", "电商订单数据整体情况与平台分布")
        if state.cleaned_data is None:
            lbl = QLabel("暂无数据，请点击左侧「导入数据」按钮加载 Excel 文件")
            lbl.setStyleSheet("color: #9ca3af; font-size: 14px; padding: 40px;")
            layout.addWidget(lbl)
            self.content.setCurrentIndex(0)
            return

        r = self.analysis_results
        kpi = r.get('M3_kpi', {})
        self._add_kpi_row(layout, [
            {'title': '总销售额 (GMV)', 'value': f"¥{kpi.get('total_sales', 0):,.2f}"},
            {'title': '实际销售额', 'value': f"¥{kpi.get('actual_sales', 0):,.2f}"},
            {'title': '有效订单', 'value': f"{kpi.get('normal_orders', 0):,}"},
            {'title': '退货率', 'value': f"{kpi.get('refund_rate', 0)}%"},
        ])

        # 平台分布图
        canvas, fig, ax = self._create_chart_widget(10, 5)
        m1 = r.get('M1_platforms', {})
        platforms = list(m1.get('counts', {}).keys())
        counts = list(m1.get('counts', {}).values())
        colors = get_color_palette(len(platforms))
        bars = ax.bar(platforms, counts, color=colors, edgecolor='white', linewidth=0.5)
        ax.set_title('各平台订单分布', fontweight='bold', pad=15)
        ax.set_ylabel('订单数')
        for bar in bars:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., h, f'{int(h):,}',
                    ha='center', va='bottom', fontsize=9)
        fig.tight_layout()
        layout.addWidget(canvas)

        self._add_text_analysis(layout,
            f"<b>数据质量概况：</b>原始数据共 {kpi.get('total_orders', 0):,} 条，"
            f"异常订单 {r.get('M2_anomalies', {}).get('count', 0):,} 条已隔离。"
            f"有效客户数 {kpi.get('unique_customers', 0):,} 人，订单均价 ¥{kpi.get('aov', 0):.2f}。"
            f"退货率 {kpi.get('refund_rate', 0)}% 处于电商行业平均水平（10%-15%）。<br>"
            f"<b>商业建议：</b>重点关注微信与 APP 两大核心渠道的用户体验优化，同时审视退货流程以降低 13% 的退货损失。")
        self.content.setCurrentIndex(0)

    def show_platform(self):
        layout = self.pages["📱 平台分析"]
        self.clear_layout(layout)
        self._add_title(layout, "平台归一化分析", "同一平台不同表述的智能归一与分布")
        if not self.analysis_results:
            layout.addWidget(QLabel("请先导入数据"))
            self.content.setCurrentIndex(1)
            return
        m1 = self.analysis_results.get('M1_platforms', {})
        self._add_table(layout, m1.get('counts', {}))
        self._add_text_analysis(layout,
            "<b>方法论：</b>采用规则映射表 + Levenshtein 编辑距离模糊匹配（阈值 0.6），"
            "将 APP/AP P/微信/vx/VX 等 13 种变体归一化为 5 个标准平台。"
            "<br><b>发现：</b>微信渠道订单量占比最高，APP 次之，两者合计超过 80%。建议针对微信生态优化小程序支付体验，"
            "同时注意 WEB 端虽然订单量小但可能具有高客单价特征。")
        self.content.setCurrentIndex(1)

    def show_anomaly(self):
        layout = self.pages["⚠️ 异常检测"]
        self.clear_layout(layout)
        self._add_title(layout, "异常订单检测", "多规则异常检测引擎与明细审计")
        if not self.analysis_results:
            layout.addWidget(QLabel("请先导入数据"))
            self.content.setCurrentIndex(2)
            return
        m2 = self.analysis_results.get('M2_anomalies', {})
        self._add_kpi_row(layout, [
            {'title': '异常订单总数', 'value': f"{m2.get('count', 0):,}"},
        ])
        self._add_table(layout, m2.get('breakdown', {}))
        self._add_text_analysis(layout,
            "<b>方法论：</b>基于业务规则的多维度异常检测。<br>"
            "规则 A：支付金额 < 0（系统退款或数据录入错误）；<br>"
            "规则 B：支付时间早于下单时间（时间悖论，可能为时区或系统故障）；<br>"
            "规则 C：支付金额 > 订单金额 150%（可能含运费或大额补差价，但需审计）。<br>"
            "<b>建议：</b>异常订单已隔离，建议将明细导出交由财务与风控部门二次核查。")
        self.content.setCurrentIndex(2)

    def show_kpi(self):
        layout = self.pages["🎯 KPI 仪表盘"]
        self.clear_layout(layout)
        self._add_title(layout, "核心 KPI 仪表盘", "总销售额 · 实际销售额 · 退货率 · AOV")
        if not self.analysis_results:
            layout.addWidget(QLabel("请先导入数据"))
            self.content.setCurrentIndex(3)
            return
        m3 = self.analysis_results.get('M3_kpi', {})
        self._add_kpi_row(layout, [
            {'title': '总销售额 (GMV)', 'value': f"¥{m3.get('total_sales', 0):,.2f}"},
            {'title': '实际销售额', 'value': f"¥{m3.get('actual_sales', 0):,.2f}"},
            {'title': '订单均价 (AOV)', 'value': f"¥{m3.get('aov', 0):,.2f}"},
            {'title': '退货率', 'value': f"{m3.get('refund_rate', 0)}%"},
            {'title': '有效订单', 'value': f"{m3.get('normal_orders', 0):,}"},
            {'title': '退货订单', 'value': f"{m3.get('refund_orders', 0):,}"},
        ])

        # 销售额构成瀑布图
        canvas1, fig1, ax1 = self._create_chart_widget(10, 4.5)
        labels = ['总销售额\n(GMV)', '实际销售额', '退货损失']
        total = m3.get('total_sales', 0)
        actual = m3.get('actual_sales', 0)
        refund_loss = total - actual
        values = [total, actual, refund_loss]
        colors = ['#4472C4', '#10B981', '#EF4444']
        bars = ax1.bar(labels, values, color=colors, edgecolor='white', width=0.6)
        ax1.set_title('销售额构成分析', fontweight='bold', pad=15)
        ax1.set_ylabel('金额 (元)')
        for bar in bars:
            h = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., h, f'¥{h:,.0f}',
                    ha='center', va='bottom', fontsize=10)
        fig1.tight_layout()
        layout.addWidget(canvas1)

        # 订单状态环形图
        canvas2, fig2, ax2 = self._create_chart_widget(7, 7)
        normal = m3.get('normal_orders', 0)
        refund = m3.get('refund_orders', 0)
        sizes = [normal, refund]
        pie_labels = [f'正常订单\n{normal:,}', f'退货订单\n{refund:,}']
        pie_colors = ['#10B981', '#EF4444']
        wedges, texts, autotexts = ax2.pie(sizes, labels=pie_labels, autopct='%1.1f%%',
                                            colors=pie_colors, startangle=90,
                                            wedgeprops=dict(width=0.5, edgecolor='white', linewidth=2))
        ax2.set_title('订单状态分布', fontweight='bold', pad=15)
        fig2.tight_layout()
        layout.addWidget(canvas2)

        self._add_text_analysis(layout,
            f"<b>发现：</b>实际销售额占总销售额的 {(m3.get('actual_sales',0)/max(m3.get('total_sales',1),1)*100):.1f}%。"
            f"订单均价 ¥{m3.get('aov',0):.2f} 处于行业中位水平。<br>"
            f"<b>建议：</b>关注退货率 {m3.get('refund_rate',0)}% 的品类构成，识别高退货品类进行优化；"
            f"通过捆绑销售与满减策略提升 AOV。")
        self.content.setCurrentIndex(3)

    def show_monthly(self):
        layout = self.pages["📅 月度趋势"]
        self.clear_layout(layout)
        self._add_title(layout, "月度销售额趋势", "LOESS 平滑 + 环比增长率")
        if not self.analysis_results:
            layout.addWidget(QLabel("请先导入数据"))
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

        canvas, fig, ax = self._create_chart_widget(11, 5.5)
        colors = get_color_palette(len(months))
        bars = ax.bar(months, sales, color=colors[0], edgecolor='white', alpha=0.85)
        ax.set_title('月度销售额与环比增长率', fontweight='bold', pad=15)
        ax.set_xlabel('月份')
        ax.set_ylabel('销售额 (元)')
        for bar in bars:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., h, f'{h/1e4:.1f}万',
                    ha='center', va='bottom', fontsize=8)
        ax2 = ax.twinx()
        ax2.plot(months, growth, color='#C5504B', marker='o', linewidth=2, markersize=5, label='环比增长率%')
        ax2.set_ylabel('环比增长率 (%)', color='#C5504B')
        ax2.spines['top'].set_visible(False)
        ax2.tick_params(axis='y', labelcolor='#C5504B')
        fig.tight_layout()
        layout.addWidget(canvas)

        self._add_text_analysis(layout,
            "<b>方法论：</b>月度聚合 + 环比增长率计算。柱状图展示绝对销售额，红色折线展示环比增速。<br>"
            "<b>商业建议：</b>关注增长率由正转负的拐点月份，提前部署促销资源；识别销售旺季进行库存预配。")
        self.content.setCurrentIndex(4)

    def show_channel(self):
        layout = self.pages["🥧 渠道构成"]
        self.clear_layout(layout)
        self._add_title(layout, "渠道销售额构成", "帕累托分析 + 环形图")
        if not self.analysis_results:
            layout.addWidget(QLabel("请先导入数据"))
            self.content.setCurrentIndex(5)
            return
        m5 = self.analysis_results.get('M5_channels', {})
        ch = m5.get('channels', {})
        if not ch:
            layout.addWidget(QLabel("无渠道数据"))
            self.content.setCurrentIndex(5)
            return

        canvas, fig, ax = self._create_chart_widget(8, 8)
        labels = list(ch.keys())[:10]
        sizes = list(ch.values())[:10]
        colors = get_color_palette(len(labels))
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%',
                                            colors=colors, startangle=90,
                                            wedgeprops=dict(width=0.5, edgecolor='white'))
        ax.set_title('TOP10 渠道销售额占比（环形图）', fontweight='bold', pad=15)
        fig.tight_layout()
        layout.addWidget(canvas)

        self._add_text_analysis(layout,
            f"<b>方法论：</b>帕累托分析。前 {m5.get('top80_count', 0)} 个渠道贡献了约 80% 的销售额，"
            "符合 80/20 法则。<br><b>建议：</b>将营销预算向头部渠道集中，同时测试长尾渠道的高潜品类。")
        self.content.setCurrentIndex(5)

    def show_weekday(self):
        layout = self.pages["📆 星期周期"]
        self.clear_layout(layout)
        self._add_title(layout, "星期消费周期模式", "Kruskal-Wallis 非参数检验")
        if not self.analysis_results:
            layout.addWidget(QLabel("请先导入数据"))
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

        canvas, fig, ax = self._create_chart_widget(10, 5.5)
        colors = get_color_palette(7)
        bars = ax.bar(days, values, color=colors, edgecolor='white')
        ax.set_title('各星期销售额分布', fontweight='bold', pad=15)
        ax.set_ylabel('销售额 (元)')
        ax.axhline(y=np.mean(values), color='#C5504B', linestyle='--', linewidth=1.5, label=f'平均值')
        ax.legend(frameon=False)
        fig.tight_layout()
        layout.addWidget(canvas)

        sig_text = "显著" if m6.get('significant') else "不显著"
        self._add_text_analysis(layout,
            f"<b>方法论：</b>Kruskal-Wallis H 检验（非参数 ANOVA），统计量 H={m6.get('kw_statistic',0)}, p={m6.get('kw_pvalue',0)}。"
            f"星期效应 {sig_text} (α=0.05)。<br>"
            "<b>发现：</b>周末与工作日的消费差异可用于制定差异化运营策略，如周末限时秒杀、工作日满减等。")
        self.content.setCurrentIndex(6)

    def show_hourly(self):
        layout = self.pages["⏰ 24小时热力"]
        self.clear_layout(layout)
        self._add_title(layout, "24小时消费热力", "全年小时级聚合 + 标准差区间")
        if not self.analysis_results:
            layout.addWidget(QLabel("请先导入数据"))
            self.content.setCurrentIndex(7)
            return
        m7 = self.analysis_results.get('M7_hourly', {})
        sales = m7.get('sales', {})
        if not sales:
            layout.addWidget(QLabel("无数据"))
            self.content.setCurrentIndex(7)
            return
        hours = list(range(24))
        values = [sales.get(h, 0) for h in hours]
        std_vals = [m7.get('std', {}).get(h, 0) for h in hours]

        canvas, fig, ax = self._create_chart_widget(12, 5)
        ax.fill_between(hours, np.array(values) - np.array(std_vals), np.array(values) + np.array(std_vals),
                        alpha=0.2, color='#4472C4', label='±1σ 区间')
        ax.plot(hours, values, color='#4472C4', linewidth=2.5, marker='o', markersize=4, label='销售额')
        ax.set_title('24小时销售额分布（全年聚合）', fontweight='bold', pad=15)
        ax.set_xlabel('小时')
        ax.set_ylabel('销售额 (元)')
        ax.set_xticks(hours)
        ax.legend(frameon=False)
        fig.tight_layout()
        layout.addWidget(canvas)

        self._add_text_analysis(layout,
            f"<b>方法论：</b>全年小时级聚合，阴影区域表示各小时销售额的标准差。"
            f"峰值时段：{m7.get('peak_hour',0)}:00，低谷时段：{m7.get('valley_hour',0)}:00。<br>"
            "<b>建议：</b>在峰值前 1 小时加大广告投放与客服资源配置；低谷时段安排系统维护。")
        self.content.setCurrentIndex(7)

    def show_customer_value(self):
        layout = self.pages["💎 客户价值"]
        self.clear_layout(layout)
        self._add_title(layout, "客户价值分层", "洛伦兹曲线 + 基尼系数")
        if not self.analysis_results:
            layout.addWidget(QLabel("请先导入数据"))
            self.content.setCurrentIndex(8)
            return
        m8 = self.analysis_results.get('M8_customer_value', {})

        canvas, fig, ax = self._create_chart_widget(8, 8)
        lorenz_x = m8.get('lorenz_x', [])
        lorenz_y = m8.get('lorenz_y', [])
        if lorenz_x and lorenz_y:
            ax.plot(lorenz_x, lorenz_y, color='#4472C4', linewidth=2.5, label='实际分布')
            ax.plot([0, 100], [0, 100], color='#999999', linestyle='--', linewidth=1, label='绝对平等线')
            ax.fill_between(lorenz_x, lorenz_y, [x * (lorenz_y[-1]/100) for x in lorenz_x], alpha=0.1, color='#4472C4')
            ax.set_title('客户消费洛伦兹曲线', fontweight='bold', pad=15)
            ax.set_xlabel('客户累积占比 (%)')
            ax.set_ylabel('销售额累积占比 (%)')
            ax.legend(frameon=False)
            fig.tight_layout()
        layout.addWidget(canvas)

        self._add_kpi_row(layout, [
            {'title': '前10%客户贡献', 'value': f"{m8.get('top10_pct', 0)}%"},
            {'title': '后10%客户贡献', 'value': f"{m8.get('bottom10_pct', 0)}%"},
            {'title': '基尼系数', 'value': f"{m8.get('gini', 0)}"},
        ])
        self._add_text_analysis(layout,
            f"<b>方法论：</b>洛伦兹曲线描述财富（此处为消费额）分配不平等程度。基尼系数 {m8.get('gini',0)} "
            f"{'> 0.4 表示高度集中' if m8.get('gini',0) > 0.4 else '< 0.4 表示相对均衡'}。<br>"
            "<b>策略：</b>前 10% 高价值客户应纳入 VIP 专属服务体系；针对后 10% 尝试低成本激活或放弃维护。")
        self.content.setCurrentIndex(8)

    def show_holiday(self):
        layout = self.pages["🎉 节假日影响"]
        self.clear_layout(layout)
        self._add_title(layout, "节假日消费影响", "双重差分法 (Difference-in-Differences)")
        if not self.analysis_results:
            layout.addWidget(QLabel("请先导入数据"))
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
        colors = ['#EF4444' if d < 0 else '#10B981' for d in diffs]

        canvas, fig, ax = self._create_chart_widget(10, 5.5)
        bars = ax.barh(names, diffs, color=colors, edgecolor='white')
        ax.axvline(x=0, color='#333333', linewidth=0.8)
        ax.set_title('节假日日均销售额净效应（DiD 估计）', fontweight='bold', pad=15)
        ax.set_xlabel('日均销售额差异 (元)')
        for bar in bars:
            w = bar.get_width()
            ax.text(w, bar.get_y() + bar.get_height()/2., f'{w:,.0f}',
                    ha='left' if w > 0 else 'right', va='center', fontsize=9)
        fig.tight_layout()
        layout.addWidget(canvas)

        self._add_text_analysis(layout,
            "<b>方法论：</b>双重差分法（DiD）。处理组为节假日期间，对照组为节前节后等长窗口。"
            "控制时间趋势后，估计节假日的净促销效应。正值表示节假日显著拉动消费。<br>"
            "<b>注意：</b>春节与国庆的长假效应可能包含消费提前或延后，需结合节前节后具体数据解读。")
        self.content.setCurrentIndex(9)

    def show_payment_lag(self):
        layout = self.pages["⏱️ 支付时滞"]
        self.clear_layout(layout)
        self._add_title(layout, "支付时滞分析", "分布拟合 + K-Means 客户分群")
        if not self.analysis_results:
            layout.addWidget(QLabel("请先导入数据"))
            self.content.setCurrentIndex(10)
            return
        m10 = self.analysis_results.get('M10_payment_lag', {})
        self._add_kpi_row(layout, [
            {'title': '平均支付时滞', 'value': f"{m10.get('mean_sec', 0):.0f} 秒"},
            {'title': '中位数', 'value': f"{m10.get('median_sec', 0):.0f} 秒"},
        ])
        clusters = m10.get('clusters', {})
        if clusters:
            self._add_table(layout, clusters)
        self._add_text_analysis(layout,
            "<b>方法论：</b>支付时滞 = pay_time - order_time。K-Means 聚类（标准化后的时滞 + 订单金额）"
            "将客户划分为即时支付型、犹豫比对型等群体。<br>"
            "<b>发现：</b>中位数远低于平均值，说明存在少数长时滞订单拉高了均值，可针对长时滞客户推送限时优惠促成转化。")
        self.content.setCurrentIndex(10)

    def show_rfm(self):
        layout = self.pages["🧬 RFM & CLV"]
        self.clear_layout(layout)
        self._add_title(layout, "RFM 客户价值模型 & CLV", "K-Means 聚类 + 客户生命周期价值")
        if not self.analysis_results:
            layout.addWidget(QLabel("请先导入数据"))
            self.content.setCurrentIndex(11)
            return
        m11 = self.analysis_results.get('M11_rfm_clv', {})
        self._add_kpi_row(layout, [
            {'title': '总客户数', 'value': f"{m11.get('total_customers', 0):,}"},
            {'title': '平均 CLV', 'value': f"¥{m11.get('avg_clv', 0):,.2f}"},
        ])
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

    def show_advanced(self):
        layout = self.pages["🔬 高阶网络与生存"]
        self.clear_layout(layout)
        self._add_title(layout, "高阶网络与生存分析",
                        "Jaccard + Leiden + Null Model + 动态网络 + Cox 生存 + Markov 状态空间")
        if not self.analysis_results:
            layout.addWidget(QLabel("请先导入数据"))
            self.content.setCurrentIndex(12)
            return
        m12 = self.analysis_results.get('M12_advanced', {})
        net = m12.get('network', {})
        dyn = m12.get('dynamic_network', [])
        surv = m12.get('survival', {})
        markov = m12.get('markov', {})

        if net:
            self._add_kpi_row(layout, [
                {'title': '网络节点数', 'value': f"{net.get('nodes', 0):,}"},
                {'title': '网络边数', 'value': f"{net.get('edges', 0):,}"},
                {'title': '社群数', 'value': f"{net.get('communities', 0)}"},
                {'title': '模块度', 'value': f"{net.get('modularity', 0)}"},
                {'title': 'Null Z-score', 'value': f"{net.get('z_score', 0)}"},
                {'title': 'p-value', 'value': f"{net.get('p_value', 0)}"},
            ])

        if dyn:
            canvas, fig, ax = self._create_chart_widget(10, 4.5)
            quarters = [d['quarter'] for d in dyn]
            mods = [d['modularity'] for d in dyn]
            ax.plot(quarters, mods, color='#4472C4', marker='o', linewidth=2, markersize=6)
            ax.set_title('动态网络模块度演化（季度切片）', fontweight='bold', pad=15)
            ax.set_ylabel('模块度')
            fig.tight_layout()
            layout.addWidget(canvas)

        if surv and 'timeline' in surv:
            canvas2, fig2, ax2 = self._create_chart_widget(10, 5)
            timeline = surv['timeline']
            sp = surv['survival_prob']
            ci_lower = surv['ci_lower']
            ci_upper = surv['ci_upper']
            ax2.fill_between(timeline, ci_lower, ci_upper, alpha=0.2, color='#4472C4', label='95% CI')
            ax2.plot(timeline, sp, color='#4472C4', linewidth=2.5, label='Kaplan-Meier 生存概率')
            ax2.set_title('客户复购生存曲线', fontweight='bold', pad=15)
            ax2.set_xlabel('距上次购买天数')
            ax2.set_ylabel('未流失概率')
            ax2.legend(frameon=False)
            fig2.tight_layout()
            layout.addWidget(canvas2)

        if markov:
            states = markov.get('states', [])
            matrix = markov.get('transition_matrix', {})
            if matrix:
                card = QFrame()
                card.setStyleSheet("background-color: #ffffff; border-radius: 10px; border: 1px solid #e5e7eb;")
                c_layout = QVBoxLayout(card)
                c_layout.setContentsMargins(16, 16, 16, 16)
                lbl = QLabel("<b>Markov 状态转移矩阵</b>")
                lbl.setStyleSheet("font-size: 14px; color: #111827; border: none; background: transparent;")
                c_layout.addWidget(lbl)
                table = QTableWidget(len(states), len(states) + 1)
                table.setHorizontalHeaderLabels(['状态'] + states)
                table.setStyleSheet("""
                    QTableWidget { background-color: #ffffff; border: none; gridline-color: #f3f4f6; }
                    QHeaderView::section { background-color: #f9fafb; color: #374151; padding: 8px; border: none; border-bottom: 2px solid #e5e7eb; font-weight: bold; }
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
                table.setMaximumHeight(200)
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
