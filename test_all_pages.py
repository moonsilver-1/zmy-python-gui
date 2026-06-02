#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全页面自动化测试：不弹GUI，只验证图表渲染"""
import sys, traceback, warnings, os
warnings.filterwarnings('ignore')
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

from PyQt5.QtWidgets import QApplication
app = QApplication(sys.argv)

try:
    from ui.main_window import MainWindow
    from core.data_loader import DataLoader
    from core.data_cleaner import DataCleaner
    from analysis.engine import AnalysisEngine

    print("[1/3] Loading data...")
    df = DataLoader.load_excel('D:/coding/pythonlesson/5/某电商平台2021年订单数据.xlsx')
    print(f"    -> {len(df)} rows")

    print("[2/3] Cleaning & analyzing...")
    cleaner = DataCleaner(df)
    clean_df, anomaly_df, report = cleaner.clean()
    engine = AnalysisEngine(clean_df, anomaly_df)
    results = engine.run_all()
    print(f"    -> {len(clean_df)} clean, {len(anomaly_df)} anomalies")

    print("[3/3] Rendering all pages...")
    window = MainWindow()
    window.analysis_results = results
    window.state = type('obj', (object,), {'cleaned_data': clean_df})()

    pages = [
        ('overview', window.show_overview),
        ('platform', window.show_platform),
        ('anomaly', window.show_anomaly),
        ('kpi', window.show_kpi),
        ('monthly', window.show_monthly),
        ('channel', window.show_channel),
        ('weekday', window.show_weekday),
        ('hourly', window.show_hourly),
        ('customer_value', window.show_customer_value),
        ('holiday', window.show_holiday),
        ('payment_lag', window.show_payment_lag),
        ('rfm', window.show_rfm),
        ('advanced', window.show_advanced),
    ]

    for name, fn in pages:
        try:
            fn()
            print(f"    -> {name}: OK")
        except Exception as e:
            print(f"    -> {name}: FAILED - {e}")
            traceback.print_exc()
            sys.exit(1)

    print("\nALL 13 PAGES PASSED")
except Exception as e:
    traceback.print_exc()
    sys.exit(1)
