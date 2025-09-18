"""
多交易所价格比较组件
实时显示同一资产在不同交易所的价格差异，识别套利机会
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


class MultiExchangeComparison:
    """多交易所价格比较类"""

    def __init__(self):
        self.exchanges = [
            "Binance", "OKX", "Huobi", "KuCoin", "Gate.io",
            "Bybit", "Coinbase", "Kraken", "Bitfinex", "Bitstamp"
        ]

        self.popular_pairs = [
            "BTC/USDT", "ETH/USDT", "BNB/USDT", "XRP/USDT", "ADA/USDT",
            "SOL/USDT", "DOGE/USDT", "DOT/USDT", "MATIC/USDT", "AVAX/USDT",
            "LTC/USDT", "UNI/USDT", "LINK/USDT", "ATOM/USDT", "FIL/USDT"
        ]

        # 交易所特征（影响价格差异）
        self.exchange_features = {
            "Binance": {"liquidity": 0.95, "fee": 0.1, "region": "Global"},
            "OKX": {"liquidity": 0.90, "fee": 0.1, "region": "Global"},
            "Huobi": {"liquidity": 0.85, "fee": 0.2, "region": "Asia"},
            "KuCoin": {"liquidity": 0.80, "fee": 0.1, "region": "Global"},
            "Gate.io": {"liquidity": 0.75, "fee": 0.2, "region": "Global"},
            "Bybit": {"liquidity": 0.88, "fee": 0.1, "region": "Global"},
            "Coinbase": {"liquidity": 0.92, "fee": 0.5, "region": "US"},
            "Kraken": {"liquidity": 0.85, "fee": 0.26, "region": "EU"},
            "Bitfinex": {"liquidity": 0.82, "fee": 0.2, "region": "Global"},
            "Bitstamp": {"liquidity": 0.78, "fee": 0.5, "region": "EU"}
        }

    def generate_exchange_prices(self, pair: str) -> Dict[str, Dict]:
        """为指定交易对生成各交易所的价格数据"""
        base_price = random.uniform(0.1, 50000)

        exchange_data = {}

        for exchange in self.exchanges:
            features = self.exchange_features[exchange]

            # 基于交易所特征生成价格差异
            liquidity_factor = features["liquidity"]
            fee_factor = features["fee"] / 100

            # 价格偏差（流动性越低，偏差越大）
            price_deviation = random.gauss(0, (1 - liquidity_factor) * 0.02)

            # 最终价格
            final_price = base_price * (1 + price_deviation)

            # 买卖价差（基于手续费和流动性）
            spread_base = fee_factor + (1 - liquidity_factor) * 0.005
            spread = random.uniform(spread_base, spread_base * 2)

            bid_price = final_price * (1 - spread/2)
            ask_price = final_price * (1 + spread/2)

            # 24小时成交量（基于流动性）
            volume_24h = random.uniform(1000000, 100000000) * liquidity_factor

            # 24小时价格变化
            price_change_24h = random.uniform(-10, 10)

            # 订单簿深度
            depth_factor = liquidity_factor * random.uniform(0.8, 1.2)
            bid_depth = random.uniform(50000, 500000) * depth_factor
            ask_depth = random.uniform(50000, 500000) * depth_factor

            exchange_data[exchange] = {
                "price": final_price,
                "bid": bid_price,
                "ask": ask_price,
                "spread": spread * 100,  # 转换为百分比
                "volume_24h": volume_24h,
                "change_24h": price_change_24h,
                "bid_depth": bid_depth,
                "ask_depth": ask_depth,
                "liquidity": liquidity_factor,
                "fee": features["fee"],
                "region": features["region"],
                "last_update": datetime.now()
            }

        return exchange_data

    def calculate_arbitrage_opportunities(self, exchange_data: Dict[str, Dict]) -> List[Dict]:
        """计算套利机会"""
        opportunities = []

        exchanges = list(exchange_data.keys())

        for i in range(len(exchanges)):
            for j in range(i + 1, len(exchanges)):
                buy_exchange = exchanges[i]
                sell_exchange = exchanges[j]

                buy_price = exchange_data[buy_exchange]["ask"]  # 买入价格（卖单价格）
                sell_price = exchange_data[sell_exchange]["bid"]  # 卖出价格（买单价格）

                # 计算价格差异
                if sell_price > buy_price:
                    price_diff = ((sell_price - buy_price) / buy_price) * 100

                    # 计算手续费
                    buy_fee = exchange_data[buy_exchange]["fee"]
                    sell_fee = exchange_data[sell_exchange]["fee"]
                    total_fee = buy_fee + sell_fee

                    # 净利润
                    net_profit = price_diff - total_fee

                    if net_profit > 0.1:  # 最小利润阈值
                        # 计算执行难度
                        avg_liquidity = (exchange_data[buy_exchange]["liquidity"] +
                                       exchange_data[sell_exchange]["liquidity"]) / 2

                        if avg_liquidity > 0.9:
                            difficulty = "🟢 简单"
                        elif avg_liquidity > 0.8:
                            difficulty = "🟡 中等"
                        else:
                            difficulty = "🔴 困难"

                        # 风险评估
                        min_depth = min(exchange_data[buy_exchange]["bid_depth"],
                                      exchange_data[sell_exchange]["ask_depth"])

                        if min_depth > 100000:
                            risk = "🟢 低风险"
                        elif min_depth > 50000:
                            risk = "🟡 中风险"
                        else:
                            risk = "🔴 高风险"

                        opportunities.append({
                            "买入交易所": buy_exchange,
                            "卖出交易所": sell_exchange,
                            "买入价格": buy_price,
                            "卖出价格": sell_price,
                            "价格差异": price_diff,
                            "总手续费": total_fee,
                            "净利润": net_profit,
                            "执行难度": difficulty,
                            "风险等级": risk,
                            "最小深度": min_depth
                        })

        # 按净利润排序
        opportunities.sort(key=lambda x: x["净利润"], reverse=True)
        return opportunities

    def render_price_comparison_table(self, pair: str, exchange_data: Dict[str, Dict]):
        """渲染价格比较表格"""
        st.subheader(f"💱 {pair} 多交易所价格比较")

        # 准备表格数据
        table_data = []
        prices = [data["price"] for data in exchange_data.values()]
        min_price = min(prices)
        max_price = max(prices)

        for exchange, data in exchange_data.items():
            # 价格状态指示器
            if data["price"] == min_price:
                price_indicator = "🟢 最低"
            elif data["price"] == max_price:
                price_indicator = "🔴 最高"
            else:
                price_indicator = "⚪ 中等"

            # 24小时变化指示器
            change_indicator = "📈" if data["change_24h"] >= 0 else "📉"

            table_data.append({
                "交易所": exchange,
                "价格": f"${data['price']:.4f}",
                "状态": price_indicator,
                "买价": f"${data['bid']:.4f}",
                "卖价": f"${data['ask']:.4f}",
                "价差": f"{data['spread']:.3f}%",
                "24h变化": f"{change_indicator} {data['change_24h']:+.2f}%",
                "24h成交量": f"${data['volume_24h']/1e6:.1f}M",
                "流动性": f"{data['liquidity']*100:.0f}%",
                "手续费": f"{data['fee']:.2f}%",
                "地区": data["region"]
            })

        df = pd.DataFrame(table_data)

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "交易所": st.column_config.TextColumn("交易所", width="small"),
                "价格": st.column_config.TextColumn("价格", width="small"),
                "状态": st.column_config.TextColumn("状态", width="small"),
                "流动性": st.column_config.ProgressColumn(
                    "流动性",
                    help="交易所流动性评分",
                    min_value=0,
                    max_value=100,
                    format="%.0f%%"
                )
            }
        )

    def render_price_chart(self, pair: str, exchange_data: Dict[str, Dict]):
        """渲染价格对比图表"""
        st.subheader(f"📊 {pair} 价格分布图表")

        col1, col2 = st.columns(2)

        with col1:
            # 价格分布柱状图
            exchanges = list(exchange_data.keys())
            prices = [exchange_data[ex]["price"] for ex in exchanges]
            colors = ['red' if p == max(prices) else 'green' if p == min(prices) else 'blue'
                     for p in prices]

            fig_bar = go.Figure(data=[
                go.Bar(
                    x=exchanges,
                    y=prices,
                    marker_color=colors,
                    text=[f"${p:.4f}" for p in prices],
                    textposition='auto',
                )
            ])

            fig_bar.update_layout(
                title="各交易所价格对比",
                xaxis_title="交易所",
                yaxis_title="价格 (USD)",
                height=400
            )

            fig_bar.update_xaxes(tickangle=45)

            st.plotly_chart(fig_bar, use_container_width=True)

        with col2:
            # 买卖价差对比
            spreads = [exchange_data[ex]["spread"] for ex in exchanges]

            fig_spread = go.Figure(data=[
                go.Bar(
                    x=exchanges,
                    y=spreads,
                    marker_color='orange',
                    text=[f"{s:.3f}%" for s in spreads],
                    textposition='auto',
                )
            ])

            fig_spread.update_layout(
                title="各交易所买卖价差",
                xaxis_title="交易所",
                yaxis_title="价差 (%)",
                height=400
            )

            fig_spread.update_xaxes(tickangle=45)

            st.plotly_chart(fig_spread, use_container_width=True)

    def render_arbitrage_opportunities_table(self, pair: str, opportunities: List[Dict]):
        """渲染套利机会表格"""
        st.subheader(f"🎯 {pair} 套利机会")

        if opportunities:
            # 准备表格数据
            table_data = []
            for opp in opportunities[:10]:  # 显示前10个机会
                table_data.append({
                    "买入交易所": opp["买入交易所"],
                    "卖出交易所": opp["卖出交易所"],
                    "买入价格": f"${opp['买入价格']:.4f}",
                    "卖出价格": f"${opp['卖出价格']:.4f}",
                    "价格差异": f"{opp['价格差异']:.3f}%",
                    "总手续费": f"{opp['总手续费']:.3f}%",
                    "净利润": f"{opp['净利润']:.3f}%",
                    "执行难度": opp["执行难度"],
                    "风险等级": opp["风险等级"]
                })

            df_opp = pd.DataFrame(table_data)

            st.dataframe(
                df_opp,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "净利润": st.column_config.ProgressColumn(
                        "净利润",
                        help="扣除手续费后的净利润",
                        min_value=0,
                        max_value=5,
                        format="%.3f%%"
                    )
                }
            )

            # 显示最佳机会的详细信息
            if opportunities:
                best_opp = opportunities[0]
                st.success(
                    f"🏆 **最佳套利机会**: 在 {best_opp['买入交易所']} 买入，"
                    f"在 {best_opp['卖出交易所']} 卖出，净利润 {best_opp['净利润']:.3f}%"
                )
        else:
            st.info("当前没有发现有利可图的套利机会")

    def render_market_depth_comparison(self, pair: str, exchange_data: Dict[str, Dict]):
        """渲染市场深度比较"""
        st.subheader(f"📚 {pair} 市场深度比较")

        exchanges = list(exchange_data.keys())
        bid_depths = [exchange_data[ex]["bid_depth"] for ex in exchanges]
        ask_depths = [exchange_data[ex]["ask_depth"] for ex in exchanges]

        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('买单深度', '卖单深度'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}]]
        )

        # 买单深度
        fig.add_trace(
            go.Bar(
                x=exchanges,
                y=bid_depths,
                name="买单深度",
                marker_color='green',
                text=[f"${d/1000:.0f}K" for d in bid_depths],
                textposition='auto'
            ),
            row=1, col=1
        )

        # 卖单深度
        fig.add_trace(
            go.Bar(
                x=exchanges,
                y=ask_depths,
                name="卖单深度",
                marker_color='red',
                text=[f"${d/1000:.0f}K" for d in ask_depths],
                textposition='auto'
            ),
            row=1, col=2
        )

        fig.update_layout(
            height=400,
            showlegend=False
        )

        fig.update_xaxes(tickangle=45, row=1, col=1)
        fig.update_xaxes(tickangle=45, row=1, col=2)
        fig.update_yaxes(title_text="深度 (USD)", row=1, col=1)
        fig.update_yaxes(title_text="深度 (USD)", row=1, col=2)

        st.plotly_chart(fig, use_container_width=True)

    def render_real_time_alerts(self, opportunities: List[Dict]):
        """渲染实时警报"""
        st.subheader("🚨 实时套利警报")

        # 高利润机会警报
        high_profit_opps = [opp for opp in opportunities if opp["净利润"] > 2.0]

        if high_profit_opps:
            st.warning(f"🔥 发现 {len(high_profit_opps)} 个高利润套利机会 (>2%)")

            for opp in high_profit_opps[:3]:  # 显示前3个
                st.error(
                    f"⚡ **高利润警报**: {opp['买入交易所']} → {opp['卖出交易所']} "
                    f"净利润 {opp['净利润']:.3f}% ({opp['风险等级']})"
                )

        # 低风险机会警报
        low_risk_opps = [opp for opp in opportunities
                        if "低风险" in opp["风险等级"] and opp["净利润"] > 1.0]

        if low_risk_opps:
            st.success(f"✅ 发现 {len(low_risk_opps)} 个低风险套利机会 (>1%)")


def render_multi_exchange_comparison():
    """渲染多交易所价格比较仪表板"""
    st.subheader("💱 多交易所价格比较")

    # 创建比较器实例
    comparator = MultiExchangeComparison()

    # 交易对选择
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        selected_pair = st.selectbox(
            "选择交易对",
            options=comparator.popular_pairs,
            index=0,
            key="multi_exchange_pair"
        )

    with col2:
        auto_refresh = st.checkbox("自动刷新", value=False, key="multi_exchange_refresh")

    with col3:
        if st.button("🔄 手动刷新", key="manual_refresh_multi_exchange"):
            st.rerun()

    # 生成交易所数据
    exchange_data = comparator.generate_exchange_prices(selected_pair)

    # 计算套利机会
    opportunities = comparator.calculate_arbitrage_opportunities(exchange_data)

    # 渲染实时警报
    comparator.render_real_time_alerts(opportunities)

    st.divider()

    # 渲染价格比较表格
    comparator.render_price_comparison_table(selected_pair, exchange_data)

    st.divider()

    # 渲染价格图表
    comparator.render_price_chart(selected_pair, exchange_data)

    st.divider()

    # 渲染套利机会
    comparator.render_arbitrage_opportunities_table(selected_pair, opportunities)

    st.divider()

    # 渲染市场深度比较
    comparator.render_market_depth_comparison(selected_pair, exchange_data)

    # 自动刷新
    if auto_refresh:
        # 使用session state控制刷新间隔，避免冻结应用
        if 'multi_exchange_last_refresh' not in st.session_state:
            st.session_state.multi_exchange_last_refresh = datetime.now()
        
        time_since_refresh = (datetime.now() - st.session_state.multi_exchange_last_refresh).total_seconds()
        if time_since_refresh >= 30:
            st.session_state.multi_exchange_last_refresh = datetime.now()
            st.rerun()
