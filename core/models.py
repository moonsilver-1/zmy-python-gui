"""
数据模型与共享状态
"""
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any
import pandas as pd


@dataclass
class AppState:
    """应用全局状态"""
    raw_data: Optional[pd.DataFrame] = None
    cleaned_data: Optional[pd.DataFrame] = None
    anomaly_data: Optional[pd.DataFrame] = None
    analysis_results: Dict[str, Any] = field(default_factory=dict)
    current_theme: str = 'light'
    file_path: Optional[str] = None

    def reset(self):
        self.raw_data = None
        self.cleaned_data = None
        self.anomaly_data = None
        self.analysis_results = {}
        self.file_path = None


# 全局单例
state = AppState()
