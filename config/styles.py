"""
QSS 样式定义：Modern SaaS Dashboard 风格
支持 Dark / Light 双主题
"""

LIGHT_THEME = """
/* 全局 */
QWidget {
    font-family: "Microsoft YaHei", "SimHei", sans-serif;
    font-size: 13px;
    color: #1f2937;
    background-color: #f3f4f6;
}

/* 主窗口 */
QMainWindow {
    background-color: #f3f4f6;
    border: none;
}

/* 侧边栏 */
#sidebar {
    background-color: #1e293b;
    border-right: 1px solid #334155;
}
#sidebar QPushButton {
    background-color: transparent;
    color: #cbd5e1;
    border: none;
    padding: 14px 20px;
    text-align: left;
    font-size: 13px;
    border-left: 3px solid transparent;
}
#sidebar QPushButton:hover {
    background-color: #334155;
    color: #ffffff;
}
#sidebar QPushButton:checked, #sidebar QPushButton#active {
    background-color: #2563eb;
    color: #ffffff;
    border-left: 3px solid #60a5fa;
}

/* 顶部栏 */
#top_bar {
    background-color: #ffffff;
    border-bottom: 1px solid #e5e7eb;
}

/* KPI 卡片 */
#kpi_card {
    background-color: #ffffff;
    border-radius: 8px;
    border: 1px solid #e5e7eb;
    padding: 16px;
}
#kpi_card #title {
    color: #6b7280;
    font-size: 12px;
}
#kpi_card #value {
    color: #111827;
    font-size: 24px;
    font-weight: bold;
}
#kpi_card #delta {
    font-size: 11px;
}
#kpi_card #delta[positive="true"] {
    color: #059669;
}
#kpi_card #delta[positive="false"] {
    color: #dc2626;
}

/* 分析卡片 */
#analysis_card {
    background-color: #ffffff;
    border-radius: 10px;
    border: 1px solid #e5e7eb;
    padding: 20px;
}
#analysis_card #card_title {
    font-size: 15px;
    font-weight: bold;
    color: #111827;
    margin-bottom: 12px;
}

/* 按钮 */
QPushButton#primary_button {
    background-color: #2563eb;
    color: white;
    border-radius: 6px;
    padding: 8px 18px;
    font-weight: bold;
}
QPushButton#primary_button:hover {
    background-color: #1d4ed8;
}
QPushButton#secondary_button {
    background-color: #ffffff;
    color: #374151;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    padding: 8px 18px;
}
QPushButton#secondary_button:hover {
    background-color: #f9fafb;
}

/* 表格 */
QTableView {
    background-color: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 6px;
    gridline-color: #f3f4f6;
    selection-background-color: #dbeafe;
}
QTableView::item {
    padding: 6px 10px;
    border-bottom: 1px solid #f3f4f6;
}
QHeaderView::section {
    background-color: #f9fafb;
    color: #374151;
    padding: 8px 10px;
    border: none;
    border-bottom: 2px solid #e5e7eb;
    font-weight: bold;
}

/* 滚动条 */
QScrollBar:vertical {
    background: #f3f4f6;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #cbd5e1;
    border-radius: 4px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background: #94a3b8;
}

/* 文本框 */
QTextEdit, QPlainTextEdit {
    background-color: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 6px;
    padding: 10px;
    line-height: 1.6;
}
"""

DARK_THEME = """
QWidget {
    font-family: "Microsoft YaHei", "SimHei", sans-serif;
    font-size: 13px;
    color: #e2e8f0;
    background-color: #0f172a;
}
QMainWindow {
    background-color: #0f172a;
    border: none;
}
#sidebar {
    background-color: #1e293b;
    border-right: 1px solid #334155;
}
#sidebar QPushButton {
    background-color: transparent;
    color: #94a3b8;
    border: none;
    padding: 14px 20px;
    text-align: left;
    font-size: 13px;
    border-left: 3px solid transparent;
}
#sidebar QPushButton:hover {
    background-color: #334155;
    color: #f8fafc;
}
#sidebar QPushButton:checked, #sidebar QPushButton#active {
    background-color: #3b82f6;
    color: #ffffff;
    border-left: 3px solid #60a5fa;
}
#top_bar {
    background-color: #1e293b;
    border-bottom: 1px solid #334155;
}
#kpi_card {
    background-color: #1e293b;
    border-radius: 8px;
    border: 1px solid #334155;
    padding: 16px;
}
#kpi_card #title {
    color: #94a3b8;
    font-size: 12px;
}
#kpi_card #value {
    color: #f8fafc;
    font-size: 24px;
    font-weight: bold;
}
#analysis_card {
    background-color: #1e293b;
    border-radius: 10px;
    border: 1px solid #334155;
    padding: 20px;
}
#analysis_card #card_title {
    font-size: 15px;
    font-weight: bold;
    color: #f8fafc;
    margin-bottom: 12px;
}
QPushButton#primary_button {
    background-color: #3b82f6;
    color: white;
    border-radius: 6px;
    padding: 8px 18px;
    font-weight: bold;
}
QPushButton#primary_button:hover {
    background-color: #2563eb;
}
QPushButton#secondary_button {
    background-color: #1e293b;
    color: #e2e8f0;
    border: 1px solid #475569;
    border-radius: 6px;
    padding: 8px 18px;
}
QPushButton#secondary_button:hover {
    background-color: #334155;
}
QTableView {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 6px;
    gridline-color: #334155;
    selection-background-color: #1e40af;
    color: #e2e8f0;
}
QTableView::item {
    padding: 6px 10px;
    border-bottom: 1px solid #334155;
}
QHeaderView::section {
    background-color: #334155;
    color: #cbd5e1;
    padding: 8px 10px;
    border: none;
    border-bottom: 2px solid #475569;
    font-weight: bold;
}
QScrollBar:vertical {
    background: #1e293b;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #475569;
    border-radius: 4px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background: #64748b;
}
QTextEdit, QPlainTextEdit {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 10px;
    color: #e2e8f0;
    line-height: 1.6;
}
"""


def get_theme(theme_name: str = 'light') -> str:
    return LIGHT_THEME if theme_name == 'light' else DARK_THEME
