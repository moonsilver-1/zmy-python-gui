"""
Cinematic Dark 电影感暗黑科技风格样式定义
参考：Blade Runner 2049, Dune, Social Network
特征：极深蓝黑背景 + 霓虹五色点缀 + 彩色光晕阴影 + 电影级排版
"""

from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, Qt, QParallelAnimationGroup, QSequentialAnimationGroup
from PyQt5.QtGui import QColor, QPalette, QFont
from PyQt5.QtWidgets import QWidget, QGraphicsDropShadowEffect, QLabel, QGraphicsOpacityEffect, QGraphicsColorizeEffect


# ========== 电影感色彩常量 ==========
# 极深蓝黑背景（电影院熄灯感）
CINE_BG = "#0a0a0f"
CINE_BG_SECONDARY = "#0d0d14"
CINE_CARD = "#14141f"
CINE_CARD_BORDER = "rgba(255, 255, 255, 0.06)"
CINE_CARD_HOVER = "#1a1a28"
CINE_TEXT = "#e8e8ec"
CINE_TEXT_SECONDARY = "#6b6b7b"
CINE_TEXT_MUTED = "#444455"

# 霓虹五色点缀（赛博朋克调色板）
CINE_NEON_ORANGE = "#ff6b35"    # 销售额、正向指标
CINE_NEON_CYAN = "#00d4aa"      # 订单数、成功态
CINE_NEON_PURPLE = "#b967ff"    # 分析、洞察
CINE_NEON_PINK = "#ff2e63"      # 退货、异常、警告
CINE_NEON_BLUE = "#4facfe"      # 平台、渠道
CINE_NEON_GOLD = "#ffd700"      # VIP、高价值客户
CINE_NEON_WHITE = "#ffffff"     # 高亮

# 霓虹半透明（用于渐变和光晕）
CINE_NEON_ORANGE_ALPHA = "rgba(255, 107, 53, 0.15)"
CINE_NEON_CYAN_ALPHA = "rgba(0, 212, 170, 0.15)"
CINE_NEON_PURPLE_ALPHA = "rgba(185, 103, 255, 0.15)"
CINE_NEON_PINK_ALPHA = "rgba(255, 46, 99, 0.15)"
CINE_NEON_BLUE_ALPHA = "rgba(79, 172, 254, 0.15)"
CINE_NEON_GOLD_ALPHA = "rgba(255, 215, 0, 0.15)"

# 圆角
CINE_RADIUS_XL = 20
CINE_RADIUS_L = 14
CINE_RADIUS_M = 10
CINE_RADIUS_S = 6

# 电影级字体栈
CINE_FONT_STACK = "'SF Pro Display', 'Inter', -apple-system, 'Segoe UI', 'Microsoft YaHei', sans-serif"
CINE_FONT_MONO = "'SF Mono', 'JetBrains Mono', 'Fira Code', 'Courier New', monospace"


# ========== 全局 QSS 样式表 ==========

def get_cinematic_stylesheet():
    """返回电影感暗黑科技风格的 QSS"""
    return f"""
    /* ===== 全局 ===== */
    QWidget {{
        font-family: {CINE_FONT_STACK};
        font-size: 13px;
        color: {CINE_TEXT};
        background-color: {CINE_BG};
        outline: none;
        border: none;
    }}

    QMainWindow {{
        background-color: {CINE_BG};
        border: none;
    }}

    /* ===== 滚动条 ===== */
    QScrollBar:vertical {{
        background: transparent;
        width: 6px;
        border-radius: 3px;
        margin: 0px;
    }}
    QScrollBar::handle:vertical {{
        background: {CINE_TEXT_MUTED};
        border-radius: 3px;
        min-height: 40px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {CINE_NEON_PURPLE};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    QScrollBar:horizontal {{
        background: transparent;
        height: 6px;
        border-radius: 3px;
    }}
    QScrollBar::handle:horizontal {{
        background: {CINE_TEXT_MUTED};
        border-radius: 3px;
        min-width: 40px;
    }}
    QScrollBar::handle:horizontal:hover {{
        background: {CINE_NEON_PURPLE};
    }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0px;
    }}

    /* ===== 表格 ===== */
    QTableWidget {{
        background-color: {CINE_CARD};
        border: 1px solid {CINE_CARD_BORDER};
        border-radius: {CINE_RADIUS_M}px;
        gridline-color: rgba(255, 255, 255, 0.03);
        selection-background-color: {CINE_NEON_PURPLE_ALPHA};
        selection-color: {CINE_TEXT};
        alternate-background-color: rgba(255, 255, 255, 0.02);
    }}
    QTableWidget::item {{
        padding: 12px 14px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.03);
    }}
    QTableWidget::item:selected {{
        background-color: {CINE_NEON_PURPLE_ALPHA};
        color: {CINE_TEXT};
    }}
    QHeaderView::section {{
        background-color: transparent;
        color: {CINE_TEXT_SECONDARY};
        padding: 12px 14px;
        border: none;
        border-bottom: 1px solid {CINE_CARD_BORDER};
        font-weight: 600;
        font-size: 11px;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }}
    QTableCornerButton::section {{
        background-color: transparent;
        border: none;
    }}

    /* ===== 文本框 ===== */
    QTextEdit, QPlainTextEdit {{
        background-color: {CINE_CARD};
        border: 1px solid {CINE_CARD_BORDER};
        border-radius: {CINE_RADIUS_S}px;
        padding: 16px;
        line-height: 1.7;
        color: {CINE_TEXT};
        font-size: 13px;
    }}
    QTextEdit:focus, QPlainTextEdit:focus {{
        border: 1px solid {CINE_NEON_PURPLE};
    }}

    /* ===== 消息框 ===== */
    QMessageBox {{
        background-color: {CINE_CARD};
    }}
    QMessageBox QLabel {{
        color: {CINE_TEXT};
        font-size: 14px;
    }}
    QMessageBox QPushButton {{
        background-color: {CINE_NEON_PURPLE};
        color: white;
        border-radius: {CINE_RADIUS_S}px;
        padding: 10px 24px;
        font-weight: 600;
        font-size: 13px;
        min-width: 90px;
    }}
    QMessageBox QPushButton:hover {{
        background-color: {CINE_NEON_BLUE};
    }}
    """


# ========== 霓虹配色方案 ==========
CINE_COLORS = [
    CINE_NEON_ORANGE,  # 橙
    CINE_NEON_CYAN,    # 青
    CINE_NEON_PURPLE,  # 紫
    CINE_NEON_BLUE,    # 蓝
    CINE_NEON_PINK,    # 粉
    CINE_NEON_GOLD,    # 金
]

CINE_COLORS_ALPHA = [
    CINE_NEON_ORANGE_ALPHA,
    CINE_NEON_CYAN_ALPHA,
    CINE_NEON_PURPLE_ALPHA,
    CINE_NEON_BLUE_ALPHA,
    CINE_NEON_PINK_ALPHA,
    CINE_NEON_GOLD_ALPHA,
]


def get_cinematic_palette(n):
    """返回电影感霓虹配色列表，支持循环"""
    if n <= len(CINE_COLORS):
        return CINE_COLORS[:n]
    result = CINE_COLORS[:]
    while len(result) < n:
        result.extend(CINE_COLORS)
    return result[:n]


# ========== 电影感阴影效果 ==========

def apply_cinematic_shadow(widget, color_hex=CINE_NEON_PURPLE, blur=40, offset_y=8, alpha=60):
    """为 widget 应用霓虹光晕阴影"""
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(blur)
    shadow.setColor(QColor(color_hex).darker(120))
    color = QColor(color_hex)
    color.setAlpha(alpha)
    shadow.setColor(color)
    shadow.setOffset(0, offset_y)
    widget.setGraphicsEffect(shadow)
    return shadow


def apply_neon_glow(widget, color_hex=CINE_NEON_PURPLE, blur=25):
    """为 widget 应用霓虹发光效果"""
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(blur)
    color = QColor(color_hex)
    color.setAlpha(100)
    shadow.setColor(color)
    shadow.setOffset(0, 0)
    widget.setGraphicsEffect(shadow)
    return shadow


# ========== 动画辅助函数 ==========

def fade_in_widget(widget, duration=500):
    """widget 淡入动画"""
    effect = QGraphicsOpacityEffect(widget)
    widget.setGraphicsEffect(effect)
    anim = QPropertyAnimation(effect, b"opacity")
    anim.setDuration(duration)
    anim.setStartValue(0.0)
    anim.setEndValue(1.0)
    anim.setEasingCurve(QEasingCurve.OutCubic)
    anim.start()
    return anim


def scale_in_widget(widget, duration=500):
    """widget 缩放淡入（电影转场感）"""
    effect = QGraphicsOpacityEffect(widget)
    widget.setGraphicsEffect(effect)
    anim_opacity = QPropertyAnimation(effect, b"opacity")
    anim_opacity.setDuration(duration)
    anim_opacity.setStartValue(0.0)
    anim_opacity.setEndValue(1.0)
    anim_opacity.setEasingCurve(QEasingCurve.OutCubic)

    # 缩放动画通过调整最小尺寸模拟不太方便，用透明度+位移代替
    anim_opacity.start()
    return anim_opacity


def slide_up_in(widget, distance=30, duration=500):
    """从下向上滑入"""
    effect = QGraphicsOpacityEffect(widget)
    widget.setGraphicsEffect(effect)
    anim_opacity = QPropertyAnimation(effect, b"opacity")
    anim_opacity.setDuration(duration)
    anim_opacity.setStartValue(0.0)
    anim_opacity.setEndValue(1.0)
    anim_opacity.setEasingCurve(QEasingCurve.OutCubic)
    anim_opacity.start()
    return anim_opacity


# ========== 数字滚动动画组件 ==========
from PyQt5.QtCore import QTimer

class RollingNumberLabel(QLabel):
    """数字滚动标签（电影感计数器效果）"""
    def __init__(self, parent=None, prefix="", suffix="", decimals=0):
        super().__init__(parent)
        self.prefix = prefix
        self.suffix = suffix
        self.decimals = decimals
        self._target_value = 0.0
        self._current_value = 0.0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_value)
        self.setStyleSheet(f"color: {CINE_TEXT}; font-size: 32px; font-weight: 700; background: transparent;")

    def set_value(self, value, duration=1200):
        self._target_value = float(value)
        self._current_value = 0.0
        self._duration = duration
        self._step = 0
        self._total_steps = max(int(duration / 16), 1)  # 60fps
        self._timer.start(16)

    def _update_value(self):
        self._step += 1
        progress = self._step / self._total_steps
        # ease out cubic
        progress = 1 - pow(1 - progress, 3)
        self._current_value = self._target_value * progress
        if self.decimals > 0:
            text = f"{self.prefix}{self._current_value:,.{self.decimals}f}{self.suffix}"
        else:
            text = f"{self.prefix}{int(self._current_value):,}{self.suffix}"
        self.setText(text)
        if self._step >= self._total_steps:
            self._timer.stop()
            if self.decimals > 0:
                self.setText(f"{self.prefix}{self._target_value:,.{self.decimals}f}{self.suffix}")
            else:
                self.setText(f"{self.prefix}{int(self._target_value):,}{self.suffix}")


# ========== 旧版兼容 ==========

def get_theme(theme_name='light'):
    """兼容旧接口"""
    return get_cinematic_stylesheet()


def get_glass_stylesheet(theme='light'):
    return get_cinematic_stylesheet()


def get_apple_palette(n):
    return get_cinematic_palette(n)
