"""
Matplotlib 全局配置：SCI 一区 Top 水准图表规范
字体：英文 Times New Roman，中文 SimSun
配色：Nature/Science 偏好的 muted 色系
"""
import matplotlib.pyplot as plt
import matplotlib as mpl


def configure_sci_style():
    """配置 Matplotlib 为 SCI 出版级样式"""
    plt.rcParams.update({
        # 字体配置
        'font.family': ['Times New Roman', 'SimSun'],
        'font.serif': ['Times New Roman', 'SimSun'],
        'axes.unicode_minus': False,
        'mathtext.fontset': 'stix',

        # 图形尺寸与 DPI
        'figure.dpi': 150,
        'savefig.dpi': 300,
        'figure.figsize': (8, 5.5),
        'figure.facecolor': 'white',

        # 坐标轴
        'axes.linewidth': 0.8,
        'axes.edgecolor': '#333333',
        'axes.labelcolor': '#333333',
        'axes.labelsize': 11,
        'axes.titlesize': 13,
        'axes.titleweight': 'bold',

        # 刻度
        'xtick.major.width': 0.6,
        'ytick.major.width': 0.6,
        'xtick.labelsize': 9,
        'ytick.labelsize': 9,
        'xtick.color': '#555555',
        'ytick.color': '#555555',

        # 网格线
        'axes.grid': True,
        'grid.alpha': 0.25,
        'grid.linestyle': '--',
        'grid.linewidth': 0.5,
        'axes.axisbelow': True,

        # 图例
        'legend.frameon': False,
        'legend.fontsize': 9,
        'legend.loc': 'upper right',

        # 线条与标记
        'lines.linewidth': 1.5,
        'lines.markersize': 5,

        # 保存
        'savefig.facecolor': 'white',
        'savefig.bbox': 'tight',
        'savefig.pad_inches': 0.15,
    })


# SCI 级配色方案
COLORS = {
    'primary': '#4472C4',
    'secondary': '#ED7D31',
    'tertiary': '#A5A5A5',
    'quaternary': '#FFC000',
    'success': '#70AD47',
    'danger': '#C5504B',
    'info': '#5B9BD5',
    'warning': '#FF8C00',
    # Okabe-Ito 色盲友好 palette
    'okabe_ito': [
        '#E69F00', '#56B4E9', '#009E73', '#F0E442',
        '#0072B2', '#D55E00', '#CC79A7', '#999999'
    ],
    # ColorBrewer Set2
    'set2': [
        '#66C2A5', '#FC8D62', '#8DA0CB', '#E78AC3',
        '#A6D854', '#FFD92F', '#E5C494', '#B3B3B3'
    ],
    # 渐变映射
    'gradient': ['#F7FBFF', '#DEEBF7', '#C6DBEF', '#9ECAE1', '#6BAED6', '#4292C6', '#2171B5', '#08519C', '#08306B'],
}


def get_color_palette(n: int, palette: str = 'set2'):
    """获取指定长度的配色列表"""
    from matplotlib import cm
    if palette == 'okabe_ito':
        base = COLORS['okabe_ito']
    elif palette == 'set2':
        base = COLORS['set2']
    else:
        base = COLORS['okabe_ito']
    if n <= len(base):
        return base[:n]
    # 超出基础色数量时，使用 colormap 插值
    cmap = cm.get_cmap('tab20c')
    return [cmap(i / max(n - 1, 1)) for i in range(n)]
