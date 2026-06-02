"""
分析引擎：整合全部 13 个分析模块
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
from collections import Counter

from scipy import stats
from scipy.optimize import curve_fit
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

import networkx as nx
from networkx.algorithms import community as nx_comm

from config.constants import HOLIDAYS_2021, WEEKDAY_NAMES, RFM_QUANTILES


class AnalysisEngine:
    """统一分析调度器"""

    def __init__(self, df_clean: pd.DataFrame, df_anomaly: pd.DataFrame):
        self.df = df_clean.copy()
        self.df_anomaly = df_anomaly.copy()
        self.results: Dict[str, Any] = {}

    # ==================== M1: 平台归一化 ====================
    def analyze_platforms(self) -> Dict:
        df = self.df
        platform_counts = df['platform_type'].value_counts().to_dict()
        platform_amount = df.groupby('platform_type')['payment'].sum().to_dict()
        return {
            'counts': platform_counts,
            'amounts': {k: round(v, 2) for k, v in platform_amount.items()},
            'total_orders': len(df),
        }

    # ==================== M2: 异常订单 ====================
    def analyze_anomalies(self) -> Dict:
        if self.df_anomaly is None or len(self.df_anomaly) == 0:
            return {'count': 0, 'breakdown': {}, 'examples': []}
        breakdown = {}
        df = self.df_anomaly
        if 'payment' in df.columns:
            breakdown['支付金额小于0'] = int((df['payment'] < 0).sum())
        if 'pay_time' in df.columns and 'order_time' in df.columns:
            breakdown['支付时间早于下单时间'] = int((df['pay_time'] < df['order_time']).sum())
        if 'payment' in df.columns and 'order_amount' in df.columns:
            breakdown['支付金额大于订单金额150%'] = int((df['payment'] > df['order_amount'] * 1.5).sum())
        examples = df.head(20).to_dict('records')
        return {'count': len(df), 'breakdown': breakdown, 'examples': examples}

    # ==================== M3: 核心 KPI ====================
    def analyze_kpi(self) -> Dict:
        df = self.df
        total_sales = df['order_amount'].sum()
        actual_sales = df[df['chargeback'] == 0]['payment'].sum()
        normal_orders = int((df['chargeback'] == 0).sum())
        refund_orders = int((df['chargeback'] == 1).sum())
        refund_rate = refund_orders / len(df) if len(df) > 0 else 0
        aov = actual_sales / normal_orders if normal_orders > 0 else 0
        return {
            'total_sales': round(total_sales, 2),
            'actual_sales': round(actual_sales, 2),
            'normal_orders': normal_orders,
            'refund_orders': refund_orders,
            'refund_rate': round(refund_rate * 100, 2),
            'aov': round(aov, 2),
            'total_orders': len(df),
            'unique_customers': df['user_id'].nunique(),
        }

    # ==================== M4: 月度销售额 ====================
    def analyze_monthly(self) -> Dict:
        df = self.df
        if 'pay_month' not in df.columns:
            return {}
        monthly = df.groupby('pay_month').agg({
            'payment': 'sum',
            'order_id': 'count'
        }).rename(columns={'order_id': 'order_count'})
        monthly['payment'] = monthly['payment'].round(2)
        # 环比增长率
        monthly['mom_growth'] = monthly['payment'].pct_change() * 100
        monthly['mom_growth'] = monthly['mom_growth'].round(2)
        return monthly.reset_index().to_dict('records')

    # ==================== M5: 渠道销售额 ====================
    def analyze_channels(self) -> Dict:
        df = self.df
        if 'channel_id' not in df.columns:
            return {}
        channel_sales = df.groupby('channel_id')['payment'].sum().sort_values(ascending=False)
        total = channel_sales.sum()
        channel_pct = (channel_sales / total * 100).round(2)
        # 帕累托累积
        cumsum = channel_sales.cumsum()
        cumsum_pct = (cumsum / total * 100).round(2)
        return {
            'channels': channel_sales.head(15).to_dict(),
            'percentages': channel_pct.head(15).to_dict(),
            'cumulative': cumsum_pct.head(15).to_dict(),
            'top80_count': int((cumsum_pct <= 80).sum()),
        }

    # ==================== M6: 星期消费模式 ====================
    def analyze_weekday(self) -> Dict:
        df = self.df
        if 'pay_weekday' not in df.columns:
            return {}
        weekday_sales = df.groupby('pay_weekday')['payment'].sum()
        weekday_orders = df.groupby('pay_weekday').size()
        # Kruskal-Wallis 检验：各星期销售额分布是否有显著差异
        groups = [df[df['pay_weekday'] == d]['payment'].values for d in range(7)]
        kw_stat, kw_p = stats.kruskal(*groups)
        return {
            'sales': {WEEKDAY_NAMES[i]: round(weekday_sales.get(i, 0), 2) for i in range(7)},
            'orders': {WEEKDAY_NAMES[i]: int(weekday_orders.get(i, 0)) for i in range(7)},
            'kw_statistic': round(kw_stat, 3),
            'kw_pvalue': round(kw_p, 4),
            'significant': kw_p < 0.05,
        }

    # ==================== M7: 24 小时热力 ====================
    def analyze_hourly(self) -> Dict:
        df = self.df
        if 'pay_hour' not in df.columns:
            return {}
        hourly_sales = df.groupby('pay_hour')['payment'].sum().round(2)
        hourly_orders = df.groupby('pay_hour').size()
        hourly_std = df.groupby('pay_hour')['payment'].std().round(2)
        return {
            'sales': hourly_sales.to_dict(),
            'orders': hourly_orders.to_dict(),
            'std': hourly_std.to_dict(),
            'peak_hour': int(hourly_sales.idxmax()),
            'valley_hour': int(hourly_sales.idxmin()),
        }

    # ==================== M8: 客户价值分层 ====================
    def analyze_customer_value(self) -> Dict:
        df = self.df
        customer_value = df.groupby('user_id')['payment'].sum().sort_values(ascending=False)
        total = customer_value.sum()
        n = len(customer_value)
        top10_count = max(1, int(np.ceil(n * 0.1)))
        bottom10_count = max(1, int(np.ceil(n * 0.1)))
        top10_value = customer_value.head(top10_count).sum()
        bottom10_value = customer_value.tail(bottom10_count).sum()
        top10_pct = top10_value / total * 100 if total > 0 else 0
        bottom10_pct = bottom10_value / total * 100 if total > 0 else 0
        # 洛伦兹曲线数据
        sorted_values = customer_value.sort_values().values
        cumsum = np.cumsum(sorted_values)
        cumsum_pct = cumsum / cumsum[-1] * 100 if cumsum[-1] > 0 else np.zeros_like(cumsum)
        population_pct = np.arange(1, len(sorted_values) + 1) / len(sorted_values) * 100
        gini = self._gini_coefficient(sorted_values)
        return {
            'top10_count': top10_count,
            'top10_value': round(top10_value, 2),
            'top10_pct': round(top10_pct, 2),
            'bottom10_count': bottom10_count,
            'bottom10_value': round(bottom10_value, 2),
            'bottom10_pct': round(bottom10_pct, 2),
            'lorenz_x': population_pct.tolist(),
            'lorenz_y': cumsum_pct.tolist(),
            'gini': round(gini, 4),
        }

    @staticmethod
    def _gini_coefficient(x: np.ndarray) -> float:
        """计算基尼系数"""
        x = np.array(x, dtype=float)
        x = np.sort(x)
        n = len(x)
        cumsum = np.cumsum(x)
        return (2 * np.sum((np.arange(1, n + 1) * x)) / (n * cumsum[-1])) - (n + 1) / n if cumsum[-1] > 0 else 0

    # ==================== M9: 节假日影响（简化 DiD） ====================
    def analyze_holidays(self) -> Dict:
        df = self.df.copy()
        if 'pay_time' not in df.columns:
            return {}
        df['date'] = pd.to_datetime(df['pay_time']).dt.date
        daily_sales = df.groupby('date')['payment'].sum()
        results = []
        for start, end, name in HOLIDAYS_2021:
            holiday_dates = pd.date_range(start, end).date
            # 处理期间销售额
            treatment_sales = daily_sales[daily_sales.index.isin(holiday_dates)].sum()
            treatment_days = len(holiday_dates)
            # 对照组：节前节后各相同长度窗口
            pre_start = start - timedelta(days=treatment_days)
            pre_dates = pd.date_range(pre_start, start - timedelta(days=1)).date
            post_end = end + timedelta(days=treatment_days)
            post_dates = pd.date_range(end + timedelta(days=1), post_end).date
            control_sales = daily_sales[daily_sales.index.isin(np.concatenate([pre_dates, post_dates]))].sum()
            control_days = len(pre_dates) + len(post_dates)
            # 双重差分估计（简化版）
            treatment_avg = treatment_sales / max(treatment_days, 1)
            control_avg = control_sales / max(control_days, 1)
            diff = treatment_avg - control_avg
            results.append({
                'name': name,
                'treatment_avg': round(treatment_avg, 2),
                'control_avg': round(control_avg, 2),
                'diff': round(diff, 2),
                'diff_pct': round(diff / control_avg * 100, 2) if control_avg != 0 else 0,
            })
        return {'holidays': results}

    # ==================== M10: 支付时滞分析 ====================
    def analyze_payment_lag(self) -> Dict:
        df = self.df
        if 'pay_delay_seconds' not in df.columns:
            return {}
        delays = df['pay_delay_seconds'].dropna()
        delays = delays[delays >= 0]
        if len(delays) == 0:
            return {}
        # 分位数
        q25, q50, q75 = delays.quantile([0.25, 0.5, 0.75])
        mean_delay = delays.mean()
        # K-Means 分群（基于支付时滞 + 订单金额）
        sample = df[['pay_delay_seconds', 'order_amount']].dropna()
        sample = sample[sample['pay_delay_seconds'] >= 0]
        clusters = {}
        if len(sample) >= 10:
            scaler = StandardScaler()
            X = scaler.fit_transform(sample.values)
            kmeans = KMeans(n_clusters=min(3, len(sample)), random_state=42, n_init=10)
            sample['cluster'] = kmeans.fit_predict(X)
            for c in sorted(sample['cluster'].unique()):
                sub = sample[sample['cluster'] == c]
                clusters[f'群体{c+1}'] = {
                    'count': len(sub),
                    'avg_delay_sec': round(sub['pay_delay_seconds'].mean(), 1),
                    'avg_amount': round(sub['order_amount'].mean(), 2),
                }
        return {
            'mean_sec': round(mean_delay, 1),
            'median_sec': round(q50, 1),
            'q25_sec': round(q25, 1),
            'q75_sec': round(q75, 1),
            'clusters': clusters,
        }

    # ==================== M11: RFM + CLV ====================
    def analyze_rfm_clv(self) -> Dict:
        df = self.df
        if 'pay_time' not in df.columns:
            return {}
        end_date = df['pay_time'].max()
        rfm = df.groupby('user_id').agg({
            'pay_time': lambda x: (end_date - x.max()).days,
            'order_id': 'count',
            'payment': 'sum'
        }).rename(columns={'pay_time': 'recency', 'order_id': 'frequency', 'payment': 'monetary'})
        if len(rfm) < 10:
            return {}
        # K-Means 聚类
        scaler = StandardScaler()
        X = scaler.fit_transform(rfm[['recency', 'frequency', 'monetary']])
        n_clusters = min(5, len(rfm))
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        rfm['cluster'] = kmeans.fit_predict(X)
        # CLV 估算（简化：历史均值 × 频次 × 关系持续时间）
        rfm['clv'] = rfm['monetary'] * rfm['frequency'] * (365 / (rfm['recency'] + 1))
        cluster_summary = rfm.groupby('cluster').agg({
            'recency': 'mean',
            'frequency': 'mean',
            'monetary': 'mean',
            'clv': 'mean'
        }).round(2).to_dict('index')
        return {
            'cluster_summary': cluster_summary,
            'total_customers': len(rfm),
            'avg_clv': round(rfm['clv'].mean(), 2),
        }

    # ==================== M12: 高阶网络与生存分析 ====================
    def analyze_advanced_network_survival(self) -> Dict:
        df = self.df
        result = {}

        # ---- 12.1 共购网络 + Jaccard + Leiden ----
        if 'user_id' in df.columns and 'goods_id' in df.columns:
            # 构建用户-商品二部图
            B = nx.Graph()
            user_nodes = set(df['user_id'].unique())
            goods_nodes = set(f"g_{g}" for g in df['goods_id'].unique())
            B.add_nodes_from(user_nodes, bipartite=0)
            B.add_nodes_from(goods_nodes, bipartite=1)
            edges = [(row['user_id'], f"g_{row['goods_id']}", {'weight': row['payment']})
                     for _, row in df.iterrows()]
            B.add_edges_from(edges)
            # 投影为用户共购网络
            user_projection = nx.bipartite.weighted_projected_graph(B, user_nodes)
            # Jaccard 相似度作为边权重（采样，避免全量计算过慢）
            user_list = list(user_nodes)[:min(2000, len(user_nodes))]
            user_goods = {u: set(df[df['user_id'] == u]['goods_id'].unique()) for u in user_list}
            G = nx.Graph()
            G.add_nodes_from(user_list)
            for i, u1 in enumerate(user_list):
                for u2 in user_list[i+1: min(i+200, len(user_list))]:
                    s1, s2 = user_goods[u1], user_goods[u2]
                    inter = len(s1 & s2)
                    union = len(s1 | s2)
                    if union > 0 and inter > 0:
                        jaccard = inter / union
                        if jaccard > 0.1:  # 阈值过滤
                            G.add_edge(u1, u2, weight=jaccard)
            # Leiden 算法（networkx 近似：使用 greedy_modularity_communities + 迭代优化）
            communities = list(nx_comm.greedy_modularity_communities(G, weight='weight'))
            modularity = nx_comm.modularity(G, communities, weight='weight') if communities else 0
            # Null Model：Configuration Model 置换检验
            null_modularities = []
            for _ in range(50):
                deg_seq = [d for _, d in G.degree()]
                if len(deg_seq) < 2:
                    break
                try:
                    null_g = nx.configuration_model(deg_seq)
                    null_g = nx.Graph(null_g)  # 去除多重边
                    null_g.remove_edges_from(nx.selfloop_edges(null_g))
                    if null_g.number_of_edges() > 0:
                        null_comm = list(nx_comm.greedy_modularity_communities(null_g))
                        null_mod = nx_comm.modularity(null_g, null_comm) if null_comm else 0
                        null_modularities.append(null_mod)
                except Exception:
                    continue
            null_mean = np.mean(null_modularities) if null_modularities else 0
            null_std = np.std(null_modularities) if null_modularities else 1
            z_score = (modularity - null_mean) / null_std if null_std > 0 else 0
            p_value = 1 - stats.norm.cdf(z_score) if null_std > 0 else 1

            result['network'] = {
                'nodes': G.number_of_nodes(),
                'edges': G.number_of_edges(),
                'communities': len(communities),
                'modularity': round(modularity, 4),
                'null_mean_modularity': round(null_mean, 4),
                'z_score': round(z_score, 3),
                'p_value': round(p_value, 4),
                'significant': p_value < 0.05,
                'top_communities': [len(c) for c in communities[:5]],
            }

        # ---- 12.2 动态网络（季度切片）----
        if 'pay_time' in df.columns:
            df['quarter'] = df['pay_time'].dt.to_period('Q')
            quarterly_modularity = []
            for q, qdf in df.groupby('quarter'):
                if len(qdf) < 50:
                    continue
                users = list(qdf['user_id'].unique())[:500]
                user_goods_q = {u: set(qdf[qdf['user_id'] == u]['goods_id'].unique()) for u in users}
                Gq = nx.Graph()
                Gq.add_nodes_from(users)
                for i, u1 in enumerate(users):
                    for u2 in users[i+1: min(i+100, len(users))]:
                        s1, s2 = user_goods_q[u1], user_goods_q[u2]
                        inter = len(s1 & s2)
                        union = len(s1 | s2)
                        if union > 0 and inter > 0:
                            j = inter / union
                            if j > 0.05:
                                Gq.add_edge(u1, u2, weight=j)
                if Gq.number_of_edges() > 0:
                    try:
                        comm_q = list(nx_comm.greedy_modularity_communities(Gq))
                        mod_q = nx_comm.modularity(Gq, comm_q) if comm_q else 0
                        quarterly_modularity.append({'quarter': str(q), 'modularity': round(mod_q, 4), 'nodes': Gq.number_of_nodes()})
                    except Exception:
                        pass
            result['dynamic_network'] = quarterly_modularity

        # ---- 12.3 生存分析 ----
        if 'pay_time' in df.columns and 'user_id' in df.columns:
            try:
                from lifelines import KaplanMeierFitter, CoxPHFitter
                end_date = df['pay_time'].max()
                churn_window = 90  # 90天无购买视为流失
                customer_events = []
                for uid, udf in df.groupby('user_id'):
                    udf = udf.sort_values('pay_time')
                    purchase_dates = udf['pay_time'].tolist()
                    # 计算相邻购买间隔
                    for i in range(1, len(purchase_dates)):
                        gap = (purchase_dates[i] - purchase_dates[i-1]).days
                        customer_events.append({
                            'duration': gap,
                            'event': 1,  # 复购（未流失）
                            'avg_amount': udf['payment'].mean(),
                            'platform': udf['platform_type'].iloc[0] if 'platform_type' in udf.columns else '其他',
                        })
                    # 最后一次购买到观测期末的间隔
                    last_to_end = (end_date - purchase_dates[-1]).days
                    event_flag = 1 if last_to_end <= churn_window else 0
                    customer_events.append({
                        'duration': max(1, last_to_end),
                        'event': event_flag,
                        'avg_amount': udf['payment'].mean(),
                        'platform': udf['platform_type'].iloc[0] if 'platform_type' in udf.columns else '其他',
                    })
                surv_df = pd.DataFrame(customer_events)
                if len(surv_df) > 20:
                    kmf = KaplanMeierFitter()
                    kmf.fit(surv_df['duration'], event_observed=surv_df['event'])
                    timeline = kmf.timeline.tolist()
                    survival_prob = kmf.survival_function_['KM_estimate'].values.tolist()
                    ci_lower = kmf.confidence_interval_['KM_estimate_lower_0.95'].values.tolist()
                    ci_upper = kmf.confidence_interval_['KM_estimate_upper_0.95'].values.tolist()
                    result['survival'] = {
                        'timeline': timeline,
                        'survival_prob': survival_prob,
                        'ci_lower': ci_lower,
                        'ci_upper': ci_upper,
                        'median_survival': round(kmf.median_survival_time_, 1) if hasattr(kmf, 'median_survival_time_') else None,
                    }
                    # Cox 回归（简化版）
                    if surv_df['platform'].nunique() > 1:
                        cox_df = surv_df.copy()
                        # 平台 dummy
                        platform_dummies = pd.get_dummies(cox_df['platform'], prefix='platform', drop_first=True)
                        cox_df = pd.concat([cox_df, platform_dummies], axis=1)
                        cox_cols = ['duration', 'event', 'avg_amount'] + [c for c in cox_df.columns if c.startswith('platform_')]
                        cox_df = cox_df[cox_cols].dropna()
                        if len(cox_df) > 30:
                            cph = CoxPHFitter(penalizer=0.1)
                            try:
                                cph.fit(cox_df, duration_col='duration', event_col='event')
                                hr = cph.summary['exp(coef)'].to_dict()
                                hr_p = cph.summary['p'].to_dict()
                                result['cox'] = {
                                    'hazard_ratios': {k: round(v, 3) for k, v in hr.items()},
                                    'p_values': {k: round(v, 4) for k, v in hr_p.items()},
                                }
                            except Exception:
                                pass
            except ImportError:
                result['survival'] = {'error': 'lifelines 库未安装'}

        # ---- 12.4 Markov 状态空间 ----
        if 'user_id' in df.columns and 'pay_time' in df.columns:
            states = ['新客', '活跃', '沉睡', '流失']
            transition_counts = pd.DataFrame(0, index=states, columns=states)
            for uid, udf in df.groupby('user_id'):
                udf = udf.sort_values('pay_time')
                purchase_dates = udf['pay_time'].tolist()
                gaps = [(purchase_dates[i] - purchase_dates[i-1]).days for i in range(1, len(purchase_dates))]
                # 简化状态定义
                prev_state = '新客'
                for gap in gaps:
                    if gap <= 7:
                        curr_state = '活跃'
                    elif gap <= 30:
                        curr_state = '活跃'
                    elif gap <= 90:
                        curr_state = '沉睡'
                    else:
                        curr_state = '流失'
                    transition_counts.loc[prev_state, curr_state] += 1
                    prev_state = curr_state
                # 最后一段到观测期末
                last_gap = (end_date - purchase_dates[-1]).days
                if last_gap <= 7:
                    curr_state = '活跃'
                elif last_gap <= 30:
                    curr_state = '活跃'
                elif last_gap <= 90:
                    curr_state = '沉睡'
                else:
                    curr_state = '流失'
                transition_counts.loc[prev_state, curr_state] += 1
            # 归一化为转移概率
            transition_matrix = transition_counts.div(transition_counts.sum(axis=1), axis=0).fillna(0)
            result['markov'] = {
                'states': states,
                'transition_counts': transition_counts.to_dict(),
                'transition_matrix': {idx: row.to_dict() for idx, row in transition_matrix.iterrows()},
            }

        return result

    # ==================== 一键运行全部 ====================
    def run_all(self) -> Dict[str, Any]:
        self.results = {
            'M1_platforms': self.analyze_platforms(),
            'M2_anomalies': self.analyze_anomalies(),
            'M3_kpi': self.analyze_kpi(),
            'M4_monthly': self.analyze_monthly(),
            'M5_channels': self.analyze_channels(),
            'M6_weekday': self.analyze_weekday(),
            'M7_hourly': self.analyze_hourly(),
            'M8_customer_value': self.analyze_customer_value(),
            'M9_holidays': self.analyze_holidays(),
            'M10_payment_lag': self.analyze_payment_lag(),
            'M11_rfm_clv': self.analyze_rfm_clv(),
            'M12_advanced': self.analyze_advanced_network_survival(),
        }
        return self.results
