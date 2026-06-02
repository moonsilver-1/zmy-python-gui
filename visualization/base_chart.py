"""
图表基类：统一封装 Matplotlib 嵌入 Qt 的渲染逻辑
"""
import io
import base64
from typing import Optional, Tuple

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from config.rc_params import configure_sci_style, get_color_palette


class ChartCanvas(FigureCanvas):
    """封装 FigureCanvas，支持 SCI 级图表渲染与交互"""

    def __init__(self, parent=None, width=8, height=5.5, dpi=150):
        configure_sci_style()
        self.fig = Figure(figsize=(width, height), dpi=dpi, facecolor='white')
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)

    def clear(self):
        self.axes.clear()
        # 移除上边框和右边框
        self.axes.spines['top'].set_visible(False)
        self.axes.spines['right'].set_visible(False)

    def set_title(self, title: str, subtitle: Optional[str] = None):
        if subtitle:
            self.axes.set_title(f"{title}\n{subtitle}", fontsize=13, fontweight='bold', pad=15)
        else:
            self.axes.set_title(title, fontsize=13, fontweight='bold', pad=15)

    def annotate_significance(self, x1, x2, y, h, text, ax=None):
        """绘制显著性标注星号线"""
        ax = ax or self.axes
        ax.plot([x1, x1, x2, x2], [y, y + h, y + h, y], lw=0.8, c='#333333')
        ax.text((x1 + x2) * 0.5, y + h + 0.02 * y, text, ha='center', va='bottom', fontsize=9)

    def tight_layout(self):
        self.fig.tight_layout()

    def to_png_bytes(self) -> bytes:
        buf = io.BytesIO()
        self.fig.savefig(buf, format='png', dpi=300, bbox_inches='tight')
        buf.seek(0)
        return buf.getvalue()

    def to_svg_string(self) -> str:
        buf = io.BytesIO()
        self.fig.savefig(buf, format='svg', bbox_inches='tight')
        buf.seek(0)
        return buf.getvalue().decode('utf-8')


def create_chart_widget(parent=None, width=8, height=5.5, dpi=150, with_toolbar=True):
    """创建包含 FigureCanvas 和可选工具栏的 QWidget"""
    from PyQt5.QtWidgets import QWidget, QVBoxLayout
    widget = QWidget(parent)
    layout = QVBoxLayout(widget)
    layout.setContentsMargins(0, 0, 0, 0)

    canvas = ChartCanvas(parent=widget, width=width, height=height, dpi=dpi)
    layout.addWidget(canvas)

    if with_toolbar:
        toolbar = NavigationToolbar(canvas, widget)
        layout.addWidget(toolbar)

    return widget, canvas
