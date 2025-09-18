"""
历史套利机会追踪器组件
提供历史套利机会的跟踪、分析和模式识别功能
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import random


class HistoricalArbitrageTracker:
    """历史套利机会追踪器"""

    def __init__(self):
        self.exchanges = ["Binance", "OKX", "Huobi", "KuCoin", "Gate.io", "Bybit"]
        self.currencies = ["BTC", "ETH", "BNB", "ADA", "DOT", "LINK", "UNI", "MATIC"]

    def generate_historical_data(self, days=30):
        """生成历史套利机会数据"""
        data = []

        for day in range(days):
            date = datetime.now() - timedelta(days=day)

            # 每天生成5-15个套利机会
            daily_opportunities = random.randint(5, 15)

            for _ in range(daily_opportunities):
                currency = random.choice(self.currencies)
                buy_exchange = random.choice(self.exchanges)
                sell_exchange = random.choice([ex for ex in self.exchanges if ex != buy_exchange])

                # 生成套利数据
                price_diff = random.uniform(0.1, 3.5)
                profit_potential = random.uniform(50, 2000)
                duration = random.randint(30, 1800)  # 30秒到30分钟
                success_rate = random.uniform(60, 95)

                # 执行状态
                status = random.choices(
                    ["executed", "missed", "expired", "cancelled"],
                    weights=[0.4, 0.3, 0.2, 0.1]
                )[0]

                # 实际利润（如果执行）
                actual_profit = 0
                if status == "executed":
                    # 实际利润通常低于预期
                    actual_profit = profit_potential * random.uniform(0.7, 0.95)

                data.append({
                    "timestamp": date,
                    "currency": currency,
                    "buy_exchange": buy_exchange,
                    "sell_exchange": sell_exchange,
                    "price_difference": price_diff,
                    "profit_potential": profit_potential,
                    "actual_profit": actual_profit,
                    "duration_seconds": duration,
                    "success_rate": success_rate,
                    "status": status,
                    "volume": random.uniform(1000, 50000)
                })

        return pd.DataFrame(data)

    def render_overview_metrics(self, df):
        """渲染概览指标"""
        col1, col2, col3, col4 = st.columns(4)

        total_opportunities = len(df)
        executed_opportunities = len(df[df["status"] == "executed"])
        total_profit = df[df["status"] == "executed"]["actual_profit"].sum()
        avg_success_rate = df["success_rate"].mean()

        with col1:
            st.metric(
                "总机会数",
                f"{total_opportunities:,}",
                delta=f"+{random.randint(5, 20)} (今日)"
            )

        with col2:
            execution_rate = (executed_opportunities / total_opportunities * 100) if total_opportunities > 0 else 0
            st.metric(
                "执行率",
                f"{execution_rate:.1f}%",
                delta=f"{random.uniform(-2, 5):.1f}%"
            )

        with col3:
            st.metric(
                "累计利润",
                f"${total_profit:,.0f}",
                delta=f"+${random.uniform(100, 500):.0f} (今日)"
            )

        with col4:
            st.metric(
                "平均成功率",
                f"{avg_success_rate:.1f}%",
                delta=f"{random.uniform(-1, 3):.1f}%"
            )

    def render_profit_timeline(self, df):
        """渲染利润时间线图表"""
        st.subheader("📈 利润时间线")

        # 按日期聚合利润
        daily_profit = df[df["status"] == "executed"].groupby(
            df["timestamp"].dt.date
        )["actual_profit"].sum().reset_index()
        daily_profit["cumulative_profit"] = daily_profit["actual_profit"].cumsum()

        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=["每日利润", "累计利润"],
            vertical_spacing=0.1
        )

        # 每日利润柱状图
        fig.add_trace(
            go.Bar(
                x=daily_profit["timestamp"],
                y=daily_profit["actual_profit"],
                name="每日利润",
                marker_color="lightblue"
            ),
            row=1, col=1
        )

        # 累计利润线图
        fig.add_trace(
            go.Scatter(
                x=daily_profit["timestamp"],
                y=daily_profit["cumulative_profit"],
                mode="lines+markers",
                name="累计利润",
                line=dict(color="green", width=3)
            ),
            row=2, col=1
        )

        fig.update_layout(
            height=500,
            showlegend=False,
            title_text="利润分析"
        )

        st.plotly_chart(fig, use_container_width=True)

    def render_opportunity_patterns(self, df):
        """渲染机会模式分析"""
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🏆 最佳交易对")

            # 按货币统计
            currency_stats = df.groupby("currency").agg({
                "profit_potential": "sum",
                "actual_profit": "sum",
                "status": lambda x: (x == "executed").sum()
            }).round(2)
            currency_stats.columns = ["潜在利润", "实际利润", "执行次数"]
            currency_stats = currency_stats.sort_values("实际利润", ascending=False)

            st.dataframe(currency_stats, use_container_width=True)

        with col2:
            st.subheader("🏢 交易所表现")

            # 统计各交易所作为买入方的表现
            exchange_stats = []
            for exchange in self.exchanges:
                buy_ops = df[df["buy_exchange"] == exchange]
                sell_ops = df[df["sell_exchange"] == exchange]

                total_ops = len(buy_ops) + len(sell_ops)
                total_profit = (buy_ops[buy_ops["status"] == "executed"]["actual_profit"].sum() +
                              sell_ops[sell_ops["status"] == "executed"]["actual_profit"].sum())

                exchange_stats.append({
                    "交易所": exchange,
                    "参与次数": total_ops,
                    "总利润": total_profit
                })

            exchange_df = pd.DataFrame(exchange_stats).sort_values("总利润", ascending=False)
            st.dataframe(exchange_df, use_container_width=True)

    def render_duration_analysis(self, df):
        """渲染持续时间分析"""
        st.subheader("⏱️ 机会持续时间分析")

        # 创建持续时间分布图
        fig = px.histogram(
            df,
            x="duration_seconds",
            nbins=20,
            title="套利机会持续时间分布",
            labels={"duration_seconds": "持续时间 (秒)", "count": "频次"}
        )

        fig.update_layout(
            xaxis_title="持续时间 (秒)",
            yaxis_title="机会数量"
        )

        st.plotly_chart(fig, use_container_width=True)

        # 持续时间统计
        col1, col2, col3 = st.columns(3)

        with col1:
            avg_duration = df["duration_seconds"].mean()
            st.metric("平均持续时间", f"{avg_duration:.0f}秒")

        with col2:
            median_duration = df["duration_seconds"].median()
            st.metric("中位持续时间", f"{median_duration:.0f}秒")

        with col3:
            max_duration = df["duration_seconds"].max()
            st.metric("最长持续时间", f"{max_duration:.0f}秒")

    def render_success_factors(self, df):
        """渲染成功因素分析"""
        st.subheader("🎯 成功因素分析")

        col1, col2 = st.columns(2)

        with col1:
            # 价格差与执行成功率的关系
            df["price_range"] = pd.cut(df["price_difference"], bins=5, labels=[
                "0-0.7%", "0.7-1.4%", "1.4-2.1%", "2.1-2.8%", "2.8%+"
            ])

            success_by_price = df.groupby("price_range").apply(
                lambda x: (x["status"] == "executed").sum() / len(x) * 100
            ).reset_index()
            success_by_price.columns = ["价格差范围", "执行成功率"]

            fig = px.bar(
                success_by_price,
                x="价格差范围",
                y="执行成功率",
                title="价格差与执行成功率关系"
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # 持续时间与执行成功率的关系
            df["duration_range"] = pd.cut(df["duration_seconds"], bins=5, labels=[
                "0-360s", "360-720s", "720-1080s", "1080-1440s", "1440s+"
            ])

            success_by_duration = df.groupby("duration_range").apply(
                lambda x: (x["status"] == "executed").sum() / len(x) * 100
            ).reset_index()
            success_by_duration.columns = ["持续时间范围", "执行成功率"]

            fig = px.bar(
                success_by_duration,
                x="持续时间范围",
                y="执行成功率",
                title="持续时间与执行成功率关系"
            )
            st.plotly_chart(fig, use_container_width=True)

    def render_detailed_history(self, df):
        """渲染详细历史记录"""
        st.subheader("📋 详细历史记录")

        # 筛选选项
        col1, col2, col3 = st.columns(3)

        with col1:
            status_filter = st.selectbox(
                "状态筛选",
                ["全部"] + df["status"].unique().tolist()
            )

        with col2:
            currency_filter = st.selectbox(
                "货币筛选",
                ["全部"] + sorted(df["currency"].unique().tolist())
            )

        with col3:
            days_filter = st.selectbox(
                "时间范围",
                [7, 14, 30],
                index=2
            )

        # 应用筛选
        filtered_df = df.copy()

        if status_filter != "全部":
            filtered_df = filtered_df[filtered_df["status"] == status_filter]

        if currency_filter != "全部":
            filtered_df = filtered_df[filtered_df["currency"] == currency_filter]

        cutoff_date = datetime.now() - timedelta(days=days_filter)
        filtered_df = filtered_df[filtered_df["timestamp"] >= cutoff_date]

        # 格式化显示数据
        display_df = filtered_df.copy()
        display_df["时间"] = display_df["timestamp"].dt.strftime("%Y-%m-%d %H:%M")
        display_df["交易对"] = display_df["currency"]
        display_df["买入交易所"] = display_df["buy_exchange"]
        display_df["卖出交易所"] = display_df["sell_exchange"]
        display_df["价格差"] = display_df["price_difference"].apply(lambda x: f"{x:.2f}%")
        display_df["潜在利润"] = display_df["profit_potential"].apply(lambda x: f"${x:.0f}")
        display_df["实际利润"] = display_df["actual_profit"].apply(lambda x: f"${x:.0f}" if x > 0 else "-")
        display_df["持续时间"] = display_df["duration_seconds"].apply(lambda x: f"{x}秒")
        display_df["状态"] = display_df["status"].map({
            "executed": "✅ 已执行",
            "missed": "❌ 错过",
            "expired": "⏰ 过期",
            "cancelled": "🚫 取消"
        })

        # 显示表格
        st.dataframe(
            display_df[["时间", "交易对", "买入交易所", "卖出交易所", "价格差", "潜在利润", "实际利润", "持续时间", "状态"]],
            use_container_width=True,
            height=400
        )


def render_historical_arbitrage_tracker():
    """渲染历史套利机会追踪器主界面"""
    st.title("📊 历史套利机会追踪器")
    st.markdown("---")

    tracker = HistoricalArbitrageTracker()

    # 生成历史数据（快速加载）
    st.info("📊 正在加载历史数据...")
    df = tracker.generate_historical_data(30)

    # 渲染各个组件
    tracker.render_overview_metrics(df)
    st.markdown("---")

    tracker.render_profit_timeline(df)
    st.markdown("---")

    tracker.render_opportunity_patterns(df)
    st.markdown("---")

    tracker.render_duration_analysis(df)
    st.markdown("---")

    tracker.render_success_factors(df)
    st.markdown("---")

    tracker.render_detailed_history(df)

    # 刷新按钮
    if st.button("🔄 刷新数据", key="historical_tracker_refresh"):
        st.rerun()
