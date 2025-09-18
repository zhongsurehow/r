"""
可拖拽仪表盘布局定制系统
支持小部件管理、布局保存和个性化配置
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import json
from typing import Dict, List, Optional, Any, Tuple
import uuid

class DashboardCustomization:
    """仪表盘定制系统"""

    def __init__(self):
        self.available_widgets = self._load_available_widgets()
        self.default_layouts = self._load_default_layouts()
        self.widget_data = self._generate_widget_data()

    def _load_available_widgets(self) -> Dict[str, Dict]:
        """加载可用小部件"""
        return {
            "price_ticker": {
                "name": "价格行情",
                "description": "实时价格显示",
                "category": "market_data",
                "size": "small",
                "icon": "💰",
                "config": {
                    "symbols": ["BTC/USDT", "ETH/USDT", "BNB/USDT"],
                    "update_interval": 1,
                    "show_change": True,
                    "show_volume": True
                }
            },
            "price_chart": {
                "name": "价格图表",
                "description": "K线图表显示",
                "category": "charts",
                "size": "large",
                "icon": "📈",
                "config": {
                    "symbol": "BTC/USDT",
                    "timeframe": "1h",
                    "indicators": ["MA", "RSI"],
                    "chart_type": "candlestick"
                }
            },
            "arbitrage_opportunities": {
                "name": "套利机会",
                "description": "实时套利机会列表",
                "category": "arbitrage",
                "size": "medium",
                "icon": "⚡",
                "config": {
                    "min_profit": 1.0,
                    "max_results": 10,
                    "auto_refresh": True,
                    "show_exchanges": True
                }
            },
            "portfolio_overview": {
                "name": "投资组合概览",
                "description": "账户资产概览",
                "category": "portfolio",
                "size": "medium",
                "icon": "💼",
                "config": {
                    "show_pnl": True,
                    "show_allocation": True,
                    "currency": "USDT",
                    "chart_type": "pie"
                }
            },
            "order_book": {
                "name": "订单簿",
                "description": "买卖盘深度",
                "category": "market_data",
                "size": "medium",
                "icon": "📊",
                "config": {
                    "symbol": "BTC/USDT",
                    "depth": 20,
                    "show_spread": True,
                    "color_coding": True
                }
            },
            "trade_history": {
                "name": "交易历史",
                "description": "最近交易记录",
                "category": "trading",
                "size": "medium",
                "icon": "📋",
                "config": {
                    "max_records": 50,
                    "show_pnl": True,
                    "filter_by_symbol": False,
                    "auto_refresh": True
                }
            },
            "risk_metrics": {
                "name": "风险指标",
                "description": "实时风险监控",
                "category": "risk",
                "size": "small",
                "icon": "🛡️",
                "config": {
                    "metrics": ["VaR", "Sharpe", "MaxDD"],
                    "alert_threshold": 5.0,
                    "time_period": "24h",
                    "show_alerts": True
                }
            },
            "correlation_matrix": {
                "name": "相关性矩阵",
                "description": "资产相关性分析",
                "category": "analysis",
                "size": "large",
                "icon": "🔗",
                "config": {
                    "symbols": ["BTC", "ETH", "BNB", "ADA"],
                    "time_period": "30d",
                    "heatmap_style": "viridis",
                    "show_values": True
                }
            },
            "news_feed": {
                "name": "新闻动态",
                "description": "市场新闻和公告",
                "category": "information",
                "size": "medium",
                "icon": "📰",
                "config": {
                    "sources": ["CoinDesk", "CoinTelegraph"],
                    "max_items": 10,
                    "auto_refresh": True,
                    "filter_keywords": ["Bitcoin", "Ethereum"]
                }
            },
            "performance_chart": {
                "name": "绩效图表",
                "description": "策略绩效分析",
                "category": "performance",
                "size": "large",
                "icon": "📊",
                "config": {
                    "time_period": "30d",
                    "benchmark": "BTC",
                    "show_drawdown": True,
                    "metrics": ["return", "volatility"]
                }
            },
            "market_overview": {
                "name": "市场概览",
                "description": "整体市场状况",
                "category": "market_data",
                "size": "large",
                "icon": "🌍",
                "config": {
                    "top_coins": 20,
                    "sort_by": "market_cap",
                    "show_heatmap": True,
                    "time_frame": "24h"
                }
            },
            "alerts_panel": {
                "name": "警报面板",
                "description": "系统警报和通知",
                "category": "alerts",
                "size": "small",
                "icon": "🚨",
                "config": {
                    "max_alerts": 5,
                    "auto_dismiss": False,
                    "sound_enabled": True,
                    "priority_filter": "high"
                }
            }
        }

    def _load_default_layouts(self) -> Dict[str, Dict]:
        """加载默认布局"""
        return {
            "trader_layout": {
                "name": "交易者布局",
                "description": "专为活跃交易者设计",
                "widgets": [
                    {"id": "price_ticker", "position": {"row": 0, "col": 0, "width": 4}},
                    {"id": "price_chart", "position": {"row": 0, "col": 4, "width": 8}},
                    {"id": "order_book", "position": {"row": 1, "col": 0, "width": 4}},
                    {"id": "trade_history", "position": {"row": 1, "col": 4, "width": 4}},
                    {"id": "arbitrage_opportunities", "position": {"row": 1, "col": 8, "width": 4}},
                    {"id": "risk_metrics", "position": {"row": 2, "col": 0, "width": 6}},
                    {"id": "alerts_panel", "position": {"row": 2, "col": 6, "width": 6}}
                ]
            },
            "analyst_layout": {
                "name": "分析师布局",
                "description": "专为市场分析师设计",
                "widgets": [
                    {"id": "market_overview", "position": {"row": 0, "col": 0, "width": 8}},
                    {"id": "price_ticker", "position": {"row": 0, "col": 8, "width": 4}},
                    {"id": "correlation_matrix", "position": {"row": 1, "col": 0, "width": 6}},
                    {"id": "performance_chart", "position": {"row": 1, "col": 6, "width": 6}},
                    {"id": "news_feed", "position": {"row": 2, "col": 0, "width": 4}},
                    {"id": "portfolio_overview", "position": {"row": 2, "col": 4, "width": 4}},
                    {"id": "risk_metrics", "position": {"row": 2, "col": 8, "width": 4}}
                ]
            },
            "arbitrage_layout": {
                "name": "套利专用布局",
                "description": "专为套利交易设计",
                "widgets": [
                    {"id": "arbitrage_opportunities", "position": {"row": 0, "col": 0, "width": 6}},
                    {"id": "price_ticker", "position": {"row": 0, "col": 6, "width": 6}},
                    {"id": "price_chart", "position": {"row": 1, "col": 0, "width": 8}},
                    {"id": "order_book", "position": {"row": 1, "col": 8, "width": 4}},
                    {"id": "trade_history", "position": {"row": 2, "col": 0, "width": 6}},
                    {"id": "risk_metrics", "position": {"row": 2, "col": 6, "width": 3}},
                    {"id": "alerts_panel", "position": {"row": 2, "col": 9, "width": 3}}
                ]
            },
            "minimal_layout": {
                "name": "简约布局",
                "description": "简洁的监控界面",
                "widgets": [
                    {"id": "price_chart", "position": {"row": 0, "col": 0, "width": 8}},
                    {"id": "price_ticker", "position": {"row": 0, "col": 8, "width": 4}},
                    {"id": "portfolio_overview", "position": {"row": 1, "col": 0, "width": 6}},
                    {"id": "arbitrage_opportunities", "position": {"row": 1, "col": 6, "width": 6}}
                ]
            }
        }

    def _generate_widget_data(self) -> Dict[str, Any]:
        """生成小部件模拟数据"""
        np.random.seed(42)

        # 价格数据
        symbols = ["BTC/USDT", "ETH/USDT", "BNB/USDT", "ADA/USDT", "DOT/USDT"]
        prices = {
            "BTC/USDT": 45000 + np.random.normal(0, 1000),
            "ETH/USDT": 3000 + np.random.normal(0, 200),
            "BNB/USDT": 400 + np.random.normal(0, 50),
            "ADA/USDT": 1.2 + np.random.normal(0, 0.1),
            "DOT/USDT": 25 + np.random.normal(0, 3)
        }

        # 生成历史价格数据
        dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='1H')
        price_history = {}

        for symbol in symbols:
            base_price = prices[symbol]
            returns = np.random.normal(0, 0.02, len(dates))
            price_series = [base_price]

            for ret in returns[1:]:
                new_price = price_series[-1] * (1 + ret)
                price_series.append(new_price)

            price_history[symbol] = pd.DataFrame({
                'timestamp': dates,
                'price': price_series[:len(dates)],
                'volume': np.random.uniform(1000000, 10000000, len(dates))
            })

        # 套利机会数据
        arbitrage_opportunities = []
        for i in range(10):
            symbol = np.random.choice(symbols)
            profit = np.random.uniform(0.5, 5.0)
            arbitrage_opportunities.append({
                'symbol': symbol,
                'buy_exchange': np.random.choice(['Binance', 'Coinbase', 'Kraken']),
                'sell_exchange': np.random.choice(['Binance', 'Coinbase', 'Kraken']),
                'profit_pct': profit,
                'volume': np.random.uniform(1000, 50000),
                'timestamp': datetime.now() - timedelta(minutes=np.random.randint(0, 60))
            })

        # 投资组合数据
        portfolio = {
            'total_value': 125000,
            'pnl_24h': 2500,
            'pnl_pct_24h': 2.04,
            'assets': [
                {'symbol': 'BTC', 'amount': 1.5, 'value': 67500, 'allocation': 54.0},
                {'symbol': 'ETH', 'amount': 10.0, 'value': 30000, 'allocation': 24.0},
                {'symbol': 'BNB', 'amount': 50.0, 'value': 20000, 'allocation': 16.0},
                {'symbol': 'USDT', 'amount': 7500, 'value': 7500, 'allocation': 6.0}
            ]
        }

        # 风险指标
        risk_metrics = {
            'var_1d': -2.5,
            'var_7d': -8.2,
            'sharpe_ratio': 1.85,
            'max_drawdown': -5.2,
            'volatility': 15.6,
            'beta': 1.12
        }

        # 新闻数据
        news_items = [
            {
                'title': 'Bitcoin突破新高，市场情绪乐观',
                'source': 'CoinDesk',
                'timestamp': datetime.now() - timedelta(hours=1),
                'sentiment': 'positive'
            },
            {
                'title': '以太坊2.0升级进展顺利',
                'source': 'CoinTelegraph',
                'timestamp': datetime.now() - timedelta(hours=3),
                'sentiment': 'positive'
            },
            {
                'title': '监管政策可能影响加密货币市场',
                'source': 'CryptoNews',
                'timestamp': datetime.now() - timedelta(hours=5),
                'sentiment': 'neutral'
            }
        ]

        return {
            'prices': prices,
            'price_history': price_history,
            'arbitrage_opportunities': arbitrage_opportunities,
            'portfolio': portfolio,
            'risk_metrics': risk_metrics,
            'news_items': news_items
        }

    def render_widget(self, widget_id: str, config: Dict = None) -> bool:
        """渲染单个小部件"""
        if widget_id not in self.available_widgets:
            st.error(f"未知的小部件: {widget_id}")
            return False

        widget = self.available_widgets[widget_id]
        widget_config = config or widget['config']

        try:
            if widget_id == "price_ticker":
                self._render_price_ticker(widget_config)
            elif widget_id == "price_chart":
                self._render_price_chart(widget_config)
            elif widget_id == "arbitrage_opportunities":
                self._render_arbitrage_opportunities(widget_config)
            elif widget_id == "portfolio_overview":
                self._render_portfolio_overview(widget_config)
            elif widget_id == "order_book":
                self._render_order_book(widget_config)
            elif widget_id == "trade_history":
                self._render_trade_history(widget_config)
            elif widget_id == "risk_metrics":
                self._render_risk_metrics(widget_config)
            elif widget_id == "correlation_matrix":
                self._render_correlation_matrix(widget_config)
            elif widget_id == "news_feed":
                self._render_news_feed(widget_config)
            elif widget_id == "performance_chart":
                self._render_performance_chart(widget_config)
            elif widget_id == "market_overview":
                self._render_market_overview(widget_config)
            elif widget_id == "alerts_panel":
                self._render_alerts_panel(widget_config)
            else:
                st.warning(f"小部件 {widget_id} 的渲染器尚未实现")
                return False

            return True

        except Exception as e:
            st.error(f"渲染小部件 {widget_id} 时出错: {str(e)}")
            return False

    def _render_price_ticker(self, config: Dict):
        """渲染价格行情小部件"""
        st.subheader("💰 价格行情")

        symbols = config.get('symbols', ['BTC/USDT', 'ETH/USDT'])

        for symbol in symbols:
            if symbol in self.widget_data['prices']:
                price = self.widget_data['prices'][symbol]
                change_pct = np.random.uniform(-5, 5)

                col1, col2, col3 = st.columns([2, 1, 1])

                with col1:
                    st.write(f"**{symbol}**")

                with col2:
                    st.metric("价格", f"${price:,.2f}")

                with col3:
                    delta_color = "normal" if change_pct >= 0 else "inverse"
                    st.metric("24h变化", f"{change_pct:+.2f}%", delta=f"{change_pct:+.2f}%")

    def _render_price_chart(self, config: Dict):
        """渲染价格图表小部件"""
        st.subheader("📈 价格图表")

        symbol = config.get('symbol', 'BTC/USDT')

        if symbol in self.widget_data['price_history']:
            data = self.widget_data['price_history'][symbol]

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=data['timestamp'],
                y=data['price'],
                mode='lines',
                name=symbol,
                line=dict(color='#00ff88', width=2)
            ))

            fig.update_layout(
                title=f"{symbol} 价格走势",
                xaxis_title="时间",
                yaxis_title="价格 ($)",
                template="plotly_dark",
                height=300
            )

            st.plotly_chart(fig, use_container_width=True)

    def _render_arbitrage_opportunities(self, config: Dict):
        """渲染套利机会小部件"""
        st.subheader("⚡ 套利机会")

        opportunities = self.widget_data['arbitrage_opportunities']
        min_profit = config.get('min_profit', 1.0)
        max_results = config.get('max_results', 10)

        # 过滤和排序
        filtered_ops = [op for op in opportunities if op['profit_pct'] >= min_profit]
        filtered_ops = sorted(filtered_ops, key=lambda x: x['profit_pct'], reverse=True)[:max_results]

        if filtered_ops:
            for op in filtered_ops:
                with st.container():
                    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])

                    with col1:
                        st.write(f"**{op['symbol']}**")

                    with col2:
                        st.write(f"买入: {op['buy_exchange']}")
                        st.write(f"卖出: {op['sell_exchange']}")

                    with col3:
                        st.metric("利润", f"{op['profit_pct']:.2f}%")

                    with col4:
                        if st.button("执行", key=f"arb_{op['symbol']}_{op['buy_exchange']}"):
                            st.success("套利订单已提交!")

                    st.divider()
        else:
            st.info("当前没有符合条件的套利机会")

    def _render_portfolio_overview(self, config: Dict):
        """渲染投资组合概览小部件"""
        st.subheader("💼 投资组合概览")

        portfolio = self.widget_data['portfolio']

        # 总览指标
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("总价值", f"${portfolio['total_value']:,.0f}")

        with col2:
            st.metric("24h盈亏", f"${portfolio['pnl_24h']:,.0f}",
                     delta=f"{portfolio['pnl_pct_24h']:+.2f}%")

        with col3:
            st.metric("资产数量", len(portfolio['assets']))

        # 资产分配饼图
        if config.get('show_allocation', True):
            assets_df = pd.DataFrame(portfolio['assets'])

            fig = px.pie(
                assets_df,
                values='allocation',
                names='symbol',
                title="资产分配",
                template="plotly_dark"
            )
            fig.update_layout(height=250)
            st.plotly_chart(fig, use_container_width=True)

    def _render_order_book(self, config: Dict):
        """渲染订单簿小部件"""
        st.subheader("📊 订单簿")

        symbol = config.get('symbol', 'BTC/USDT')
        depth = config.get('depth', 10)

        # 生成模拟订单簿数据
        base_price = self.widget_data['prices'].get(symbol, 45000)

        # 买单
        buy_orders = []
        for i in range(depth):
            price = base_price * (1 - (i + 1) * 0.001)
            amount = np.random.uniform(0.1, 5.0)
            buy_orders.append({'价格': f"${price:.2f}", '数量': f"{amount:.3f}", '总额': f"${price * amount:.2f}"})

        # 卖单
        sell_orders = []
        for i in range(depth):
            price = base_price * (1 + (i + 1) * 0.001)
            amount = np.random.uniform(0.1, 5.0)
            sell_orders.append({'价格': f"${price:.2f}", '数量': f"{amount:.3f}", '总额': f"${price * amount:.2f}"})

        col1, col2 = st.columns(2)

        with col1:
            st.write("**卖单 (Ask)**")
            st.dataframe(pd.DataFrame(sell_orders[:5]), hide_index=True, use_container_width=True)

        with col2:
            st.write("**买单 (Bid)**")
            st.dataframe(pd.DataFrame(buy_orders[:5]), hide_index=True, use_container_width=True)

        # 价差
        spread = (sell_orders[0]['价格'].replace('$', '').replace(',', '')) - (buy_orders[0]['价格'].replace('$', '').replace(',', ''))
        st.metric("买卖价差", f"${float(spread):.2f}")

    def _render_trade_history(self, config: Dict):
        """渲染交易历史小部件"""
        st.subheader("📋 交易历史")

        max_records = config.get('max_records', 10)

        # 生成模拟交易数据
        trades = []
        for i in range(max_records):
            symbol = np.random.choice(['BTC/USDT', 'ETH/USDT', 'BNB/USDT'])
            side = np.random.choice(['买入', '卖出'])
            amount = np.random.uniform(0.1, 2.0)
            price = self.widget_data['prices'][symbol] * (1 + np.random.normal(0, 0.01))
            pnl = np.random.uniform(-100, 200)

            trades.append({
                '时间': (datetime.now() - timedelta(hours=i)).strftime('%H:%M'),
                '交易对': symbol,
                '方向': side,
                '数量': f"{amount:.3f}",
                '价格': f"${price:.2f}",
                '盈亏': f"${pnl:+.2f}"
            })

        st.dataframe(pd.DataFrame(trades), hide_index=True, use_container_width=True)

    def _render_risk_metrics(self, config: Dict):
        """渲染风险指标小部件"""
        st.subheader("🛡️ 风险指标")

        metrics = self.widget_data['risk_metrics']

        col1, col2 = st.columns(2)

        with col1:
            st.metric("VaR (1天)", f"{metrics['var_1d']:.1f}%")
            st.metric("最大回撤", f"{metrics['max_drawdown']:.1f}%")
            st.metric("波动率", f"{metrics['volatility']:.1f}%")

        with col2:
            st.metric("夏普比率", f"{metrics['sharpe_ratio']:.2f}")
            st.metric("Beta系数", f"{metrics['beta']:.2f}")

            # 风险等级
            if abs(metrics['var_1d']) < 2:
                risk_level = "🟢 低风险"
            elif abs(metrics['var_1d']) < 5:
                risk_level = "🟡 中等风险"
            else:
                risk_level = "🔴 高风险"

            st.write(f"**风险等级:** {risk_level}")

    def _render_correlation_matrix(self, config: Dict):
        """渲染相关性矩阵小部件"""
        st.subheader("🔗 相关性矩阵")

        symbols = config.get('symbols', ['BTC', 'ETH', 'BNB', 'ADA'])

        # 生成相关性矩阵
        np.random.seed(42)
        corr_matrix = np.random.uniform(0.3, 0.9, (len(symbols), len(symbols)))
        np.fill_diagonal(corr_matrix, 1.0)

        # 确保矩阵对称
        corr_matrix = (corr_matrix + corr_matrix.T) / 2
        np.fill_diagonal(corr_matrix, 1.0)

        fig = px.imshow(
            corr_matrix,
            x=symbols,
            y=symbols,
            color_continuous_scale='RdYlBu_r',
            title="资产相关性矩阵",
            template="plotly_dark"
        )

        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

    def _render_news_feed(self, config: Dict):
        """渲染新闻动态小部件"""
        st.subheader("📰 新闻动态")

        news_items = self.widget_data['news_items']
        max_items = config.get('max_items', 5)

        for item in news_items[:max_items]:
            with st.container():
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.write(f"**{item['title']}**")
                    st.caption(f"{item['source']} • {item['timestamp'].strftime('%H:%M')}")

                with col2:
                    if item['sentiment'] == 'positive':
                        st.success("📈 积极")
                    elif item['sentiment'] == 'negative':
                        st.error("📉 消极")
                    else:
                        st.info("📊 中性")

                st.divider()

    def _render_performance_chart(self, config: Dict):
        """渲染绩效图表小部件"""
        st.subheader("📊 绩效图表")

        # 生成绩效数据
        dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='1D')
        portfolio_returns = np.random.normal(0.001, 0.02, len(dates))
        benchmark_returns = np.random.normal(0.0005, 0.025, len(dates))

        portfolio_curve = (1 + pd.Series(portfolio_returns)).cumprod()
        benchmark_curve = (1 + pd.Series(benchmark_returns)).cumprod()

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=dates,
            y=portfolio_curve,
            mode='lines',
            name='投资组合',
            line=dict(color='#00ff88', width=2)
        ))

        fig.add_trace(go.Scatter(
            x=dates,
            y=benchmark_curve,
            mode='lines',
            name='基准 (BTC)',
            line=dict(color='#ff6b6b', width=2)
        ))

        fig.update_layout(
            title="绩效对比",
            xaxis_title="时间",
            yaxis_title="累计收益",
            template="plotly_dark",
            height=300
        )

        st.plotly_chart(fig, use_container_width=True)

    def _render_market_overview(self, config: Dict):
        """渲染市场概览小部件"""
        st.subheader("🌍 市场概览")

        # 生成市场数据
        top_coins = config.get('top_coins', 10)

        market_data = []
        for i in range(top_coins):
            coin = f"COIN{i+1}"
            price = np.random.uniform(1, 1000)
            change_24h = np.random.uniform(-10, 15)
            market_cap = np.random.uniform(1e9, 1e12)

            market_data.append({
                '币种': coin,
                '价格': f"${price:.2f}",
                '24h变化': f"{change_24h:+.2f}%",
                '市值': f"${market_cap/1e9:.1f}B"
            })

        st.dataframe(pd.DataFrame(market_data), hide_index=True, use_container_width=True)

    def _render_alerts_panel(self, config: Dict):
        """渲染警报面板小部件"""
        st.subheader("🚨 警报面板")

        # 生成警报数据
        alerts = [
            {"type": "warning", "message": "BTC价格波动超过5%", "time": "2分钟前"},
            {"type": "info", "message": "发现新的套利机会", "time": "5分钟前"},
            {"type": "error", "message": "风险指标超过阈值", "time": "10分钟前"}
        ]

        for alert in alerts:
            if alert['type'] == 'error':
                st.error(f"🔴 {alert['message']} ({alert['time']})")
            elif alert['type'] == 'warning':
                st.warning(f"🟡 {alert['message']} ({alert['time']})")
            else:
                st.info(f"🔵 {alert['message']} ({alert['time']})")

    def render_layout_designer(self):
        """渲染布局设计器"""
        st.subheader("🎨 布局设计器")

        # 布局选择
        col1, col2 = st.columns([2, 1])

        with col1:
            layout_key = st.selectbox(
                "选择预设布局",
                list(self.default_layouts.keys()),
                format_func=lambda x: self.default_layouts[x]['name']
            )

        with col2:
            if st.button("应用布局", type="primary"):
                st.session_state['current_layout'] = layout_key
                st.success(f"已应用 {self.default_layouts[layout_key]['name']}")

        # 小部件库
        st.subheader("📦 小部件库")

        # 按类别分组显示小部件
        categories = {}
        for widget_id, widget in self.available_widgets.items():
            category = widget['category']
            if category not in categories:
                categories[category] = []
            categories[category].append((widget_id, widget))

        for category, widgets in categories.items():
            with st.expander(f"📂 {category.replace('_', ' ').title()}"):
                cols = st.columns(3)
                for i, (widget_id, widget) in enumerate(widgets):
                    with cols[i % 3]:
                        st.write(f"{widget['icon']} **{widget['name']}**")
                        st.caption(widget['description'])
                        if st.button(f"添加", key=f"add_{widget_id}"):
                            st.info(f"已添加 {widget['name']} 到布局")

        # 当前布局预览
        if 'current_layout' in st.session_state:
            current_layout = self.default_layouts[st.session_state['current_layout']]
            st.subheader(f"📋 当前布局: {current_layout['name']}")

            # 显示布局中的小部件
            for widget_info in current_layout['widgets']:
                widget_id = widget_info['id']
                widget = self.available_widgets[widget_id]

                col1, col2, col3 = st.columns([2, 1, 1])

                with col1:
                    st.write(f"{widget['icon']} {widget['name']}")

                with col2:
                    st.write(f"位置: {widget_info['position']}")

                with col3:
                    if st.button("移除", key=f"remove_{widget_id}"):
                        st.warning(f"已从布局中移除 {widget['name']}")

    def render_widget_configurator(self, widget_id: str):
        """渲染小部件配置器"""
        if widget_id not in self.available_widgets:
            return None

        widget = self.available_widgets[widget_id]
        st.subheader(f"⚙️ 配置 {widget['name']}")

        config = widget['config'].copy()

        # 动态生成配置选项
        for key, value in config.items():
            if isinstance(value, bool):
                config[key] = st.checkbox(key.replace('_', ' ').title(), value=value)
            elif isinstance(value, (int, float)):
                config[key] = st.number_input(key.replace('_', ' ').title(), value=value)
            elif isinstance(value, str):
                config[key] = st.text_input(key.replace('_', ' ').title(), value=value)
            elif isinstance(value, list):
                if all(isinstance(item, str) for item in value):
                    config[key] = st.multiselect(
                        key.replace('_', ' ').title(),
                        options=value + ['BTC/USDT', 'ETH/USDT', 'BNB/USDT'],  # 添加更多选项
                        default=value
                    )

        return config

def render_dashboard_customization():
    """渲染仪表盘定制主界面"""
    st.title("🎨 仪表盘定制")

    # 创建定制系统实例
    dashboard = DashboardCustomization()

    # 创建标签页
    tab1, tab2, tab3, tab4 = st.tabs([
        "🏠 我的仪表盘",
        "🎨 布局设计",
        "📦 小部件管理",
        "⚙️ 设置"
    ])

    with tab1:
        st.subheader("🏠 我的仪表盘")

        # 获取当前布局
        current_layout_key = st.session_state.get('current_layout', 'trader_layout')
        current_layout = dashboard.default_layouts[current_layout_key]

        st.info(f"当前布局: {current_layout['name']} - {current_layout['description']}")

        # 渲染布局中的小部件
        for widget_info in current_layout['widgets']:
            widget_id = widget_info['id']

            with st.container():
                # 小部件标题栏
                col1, col2, col3 = st.columns([6, 1, 1])

                with col1:
                    widget = dashboard.available_widgets[widget_id]
                    st.write(f"### {widget['icon']} {widget['name']}")

                with col2:
                    if st.button("⚙️", key=f"config_{widget_id}", help="配置"):
                        st.session_state[f'config_{widget_id}'] = True

                with col3:
                    if st.button("❌", key=f"close_{widget_id}", help="关闭"):
                        st.info(f"已关闭 {widget['name']}")
                        continue

                # 渲染小部件内容
                try:
                    dashboard.render_widget(widget_id)
                except Exception as e:
                    st.error(f"渲染小部件时出错: {str(e)}")

                st.divider()

    with tab2:
        dashboard.render_layout_designer()

    with tab3:
        st.subheader("📦 小部件管理")

        # 小部件搜索
        search_term = st.text_input("🔍 搜索小部件", placeholder="输入小部件名称或描述...")

        # 类别过滤
        categories = list(set(widget['category'] for widget in dashboard.available_widgets.values()))
        selected_categories = st.multiselect("📂 按类别过滤", categories, default=categories)

        # 显示小部件
        filtered_widgets = {}
        for widget_id, widget in dashboard.available_widgets.items():
            if widget['category'] in selected_categories:
                if not search_term or search_term.lower() in widget['name'].lower() or search_term.lower() in widget['description'].lower():
                    filtered_widgets[widget_id] = widget

        # 网格显示小部件
        cols = st.columns(3)
        for i, (widget_id, widget) in enumerate(filtered_widgets.items()):
            with cols[i % 3]:
                with st.container():
                    st.write(f"### {widget['icon']} {widget['name']}")
                    st.caption(widget['description'])
                    st.write(f"**类别:** {widget['category']}")
                    st.write(f"**大小:** {widget['size']}")

                    col1, col2 = st.columns(2)

                    with col1:
                        if st.button("预览", key=f"preview_{widget_id}"):
                            with st.expander(f"预览 {widget['name']}", expanded=True):
                                dashboard.render_widget(widget_id)

                    with col2:
                        if st.button("添加", key=f"add_widget_{widget_id}"):
                            st.success(f"已添加 {widget['name']}")

                    st.divider()

    with tab4:
        st.subheader("⚙️ 设置")

        # 全局设置
        st.write("#### 🌐 全局设置")

        col1, col2 = st.columns(2)

        with col1:
            auto_refresh = st.checkbox("自动刷新", value=True)
            refresh_interval = st.slider("刷新间隔 (秒)", 1, 60, 5)
            show_grid = st.checkbox("显示网格", value=False)

        with col2:
            compact_mode = st.checkbox("紧凑模式", value=False)
            dark_theme = st.checkbox("深色主题", value=True)
            animations = st.checkbox("启用动画", value=True)

        # 布局设置
        st.write("#### 📐 布局设置")

        col1, col2 = st.columns(2)

        with col1:
            grid_columns = st.slider("网格列数", 6, 24, 12)
            widget_spacing = st.slider("小部件间距", 0, 20, 5)

        with col2:
            header_height = st.slider("标题栏高度", 30, 80, 50)
            sidebar_width = st.slider("侧边栏宽度", 200, 400, 300)

        # 保存设置
        if st.button("💾 保存设置", type="primary"):
            settings = {
                'auto_refresh': auto_refresh,
                'refresh_interval': refresh_interval,
                'show_grid': show_grid,
                'compact_mode': compact_mode,
                'dark_theme': dark_theme,
                'animations': animations,
                'grid_columns': grid_columns,
                'widget_spacing': widget_spacing,
                'header_height': header_height,
                'sidebar_width': sidebar_width
            }

            st.session_state['dashboard_settings'] = settings
            st.success("✅ 设置已保存")

        # 导入/导出布局
        st.write("#### 📁 布局管理")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("📤 导出当前布局"):
                current_layout_key = st.session_state.get('current_layout', 'trader_layout')
                layout_data = dashboard.default_layouts[current_layout_key]

                layout_json = json.dumps(layout_data, indent=2, ensure_ascii=False)
                st.download_button(
                    label="下载布局文件",
                    data=layout_json,
                    file_name=f"layout_{current_layout_key}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )

        with col2:
            uploaded_file = st.file_uploader("📥 导入布局", type=['json'])
            if uploaded_file is not None:
                try:
                    layout_data = json.load(uploaded_file)
                    st.success("✅ 布局导入成功")
                    st.json(layout_data)
                except Exception as e:
                    st.error(f"导入失败: {str(e)}")

    # 功能说明
    with st.expander("📖 功能说明"):
        st.markdown("""
        ### 🎨 仪表盘定制特性

        **🏠 我的仪表盘**
        - 📊 实时显示所有小部件
        - ⚙️ 快速配置小部件
        - 🔄 拖拽重新排列 (模拟)
        - 💾 自动保存布局

        **🎨 布局设计**
        - 📐 预设专业布局
        - 🎯 交易者/分析师/套利专用
        - 📦 小部件库浏览
        - 🔧 自定义布局创建

        **📦 小部件管理**
        - 🔍 智能搜索和过滤
        - 📂 按类别组织
        - 👀 实时预览功能
        - ➕ 一键添加到布局

        **⚙️ 高级设置**
        - 🌐 全局界面设置
        - 📐 网格和间距控制
        - 📁 布局导入/导出
        - 💾 配置持久化保存

        **🎯 支持的小部件类型**
        - 💰 价格行情和图表
        - ⚡ 套利机会监控
        - 💼 投资组合管理
        - 📊 市场数据分析
        - 🛡️ 风险控制面板
        - 📰 新闻和信息流
        """)

    return True

if __name__ == "__main__":
    render_dashboard_customization()
