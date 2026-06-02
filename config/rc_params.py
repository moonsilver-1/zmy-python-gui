"""
Matplotlib 全局配置：Cinematic Dark 电影感暗黑科技风格
参考：Blade Runner 2049, Dune, Cyberpunk 2077
字体：SF Pro / Inter / Microsoft YaHei
配色：霓虹赛博朋克五色
"""
import matplotlib.pyplot as plt
import matplotlib as mpl


# ========== 电影感霓虹配色 ==========
CINE_NEON_ORANGE = '#ff6b35'
CINE_NEON_CYAN = '#00d4aa'
CINE_NEON_PURPLE = '#b967ff'
CINE_NEON_PINK = '#ff2e63'
CINE_NEON_BLUE = '#4facfe'
CINE_NEON_GOLD = '#ffd700'
CINE_NEON_WHITE = '#ffffff'

CINE_COLORS = [
    CINE_NEON_ORANGE,
    CINE_NEON_CYAN,
    CINE_NEON_PURPLE,
    CINE_NEON_BLUE,
    CINE_NEON_PINK,
    CINE_NEON_GOLD,
]

# 半透明霓虹（用于填充、渐变）
CINE_COLORS_ALPHA = [
    (1.0, 0.42, 0.21, 0.15),
    (0.0, 0.83, 0.67, 0.15),
    (0.73, 0.40, 1.0, 0.15),
    (0.31, 0.67, 1.0, 0.15),
    (1.0, 0.18, 0.39, 0.15),
    (1.0, 0.84, 0.0, 0.15),
]

# 背景与文字
CINE_BG = '#0a0a0f'
CINE_CARD = '#14141f'
CINE_TEXT = '#e8e8ec'
CINE_TEXT_SECONDARY = '#6b6b7b'
CINE_GRID = 'rgba(255, 255, 255, 0.05)'


def configure_sci_style(theme='dark'):
    """配置 Matplotlib 为电影感暗黑科技风格"""
    facecolor = CINE_CARD if theme == 'dark' else 'white'
    textcolor = CINE_TEXT if theme == 'dark' else '#1d1d1f'
    gridcolor = '#2a2a3a' if theme == 'dark' else '#e5e5ea'
    edgecolor = '#2a2a3a' if theme == 'dark' else '#c7c7cc'

    plt.rcParams.update({
        # 字体配置：只使用 Windows 确定存在的字体，避免 findfont 警告
        'font.family': ['sans-serif'],
        'font.sans-serif': ['Microsoft YaHei', 'SimHei', 'Arial', 'DejaVu Sans'],
        'font.serif': ['Times New Roman', 'SimSun'],
        'axes.unicode_minus': False,
        'mathtext.fontset': 'stix',

        # 图形尺寸与 DPI
        'figure.dpi': 150,
        'savefig.dpi': 300,
        'figure.figsize': (9, 5.5),
        'figure.facecolor': facecolor,

        # 坐标轴
        'axes.linewidth': 0.5,
        'axes.edgecolor': edgecolor,
        'axes.labelcolor': textcolor,
        'axes.labelsize': 11,
        'axes.titlesize': 14,
        'axes.titleweight': 'bold',
        'axes.facecolor': facecolor,

        # 刻度
        'xtick.major.width': 0.5,
        'ytick.major.width': 0.5,
        'xtick.labelsize': 9,
        'ytick.labelsize': 9,
        'xtick.color': textcolor,
        'ytick.color': textcolor,

        # 网格线（极淡，营造氛围感）
        'axes.grid': True,
        'grid.alpha': 0.12,
        'grid.linestyle': '-',
        'grid.linewidth': 0.5,
        'grid.color': gridcolor,
        'axes.axisbelow': True,

        # 图例
        'legend.frameon': True,
        'legend.fontsize': 9,
        'legend.loc': 'upper right',
        'legend.facecolor': facecolor,
        'legend.edgecolor': edgecolor,
        'legend.fancybox': True,

        # 线条与标记
        'lines.linewidth': 2.0,
        'lines.markersize': 6,
        'lines.markeredgecolor': facecolor,
        'lines.markeredgewidth': 1.5,

        # 保存
        'savefig.facecolor': facecolor,
        'savefig.bbox': 'tight',
        'savefig.pad_inches': 0.2,
        'text.color': textcolor,
    })


# ========== 配色获取 ==========

def get_color_palette(n: int, palette: str = 'cinematic'):
    """获取电影感霓虹配色列表"""
    if palette == 'cinematic':
        base = CINE_COLORS
    elif palette == 'okabe_ito':
        base = ['#E69F00', '#56B4E9', '#009E73', '#F0E442', '#0072B2', '#D55E00', '#CC79A7', '#999999']
    elif palette == 'set2':
        base = ['#66C2A5', '#FC8D62', '#8DA0CB', '#E78AC3', '#A6D854', '#FFD92F', '#E5C494', '#B3B3B3']
    else:
        base = CINE_COLORS
    if n <= len(base):
        return base[:n]
    from matplotlib import cm
    cmap = cm.get_cmap('tab20c')
    return [cmap(i / max(n - 1, 1)) for i in range(n)]


# 旧版兼容
COLORS = {
    'primary': CINE_NEON_ORANGE,
    'secondary': CINE_NEON_CYAN,
    'tertiary': CINE_NEON_PURPLE,
    'quaternary': CINE_NEON_BLUE,
    'success': CINE_NEON_CYAN,
    'danger': CINE_NEON_PINK,
    'info': CINE_NEON_BLUE,
    'warning': CINE_NEON_GOLD,
    'okabe_ito': ['#E69F00', '#56B4E9', '#009E73', '#F0E442', '#0072B2', '#D55E00', '#CC79A7', '#999999'],
    'set2': ['#66C2A5', '#FC8D62', '#8DA0CB', '#E78AC3', '#A6D854', '#FFD92F', '#E5C494', '#B3B3B3'],
    'gradient': ['#F7FBFF', '#DEEBF7', '#C6DBEF', '#9ECAE1', '#6BAED6', '#4292C6', '#2171B5', '#08519C', '#08306B'],
}
