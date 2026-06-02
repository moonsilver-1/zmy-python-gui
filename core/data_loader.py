"""
数据加载模块：读取 Excel 并修复编码问题
"""
import pandas as pd
from typing import Optional


class DataLoader:
    """电商订单数据加载器"""

    @staticmethod
    def load_excel(file_path: str) -> Optional[pd.DataFrame]:
        """加载 Excel 文件并执行基础类型转换"""
        try:
            df = pd.read_excel(file_path, engine='openpyxl')
            df = DataLoader._standardize_columns(df)
            df = DataLoader._convert_types(df)
            return df
        except Exception as e:
            raise RuntimeError(f"数据加载失败: {e}")

    @staticmethod
    def _standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
        """标准化列名"""
        column_map = {
            'orderID': 'order_id',
            'userID': 'user_id',
            'goodsID': 'goods_id',
            'orderAmount': 'order_amount',
            'payment': 'payment',
            'chanelID': 'channel_id',
            'platfromType': 'platform_type',
            'orderTime': 'order_time',
            'payTime': 'pay_time',
            'chargeback': 'chargeback',
        }
        df = df.rename(columns={k: v for k, v in column_map.items() if k in df.columns})
        return df

    @staticmethod
    def _convert_types(df: pd.DataFrame) -> pd.DataFrame:
        """转换数据类型"""
        if 'order_time' in df.columns:
            df['order_time'] = pd.to_datetime(df['order_time'], errors='coerce')
        if 'pay_time' in df.columns:
            df['pay_time'] = pd.to_datetime(df['pay_time'], errors='coerce')
        if 'order_amount' in df.columns:
            df['order_amount'] = pd.to_numeric(df['order_amount'], errors='coerce')
        if 'payment' in df.columns:
            df['payment'] = pd.to_numeric(df['payment'], errors='coerce')
        if 'chargeback' in df.columns:
            df['chargeback'] = pd.to_numeric(df['chargeback'], errors='coerce').fillna(0).astype(int)
        return df
