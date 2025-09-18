"""
市场健康仪表板组件
提供专业的市场健康状况快照，包括价格、成交量、波动率和订单簿深度分析
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import random
from typing import Dict, List, Tuple, Optional


class MarketHealthDashboard:
    """市场健康仪表板类"""

    def __init__(self):
        self.top_pairs = [
            "BTC/USDT", "ETH/USDT", "BNB/USDT", "XRP/USDT", "ADA/USDT",
            "SOL/USDT", "DOGE/USDT", "DOT/USDT", "MATIC/USDT", "AVAX/USDT"
        ]
        self.exchanges = ["Binance", "OKX", "Huobi", "KuCoin", "Gate.io", "Bybit"]

    def generate_market_health_data(self) -> Dict:
        """生成市场健康数据"""
        data = {}

        for pair in self.top_pairs:
            base_price = random.uniform(0.1, 50000)

            # 24小时数据
            volume_24h = random.uniform(10000000, 1000000000)  # 1千万到10亿
            price_change_24h = random.uniform(-15, 15)
            high_24h = base_price * (1 + abs(price_change_24h)/100 + random.uniform(0, 0.05))
            low_24h = base_price * (1 - abs(price_change_24h)/100 - random.uniform(0, 0.05))

            # 波动率计算
            volatility = abs(price_change_24h) + random.uniform(0, 5)

            # 订单簿深度 (模拟)
            bid_depth = random.uniform(50000, 500000)
            ask_depth = random.uniform(50000, 500000)
            spread = random.uniform(0.01, 0.5)

            # 流动性评分
            liquidity_score = min(100, (volume_24h / 1000000) * 0.1 + (bid_depth + ask_depth) / 10000)

            # 市场健康评分
            health_score = self._calculate_health_score(
                volatility, liquidity_score, spread, volume_24h
            )

            data[pair] = {
                'price': base_price,
                'price_change_24h': price_change_24h,
                'volume_24h': volume_24h,
                'high_24h': high_24h,
                'low_24h': low_24h,
                'volatility': volatility,
                'bid_depth': bid_depth,
                'ask_depth': ask_depth,
                'spread': spread,
                'liquidity_score': liquidity_score,
                'health_score': health_score
            }

        return data

    def _calculate_health_score(self, volatility: float, liquidity: float,
                               spread: float, volume: float) -> float:
        """计算市场健康评分"""
        # 波动率评分 (波动率越低越好)
        volatility_score = max(0, 100 - volatility * 2)

        # 流动性评分
        liquidity_score = min(100, liquidity)

        # 价差评分 (价差越小越好)
        spread_score = max(0, 100 - spread * 50)

        # 成交量评分
        volume_score = min(100, volume / 10000000)

        # 综合评分
        health_score = (volatility_score * 0.3 + liquidity_score * 0.3 +
                       spread_score * 0.2 + volume_score * 0.2)

        return round(health_score, 1)

    def render_market_overview_cards(self, market_data: Dict):
        """渲染市场概览卡片"""
        st.subheader("🏥 市场健康快照")

        # 计算总体市场指标
        total_volume = sum(data['volume_24h'] for data in market_data.values())
        avg_volatility = np.mean([data['volatility'] for data in market_data.values()])
        avg_health_score = np.mean([data['health_score'] for data in market_data.values()])

        # 显示总体指标
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "总成交量 (24h)",
                f"${total_volume/1e9:.2f}B",
                delta=f"{random.uniform(-5, 15):.1f}%"
            )

        with col2:
            st.metric(
                "平均波动率",
                f"{avg_volatility:.1f}%",
                delta=f"{random.uniform(-2, 2):.1f}%"
            )

        with col3:
            health_color = "🟢" if avg_health_score >= 70 else "🟡" if avg_health_score >= 50 else "🔴"
            st.metric(
                "市场健康度",
                f"{health_color} {avg_health_score:.1f}",
                delta=f"{random.uniform(-5, 5):.1f}"
            )

        with col4:
            active_pairs = len([p for p in market_data.values() if p['health_score'] >= 60])
            st.metric(
                "活跃交易对",
                f"{active_pairs}/{len(market_data)}",
                delta=f"{random.randint(-2, 3)}"
            )

    def render_top_pairs_table(self, market_data: Dict):
        """渲染顶级交易对表格"""
        st.subheader("📊 顶级交易对详情")

        # 准备表格数据
        table_data = []
        for pair, data in market_data.items():
            # 健康状态图标
            if data['health_score'] >= 70:
                health_icon = "🟢"
            elif data['health_score'] >= 50:
                health_icon = "🟡"
            else:
                health_icon = "🔴"

            # 价格变化图标
            change_icon = "📈" if data['price_change_24h'] >= 0 else "📉"

            table_data.append({
                "交易对": pair,
                "价格": f"${data['price']:.4f}",
                "24h变化": f"{change_icon} {data['price_change_24h']:+.2f}%",
                "24h成交量": f"${data['volume_24h']/1e6:.1f}M",
                "波动率": f"{data['volatility']:.1f}%",
                "买卖价差": f"{data['spread']:.3f}%",
                "流动性": f"{data['liquidity_score']:.1f}",
                "健康度": f"{health_icon} {data['health_score']:.1f}"
            })

        # 显示表格
        df = pd.DataFrame(table_data)
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "交易对": st.column_config.TextColumn("交易对", width="small"),
                "价格": st.column_config.TextColumn("价格", width="small"),
                "24h变化": st.column_config.TextColumn("24h变化", width="small"),
                "24h成交量": st.column_config.TextColumn("24h成交量", width="medium"),
                "波动率": st.column_config.TextColumn("波动率", width="small"),
                "买卖价差": st.column_config.TextColumn("买卖价差", width="small"),
                "流动性": st.column_config.TextColumn("流动性", width="small"),
                "健康度": st.column_config.TextColumn("健康度", width="small")
            }
        )

    def render_market_health_charts(self, market_data: Dict):
        """渲染市场健康图表"""
        st.subheader("📈 市场健康分析图表")

        col1, col2 = st.columns(2)

        with col1:
            # 健康度分布饼图
            health_ranges = {"优秀 (70+)": 0, "良好 (50-70)": 0, "一般 (<50)": 0}

            for data in market_data.values():
                if data['health_score'] >= 70:
                    health_ranges["优秀 (70+)"] += 1
                elif data['health_score'] >= 50:
                    health_ranges["良好 (50-70)"] += 1
                else:
                    health_ranges["一般 (<50)"] += 1

            fig_pie = go.Figure(data=[go.Pie(
                labels=list(health_ranges.keys()),
                values=list(health_ranges.values()),
                hole=0.4,
                marker_colors=['#00ff00', '#ffff00', '#ff0000']
            )])

            fig_pie.update_layout(
                title="市场健康度分布",
                height=300,
                showlegend=True
            )

            st.plotly_chart(fig_pie, use_container_width=True)

        with col2:
            # 波动率 vs 流动性散点图
            pairs = list(market_data.keys())
            volatilities = [market_data[pair]['volatility'] for pair in pairs]
            liquidities = [market_data[pair]['liquidity_score'] for pair in pairs]
            health_scores = [market_data[pair]['health_score'] for pair in pairs]

            fig_scatter = go.Figure(data=go.Scatter(
                x=volatilities,
                y=liquidities,
                mode='markers',
                marker=dict(
                    size=[score/5 for score in health_scores],
                    color=health_scores,
                    colorscale='RdYlGn',
                    showscale=True,
                    colorbar=dict(title="健康度")
                ),
                text=pairs,
                hovertemplate='<b>%{text}</b><br>' +
                             '波动率: %{x:.1f}%<br>' +
                             '流动性: %{y:.1f}<br>' +
                             '<extra></extra>'
            ))

            fig_scatter.update_layout(
                title="波动率 vs 流动性分析",
                xaxis_title="波动率 (%)",
                yaxis_title="流动性评分",
                height=300
            )

            st.plotly_chart(fig_scatter, use_container_width=True)

    def render_orderbook_depth_analysis(self, market_data: Dict):
        """渲染订单簿深度分析"""
        st.subheader("📚 订单簿深度分析")

        # 选择要分析的交易对
        selected_pairs = st.multiselect(
            "选择交易对进行深度分析",
            options=list(market_data.keys()),
            default=list(market_data.keys())[:5],
            key="orderbook_pairs"
        )

        if selected_pairs:
            # 创建订单簿深度对比图
            fig = make_subplots(
                rows=1, cols=2,
                subplot_titles=('买单深度', '卖单深度'),
                specs=[[{"secondary_y": False}, {"secondary_y": False}]]
            )

            pairs = selected_pairs
            bid_depths = [market_data[pair]['bid_depth'] for pair in pairs]
            ask_depths = [market_data[pair]['ask_depth'] for pair in pairs]

            # 买单深度
            fig.add_trace(
                go.Bar(
                    x=pairs,
                    y=bid_depths,
                    name="买单深度",
                    marker_color='green',
                    opacity=0.7
                ),
                row=1, col=1
            )

            # 卖单深度
            fig.add_trace(
                go.Bar(
                    x=pairs,
                    y=ask_depths,
                    name="卖单深度",
                    marker_color='red',
                    opacity=0.7
                ),
                row=1, col=2
            )

            fig.update_layout(
                height=400,
                showlegend=False,
                title_text="订单簿深度对比"
            )

            fig.update_xaxes(tickangle=45)
            fig.update_yaxes(title_text="深度 (USDT)", row=1, col=1)
            fig.update_yaxes(title_text="深度 (USDT)", row=1, col=2)

            st.plotly_chart(fig, use_container_width=True)

    def render_market_alerts(self, market_data: Dict):
        """渲染市场警报"""
        st.subheader("⚠️ 市场警报")

        alerts = []

        for pair, data in market_data.items():
            # 高波动率警报
            if data['volatility'] > 10:
                alerts.append({
                    "级别": "🔴 高",
                    "类型": "高波动率",
                    "交易对": pair,
                    "详情": f"波动率达到 {data['volatility']:.1f}%",
                    "建议": "谨慎交易，注意风险控制"
                })

            # 低流动性警报
            if data['liquidity_score'] < 30:
                alerts.append({
                    "级别": "🟡 中",
                    "类型": "低流动性",
                    "交易对": pair,
                    "详情": f"流动性评分仅 {data['liquidity_score']:.1f}",
                    "建议": "可能存在滑点风险"
                })

            # 大价差警报
            if data['spread'] > 0.3:
                alerts.append({
                    "级别": "🟡 中",
                    "类型": "大价差",
                    "交易对": pair,
                    "详情": f"买卖价差 {data['spread']:.3f}%",
                    "建议": "交易成本较高"
                })

        if alerts:
            df_alerts = pd.DataFrame(alerts)
            st.dataframe(
                df_alerts,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.success("✅ 当前市场状况良好，无重要警报")


def render_market_health_dashboard():
    """渲染市场健康仪表板"""
    dashboard = MarketHealthDashboard()

    # 生成市场数据
    market_data = dashboard.generate_market_health_data()

    # 渲染各个组件
    dashboard.render_market_overview_cards(market_data)

    st.divider()

    dashboard.render_top_pairs_table(market_data)

    st.divider()

    dashboard.render_market_health_charts(market_data)

    st.divider()

    dashboard.render_orderbook_depth_analysis(market_data)

    st.divider()

    dashboard.render_market_alerts(market_data)
