"""
实时相关性矩阵组件
提供资产间相关性分析，帮助识别套利机会和风险管理
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import random
from typing import Dict, List, Tuple, Optional


class CorrelationMatrix:
    """相关性矩阵分析类"""

    def __init__(self):
        self.major_assets = [
            "BTC", "ETH", "BNB", "XRP", "ADA", "SOL", "DOGE", "DOT",
            "MATIC", "AVAX", "LTC", "UNI", "LINK", "ATOM"
        ]
        self.timeframes = {
            "1小时": 1,
            "4小时": 4,
            "24小时": 24,
            "7天": 168,
            "30天": 720
        }

    def generate_price_data(self, hours: int = 24) -> pd.DataFrame:
        """生成模拟价格数据"""
        # 生成时间序列
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        time_points = pd.date_range(start=start_time, end=end_time, freq='H')

        # 生成价格数据
        data = {}

        # BTC作为基准
        btc_base = 45000
        btc_volatility = 0.02
        btc_prices = [btc_base]

        for i in range(1, len(time_points)):
            change = np.random.normal(0, btc_volatility)
            new_price = btc_prices[-1] * (1 + change)
            btc_prices.append(new_price)

        data['BTC'] = btc_prices

        # 其他资产相对于BTC的相关性
        correlations = {
            'ETH': 0.85,    # 高相关性
            'BNB': 0.75,    # 较高相关性
            'XRP': 0.65,    # 中等相关性
            'ADA': 0.70,    # 中等相关性
            'SOL': 0.80,    # 高相关性
            'DOGE': 0.60,   # 中等相关性
            'DOT': 0.75,    # 较高相关性
            'MATIC': 0.70,  # 中等相关性
            'AVAX': 0.78,   # 较高相关性
            'LTC': 0.82,    # 高相关性
            'UNI': 0.72,    # 较高相关性
            'LINK': 0.68,   # 中等相关性
            'ATOM': 0.65    # 中等相关性
        }

        for asset in self.major_assets[1:]:  # 跳过BTC
            correlation = correlations.get(asset, 0.7)
            asset_volatility = btc_volatility * random.uniform(0.8, 1.5)

            asset_prices = []
            base_price = random.uniform(0.1, 3000)
            asset_prices.append(base_price)

            for i in range(1, len(time_points)):
                # 相关性影响
                btc_change = (btc_prices[i] - btc_prices[i-1]) / btc_prices[i-1]
                correlated_change = btc_change * correlation

                # 独立随机变化
                independent_change = np.random.normal(0, asset_volatility * (1 - correlation))

                total_change = correlated_change + independent_change
                new_price = asset_prices[-1] * (1 + total_change)
                asset_prices.append(new_price)

            data[asset] = asset_prices

        # 创建DataFrame
        df = pd.DataFrame(data, index=time_points)
        return df

    def calculate_correlation_matrix(self, price_data: pd.DataFrame) -> pd.DataFrame:
        """计算相关性矩阵"""
        # 计算收益率
        returns = price_data.pct_change().dropna()

        # 计算相关性矩阵
        correlation_matrix = returns.corr()

        return correlation_matrix

    def render_correlation_heatmap(self, correlation_matrix: pd.DataFrame, timeframe: str):
        """渲染相关性热力图"""
        st.subheader(f"🔥 实时相关性矩阵热力图 ({timeframe})")

        # 创建热力图
        fig = go.Figure(data=go.Heatmap(
            z=correlation_matrix.values,
            x=correlation_matrix.columns,
            y=correlation_matrix.index,
            colorscale=[
                [0, '#d73027'],      # 负相关 - 红色
                [0.25, '#f46d43'],   # 弱负相关 - 橙红
                [0.5, '#ffffff'],    # 无相关 - 白色
                [0.75, '#74add1'],   # 弱正相关 - 浅蓝
                [1, '#313695']       # 强正相关 - 深蓝
            ],
            zmid=0,
            zmin=-1,
            zmax=1,
            text=np.round(correlation_matrix.values, 2),
            texttemplate="%{text}",
            textfont={"size": 10},
            hoverongaps=False,
            hovertemplate='<b>%{x} vs %{y}</b><br>' +
                         '相关性: %{z:.3f}<br>' +
                         '<extra></extra>'
        ))

        fig.update_layout(
            title=f"资产相关性矩阵 - {timeframe}",
            xaxis_title="资产",
            yaxis_title="资产",
            height=600,
            width=800
        )

        st.plotly_chart(fig, use_container_width=True)

    def render_correlation_insights(self, correlation_matrix: pd.DataFrame):
        """渲染相关性洞察"""
        st.subheader("💡 相关性分析洞察")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**🔗 高相关性资产对 (>0.8)**")
            high_corr_pairs = []

            for i in range(len(correlation_matrix.columns)):
                for j in range(i+1, len(correlation_matrix.columns)):
                    asset1 = correlation_matrix.columns[i]
                    asset2 = correlation_matrix.columns[j]
                    corr_value = correlation_matrix.iloc[i, j]

                    if corr_value > 0.8:
                        high_corr_pairs.append({
                            "资产对": f"{asset1} - {asset2}",
                            "相关性": f"{corr_value:.3f}",
                            "套利风险": "🔴 高" if corr_value > 0.9 else "🟡 中"
                        })

            if high_corr_pairs:
                df_high = pd.DataFrame(high_corr_pairs)
                st.dataframe(df_high, hide_index=True, use_container_width=True)
            else:
                st.info("当前时间段内无高相关性资产对")

        with col2:
            st.markdown("**🔄 低相关性资产对 (<0.3)**")
            low_corr_pairs = []

            for i in range(len(correlation_matrix.columns)):
                for j in range(i+1, len(correlation_matrix.columns)):
                    asset1 = correlation_matrix.columns[i]
                    asset2 = correlation_matrix.columns[j]
                    corr_value = correlation_matrix.iloc[i, j]

                    if corr_value < 0.3:
                        low_corr_pairs.append({
                            "资产对": f"{asset1} - {asset2}",
                            "相关性": f"{corr_value:.3f}",
                            "套利机会": "🟢 高" if corr_value < 0.1 else "🟡 中"
                        })

            if low_corr_pairs:
                df_low = pd.DataFrame(low_corr_pairs)
                st.dataframe(df_low, hide_index=True, use_container_width=True)
            else:
                st.info("当前时间段内无低相关性资产对")

    def render_correlation_trends(self, timeframes_data: Dict[str, pd.DataFrame]):
        """渲染相关性趋势分析"""
        st.subheader("📈 相关性趋势分析")

        # 选择要分析的资产对
        asset_pairs = st.multiselect(
            "选择资产对进行趋势分析",
            options=[
                "BTC-ETH", "BTC-BNB", "ETH-BNB", "BTC-SOL", "ETH-SOL",
                "BTC-ADA", "ETH-ADA", "BNB-SOL", "SOL-ADA", "BTC-DOGE"
            ],
            default=["BTC-ETH", "BTC-BNB", "ETH-BNB"],
            key="correlation_trends"
        )

        if asset_pairs:
            # 创建趋势图
            fig = go.Figure()

            timeframe_labels = list(timeframes_data.keys())

            for pair in asset_pairs:
                asset1, asset2 = pair.split('-')
                correlations = []

                for timeframe in timeframe_labels:
                    corr_matrix = timeframes_data[timeframe]
                    if asset1 in corr_matrix.columns and asset2 in corr_matrix.columns:
                        corr_value = corr_matrix.loc[asset1, asset2]
                        correlations.append(corr_value)
                    else:
                        correlations.append(0)

                fig.add_trace(go.Scatter(
                    x=timeframe_labels,
                    y=correlations,
                    mode='lines+markers',
                    name=pair,
                    line=dict(width=3),
                    marker=dict(size=8)
                ))

            fig.update_layout(
                title="不同时间框架下的相关性变化",
                xaxis_title="时间框架",
                yaxis_title="相关性系数",
                height=400,
                hovermode='x unified'
            )

            fig.add_hline(y=0.8, line_dash="dash", line_color="red",
                         annotation_text="高相关性阈值 (0.8)")
            fig.add_hline(y=0.3, line_dash="dash", line_color="green",
                         annotation_text="低相关性阈值 (0.3)")

            st.plotly_chart(fig, use_container_width=True)

    def render_arbitrage_opportunities(self, correlation_matrix: pd.DataFrame):
        """基于相关性分析渲染套利机会"""
        st.subheader("🎯 基于相关性的套利机会")

        opportunities = []

        for i in range(len(correlation_matrix.columns)):
            for j in range(i+1, len(correlation_matrix.columns)):
                asset1 = correlation_matrix.columns[i]
                asset2 = correlation_matrix.columns[j]
                corr_value = correlation_matrix.iloc[i, j]

                # 低相关性表示潜在的套利机会
                if corr_value < 0.5:
                    # 模拟价格差异
                    price_diff = random.uniform(0.5, 3.0)

                    # 计算机会评分
                    opportunity_score = (1 - corr_value) * price_diff * 10

                    # 风险评估
                    if corr_value < 0.2:
                        risk_level = "🟢 低风险"
                    elif corr_value < 0.4:
                        risk_level = "🟡 中风险"
                    else:
                        risk_level = "🔴 高风险"

                    opportunities.append({
                        "资产对": f"{asset1}/{asset2}",
                        "相关性": f"{corr_value:.3f}",
                        "价格差异": f"{price_diff:.2f}%",
                        "机会评分": f"{opportunity_score:.1f}",
                        "风险等级": risk_level,
                        "建议": "考虑套利" if opportunity_score > 15 else "观察"
                    })

        if opportunities:
            # 按机会评分排序
            opportunities.sort(key=lambda x: float(x["机会评分"]), reverse=True)

            df_opportunities = pd.DataFrame(opportunities[:10])  # 显示前10个机会
            st.dataframe(
                df_opportunities,
                hide_index=True,
                use_container_width=True,
                column_config={
                    "机会评分": st.column_config.ProgressColumn(
                        "机会评分",
                        help="基于相关性和价格差异的综合评分",
                        min_value=0,
                        max_value=30,
                    ),
                }
            )
        else:
            st.info("当前市场条件下暂无明显套利机会")


def render_correlation_matrix_dashboard():
    """渲染相关性矩阵仪表板"""
    st.subheader("🔗 实时相关性矩阵分析")

    # 时间框架选择
    col1, col2 = st.columns([1, 3])

    with col1:
        selected_timeframe = st.selectbox(
            "选择时间框架",
            options=list(CorrelationMatrix().timeframes.keys()),
            index=2,  # 默认24小时
            key="correlation_timeframe"
        )

    with col2:
        auto_refresh = st.checkbox("自动刷新 (30秒)", value=False, key="correlation_auto_refresh")
        if auto_refresh:
            # 使用session state控制刷新间隔，避免无限循环
            if 'correlation_last_refresh' not in st.session_state:
                st.session_state.correlation_last_refresh = datetime.now()
            
            time_since_refresh = (datetime.now() - st.session_state.correlation_last_refresh).total_seconds()
            if time_since_refresh >= 30:
                st.session_state.correlation_last_refresh = datetime.now()
                st.rerun()

    # 创建相关性矩阵实例
    correlation_analyzer = CorrelationMatrix()

    # 生成不同时间框架的数据
    timeframes_data = {}

    for timeframe, hours in correlation_analyzer.timeframes.items():
        price_data = correlation_analyzer.generate_price_data(hours)
        correlation_matrix = correlation_analyzer.calculate_correlation_matrix(price_data)
        timeframes_data[timeframe] = correlation_matrix

    # 获取当前选择的时间框架数据
    current_correlation_matrix = timeframes_data[selected_timeframe]

    # 渲染热力图
    correlation_analyzer.render_correlation_heatmap(current_correlation_matrix, selected_timeframe)

    st.divider()

    # 渲染相关性洞察
    correlation_analyzer.render_correlation_insights(current_correlation_matrix)

    st.divider()

    # 渲染趋势分析
    correlation_analyzer.render_correlation_trends(timeframes_data)

    st.divider()

    # 渲染套利机会
    correlation_analyzer.render_arbitrage_opportunities(current_correlation_matrix)
