"""
数据清洗引擎：平台归一化、异常检测、数据修复
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from difflib import SequenceMatcher

from config.constants import PLATFORM_MAPPING, ANOMALY_RULES


class DataCleaner:
    """数据清洗与异常检测引擎"""

    def __init__(self, df: pd.DataFrame):
        self.raw_df = df.copy()
        self.cleaned_df = None
        self.anomaly_df = None
        self.platform_mapping_log = []

    def clean(self) -> Tuple[pd.DataFrame, pd.DataFrame, Dict]:
        """
        执行完整清洗流程
        Returns: (cleaned_df, anomaly_df, report)
        """
        df = self.raw_df.copy()
        report = {'original_count': len(df)}

        # 1. 平台归一化
        df = self._normalize_platforms(df)

        # 2. 异常检测（不移除，仅标记）
        anomaly_mask = self._detect_anomalies(df)
        self.anomaly_df = df[anomaly_mask].copy()
        report['anomaly_count'] = int(anomaly_mask.sum())
        report['anomaly_breakdown'] = self._anomaly_breakdown(df)

        # 3. 清洗数据 = 原始数据 - 异常数据
        df_clean = df[~anomaly_mask].copy()

        # 4. 衍生字段
        df_clean = self._engineer_features(df_clean)

        self.cleaned_df = df_clean
        report['cleaned_count'] = len(df_clean)
        report['platform_mapping'] = self.platform_mapping_log

        return df_clean, self.anomaly_df, report

    def _normalize_platforms(self, df: pd.DataFrame) -> pd.DataFrame:
        """平台名称归一化：规则映射 + 模糊匹配"""
        if 'platform_type' not in df.columns:
            return df

        def normalize_platform(val):
            if pd.isna(val):
                return '其他'
            val_str = str(val).strip()
            # 直接规则匹配
            if val_str in PLATFORM_MAPPING:
                mapped = PLATFORM_MAPPING[val_str]
                self.platform_mapping_log.append((val_str, mapped))
                return mapped
            # 模糊匹配
            best_match = None
            best_score = 0.0
            for key in PLATFORM_MAPPING:
                score = SequenceMatcher(None, val_str.lower(), key.lower()).ratio()
                if score > best_score and score > 0.6:
                    best_score = score
                    best_match = key
            if best_match:
                mapped = PLATFORM_MAPPING[best_match]
                self.platform_mapping_log.append((val_str, mapped, best_score))
                return mapped
            self.platform_mapping_log.append((val_str, '其他', 0.0))
            return '其他'

        df['platform_type_raw'] = df['platform_type']
        df['platform_type'] = df['platform_type'].apply(normalize_platform)
        return df

    def _detect_anomalies(self, df: pd.DataFrame) -> pd.Series:
        """多规则异常检测，返回异常 mask"""
        mask = pd.Series(False, index=df.index)
        if 'payment' in df.columns:
            mask |= df['payment'] < 0
        if 'pay_time' in df.columns and 'order_time' in df.columns:
            mask |= df['pay_time'] < df['order_time']
        if 'payment' in df.columns and 'order_amount' in df.columns:
            mask |= df['payment'] > df['order_amount'] * 1.5
        return mask

    def _anomaly_breakdown(self, df: pd.DataFrame) -> Dict[str, int]:
        """异常分类统计"""
        breakdown = {}
        if 'payment' in df.columns:
            cnt = int((df['payment'] < 0).sum())
            if cnt > 0:
                breakdown['支付金额小于0'] = cnt
        if 'pay_time' in df.columns and 'order_time' in df.columns:
            cnt = int((df['pay_time'] < df['order_time']).sum())
            if cnt > 0:
                breakdown['支付时间早于下单时间'] = cnt
        if 'payment' in df.columns and 'order_amount' in df.columns:
            cnt = int((df['payment'] > df['order_amount'] * 1.5).sum())
            if cnt > 0:
                breakdown['支付金额大于订单金额150%'] = cnt
        return breakdown

    def _engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """构建衍生特征"""
        if 'pay_time' in df.columns and 'order_time' in df.columns:
            df['pay_delay_seconds'] = (df['pay_time'] - df['order_time']).dt.total_seconds()
            df['pay_delay_minutes'] = df['pay_delay_seconds'] / 60.0
        if 'order_time' in df.columns:
            df['order_month'] = df['order_time'].dt.month
            df['order_weekday'] = df['order_time'].dt.weekday  # 0=Monday
            df['order_hour'] = df['order_time'].dt.hour
            df['order_date'] = df['order_time'].dt.date
        if 'pay_time' in df.columns:
            df['pay_month'] = df['pay_time'].dt.month
            df['pay_weekday'] = df['pay_time'].dt.weekday
            df['pay_hour'] = df['pay_time'].dt.hour
            df['pay_date'] = df['pay_time'].dt.date
        return df
