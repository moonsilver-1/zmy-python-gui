"""
常量定义：节假日、平台映射规则等
"""
from datetime import date
from typing import List, Tuple

# 2021 年中国法定节假日（小长假）
HOLIDAYS_2021: List[Tuple[date, date, str]] = [
    (date(2021, 1, 1), date(2021, 1, 3), "元旦"),
    (date(2021, 2, 11), date(2021, 2, 17), "春节"),
    (date(2021, 4, 3), date(2021, 4, 5), "清明"),
    (date(2021, 5, 1), date(2021, 5, 5), "劳动节"),
    (date(2021, 6, 12), date(2021, 6, 14), "端午"),
    (date(2021, 9, 19), date(2021, 9, 21), "中秋"),
    (date(2021, 10, 1), date(2021, 10, 7), "国庆"),
]

# 平台归一化映射表（处理编码乱码与变体）
# 注意：由于源文件编码损坏，部分中文字符显示为乱码，此处同时收录乱码形式与标准形式
PLATFORM_MAPPING = {
    # 微信系列
    '微信': '微信',
    '΢��': '微信',
    '΢ ��': '微信',
    '΢信': '微信',
    'vx': '微信',
    'VX': '微信',
    'wechat': '微信',
    'WeChat': '微信',
    '微': '微信',
    # 支付宝系列
    '支付宝': '支付宝',
    '֧����': '支付宝',
    '֧': '支付宝',
    '֧��������': '支付宝',
    '֧����': '支付宝',
    'alipay': '支付宝',
    'Alipay': '支付宝',
    '支': '支付宝',
    # APP
    'APP': 'APP',
    'AP P': 'APP',
    'app': 'APP',
    'App': 'APP',
    # WEB
    'WEB': 'WEB',
    'web': 'WEB',
    'Web': 'WEB',
    '��ҳ': 'WEB',
    '�� վ': 'WEB',
    '网页': 'WEB',
    # 微博/其他（编码损坏无法识别的归入其他）
    'ޱ': '其他',
    'ޱ����': '其他',
    '微博': '其他',
}

# 星期映射
WEEKDAY_NAMES = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']

# 异常检测规则阈值
ANOMALY_RULES = {
    'negative_payment': {'condition': 'payment < 0', 'desc': '支付金额小于0'},
    'payment_after_order': {'condition': 'payTime < orderTime', 'desc': '支付时间早于下单时间'},
    'payment_exceeds_order': {'condition': 'payment > orderAmount * 1.5', 'desc': '支付金额大于订单金额的150%'},
}

# RFM 分位数（用于 K-Means 前的标准化）
RFM_QUANTILES = [0.2, 0.4, 0.6, 0.8]
