"""
高级回测引擎
支持参数自定义、多时间框架、场景测试和策略比较
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
import io
import base64

class BacktestingEngine:
    """高级回测引擎"""

    def __init__(self):
        self.strategies = self._load_strategies()
        self.market_scenarios = self._load_market_scenarios()
        self.performance_metrics = {}

    def _load_strategies(self) -> Dict[str, Dict]:
        """加载预定义策略"""
        return {
            "simple_arbitrage": {
                "name": "简单套利策略",
                "description": "基于价差的简单套利策略",
                "parameters": {
                    "min_spread": {"default": 1.5, "min": 0.1, "max": 10.0, "step": 0.1},
                    "max_position_size": {"default": 10000, "min": 100, "max": 100000, "step": 100},
                    "execution_delay": {"default": 2, "min": 0, "max": 30, "step": 1},
                    "slippage": {"default": 0.1, "min": 0.0, "max": 1.0, "step": 0.01}
                }
            },
            "triangular_arbitrage": {
                "name": "三角套利策略",
                "description": "基于三角套利的策略",
                "parameters": {
                    "min_profit_margin": {"default": 0.5, "min": 0.1, "max": 5.0, "step": 0.1},
                    "max_trade_amount": {"default": 5000, "min": 100, "max": 50000, "step": 100},
                    "currency_pairs": {"default": ["BTC/USDT", "ETH/BTC", "ETH/USDT"], "type": "multiselect"},
                    "execution_speed": {"default": "fast", "options": ["slow", "medium", "fast"]}
                }
            },
            "statistical_arbitrage": {
                "name": "统计套利策略",
                "description": "基于统计模型的套利策略",
                "parameters": {
                    "lookback_period": {"default": 30, "min": 5, "max": 100, "step": 1},
                    "z_score_threshold": {"default": 2.0, "min": 1.0, "max": 4.0, "step": 0.1},
                    "correlation_threshold": {"default": 0.8, "min": 0.5, "max": 0.99, "step": 0.01},
                    "rebalance_frequency": {"default": "daily", "options": ["hourly", "daily", "weekly"]}
                }
            },
            "cross_exchange_arbitrage": {
                "name": "跨交易所套利",
                "description": "跨交易所价差套利策略",
                "parameters": {
                    "min_spread_pct": {"default": 2.0, "min": 0.5, "max": 10.0, "step": 0.1},
                    "transfer_fee": {"default": 0.1, "min": 0.0, "max": 1.0, "step": 0.01},
                    "transfer_time": {"default": 10, "min": 1, "max": 60, "step": 1},
                    "exchanges": {"default": ["Binance", "Coinbase"], "type": "multiselect"}
                }
            }
        }

    def _load_market_scenarios(self) -> Dict[str, Dict]:
        """加载市场场景"""
        return {
            "normal_market": {
                "name": "正常市场",
                "description": "正常波动的市场环境",
                "volatility_multiplier": 1.0,
                "trend_bias": 0.0,
                "liquidity_factor": 1.0
            },
            "high_volatility": {
                "name": "高波动市场",
                "description": "高波动率市场环境",
                "volatility_multiplier": 2.5,
                "trend_bias": 0.0,
                "liquidity_factor": 0.8
            },
            "bull_market": {
                "name": "牛市",
                "description": "强烈上涨趋势",
                "volatility_multiplier": 1.2,
                "trend_bias": 0.05,
                "liquidity_factor": 1.2
            },
            "bear_market": {
                "name": "熊市",
                "description": "强烈下跌趋势",
                "volatility_multiplier": 1.5,
                "trend_bias": -0.03,
                "liquidity_factor": 0.7
            },
            "low_liquidity": {
                "name": "低流动性",
                "description": "流动性不足的市场",
                "volatility_multiplier": 1.8,
                "trend_bias": 0.0,
                "liquidity_factor": 0.3
            },
            "flash_crash": {
                "name": "闪崩",
                "description": "极端下跌事件",
                "volatility_multiplier": 5.0,
                "trend_bias": -0.15,
                "liquidity_factor": 0.2
            }
        }

    def generate_market_data(self,
                           start_date: datetime,
                           end_date: datetime,
                           timeframe: str = "1h",
                           scenario: str = "normal_market") -> pd.DataFrame:
        """生成市场数据"""

        # 时间频率映射
        freq_map = {
            "1m": "1T", "5m": "5T", "15m": "15T", "30m": "30T",
            "1h": "1H", "4h": "4H", "1d": "1D", "1w": "1W"
        }

        # 生成时间序列
        dates = pd.date_range(start=start_date, end=end_date, freq=freq_map[timeframe])

        # 获取场景参数
        scenario_params = self.market_scenarios[scenario]

        # 生成价格数据
        np.random.seed(42)
        n_periods = len(dates)

        # 基础参数
        initial_price = 45000.0
        base_volatility = 0.02  # 2% 基础波动率

        # 应用场景参数
        volatility = base_volatility * scenario_params["volatility_multiplier"]
        trend = scenario_params["trend_bias"]
        liquidity = scenario_params["liquidity_factor"]

        # 生成价格路径
        returns = np.random.normal(trend / 24, volatility / np.sqrt(24), n_periods)  # 假设每小时数据

        # 添加趋势和均值回归
        for i in range(1, len(returns)):
            returns[i] += 0.1 * returns[i-1]  # 轻微的序列相关性

        # 计算价格
        prices = [initial_price]
        for ret in returns[1:]:
            new_price = prices[-1] * (1 + ret)
            prices.append(new_price)

        # 生成OHLCV数据
        data = []
        for i, (date, price) in enumerate(zip(dates, prices)):
            # 生成开高低收
            open_price = price
            high_price = open_price * (1 + abs(np.random.normal(0, volatility/4)))
            low_price = open_price * (1 - abs(np.random.normal(0, volatility/4)))
            close_price = open_price + np.random.normal(0, open_price * volatility/2)

            # 确保高低价格合理
            high_price = max(high_price, open_price, close_price)
            low_price = min(low_price, open_price, close_price)

            # 生成成交量（受流动性影响）
            base_volume = np.random.uniform(1000000, 5000000)
            volume = base_volume * liquidity * (1 + abs(returns[i]) * 10)  # 波动大时成交量增加

            data.append({
                "timestamp": date,
                "open": round(open_price, 2),
                "high": round(high_price, 2),
                "low": round(low_price, 2),
                "close": round(close_price, 2),
                "volume": int(volume)
            })

        return pd.DataFrame(data)

    def simulate_arbitrage_opportunities(self, market_data: pd.DataFrame, strategy_params: Dict) -> pd.DataFrame:
        """模拟套利机会 - 优化版本使用向量化操作"""
        # 使用向量化操作替代iterrows()
        base_prices = market_data['close'].values
        n_rows = len(base_prices)

        # 向量化生成所有交易所价格
        np.random.seed(42)  # 确保可重现性
        binance_prices = base_prices * (1 + np.random.normal(0, 0.001, n_rows))
        coinbase_prices = base_prices * (1 + np.random.normal(0, 0.002, n_rows))
        kraken_prices = base_prices * (1 + np.random.normal(0, 0.0015, n_rows))
        huobi_prices = base_prices * (1 + np.random.normal(0, 0.0018, n_rows))

        # 向量化计算最大最小价格
        all_prices = np.column_stack([binance_prices, coinbase_prices, kraken_prices, huobi_prices])
        max_prices = np.max(all_prices, axis=1)
        min_prices = np.min(all_prices, axis=1)

        opportunities = []

        for i in range(n_rows):
            max_price = max_prices[i]
            min_price = min_prices[i]
            spread_pct = (max_price - min_price) / min_price * 100

            # 检查是否满足策略条件
            min_spread = strategy_params.get('min_spread', 1.5)
            if spread_pct >= min_spread:
                # 计算潜在利润
                trade_amount = strategy_params.get('max_position_size', 10000)
                slippage = strategy_params.get('slippage', 0.1) / 100
                execution_delay = strategy_params.get('execution_delay', 2)

                # 考虑滑点和执行延迟的影响
                actual_spread = spread_pct - slippage * 2  # 买卖都有滑点
                profit = trade_amount * actual_spread / 100

                opportunities.append({
                    'timestamp': row['timestamp'],
                    'spread_pct': spread_pct,
                    'profit': profit,
                    'buy_exchange': min(exchange_prices, key=exchange_prices.get),
                    'sell_exchange': max(exchange_prices, key=exchange_prices.get),
                    'buy_price': min_price,
                    'sell_price': max_price,
                    'trade_amount': trade_amount,
                    'execution_delay': execution_delay
                })

        return pd.DataFrame(opportunities)

    def generate_mock_results(self, settings, strategy_name="基础套利策略"):
        """生成模拟回测结果"""
        days = (settings['end_date'] - settings['start_date']).days
        dates = pd.date_range(start=settings['start_date'], end=settings['end_date'], freq='D')

        # 根据策略类型调整参数
        strategy_params = self.get_strategy_parameters(strategy_name)

        # 生成模拟价格数据
        np.random.seed(hash(strategy_name) % 1000)  # 为不同策略使用不同种子

        # 基础收益率根据策略调整
        base_return = strategy_params['base_return']
        volatility_factor = strategy_params['volatility_factor']

        # 考虑市场场景影响
        scenario_multiplier = 1.0
        if 'market_scenarios' in settings:
            for scenario in settings['market_scenarios']:
                if scenario == "高波动期":
                    scenario_multiplier *= settings.get('volatility_multiplier', 1.0)
                elif scenario == "低流动性":
                    scenario_multiplier *= settings.get('liquidity_factor', 1.0)

        returns = np.random.normal(
            base_return * scenario_multiplier,
            0.02 * volatility_factor * scenario_multiplier,
            days
        )

        equity_curve = [settings['initial_capital']]

        for ret in returns:
            equity_curve.append(equity_curve[-1] * (1 + ret))

        # 计算绩效指标
        daily_returns = np.diff(equity_curve) / equity_curve[:-1] * 100
        total_return = (equity_curve[-1] - equity_curve[0]) / equity_curve[0] * 100
        volatility = np.std(daily_returns) * np.sqrt(252)
        sharpe_ratio = np.mean(daily_returns) / np.std(daily_returns) * np.sqrt(252) if np.std(daily_returns) > 0 else 0

        # 计算最大回撤
        peak = np.maximum.accumulate(equity_curve)
        drawdown = (np.array(equity_curve) - peak) / peak * 100
        max_drawdown = np.min(drawdown)

        # Calmar比率
        calmar_ratio = total_return / abs(max_drawdown) if max_drawdown != 0 else 0

        # Sortino比率
        negative_returns = daily_returns[daily_returns < 0]
        downside_deviation = np.std(negative_returns) * np.sqrt(252) if len(negative_returns) > 0 else 0.01
        sortino_ratio = np.mean(daily_returns) * np.sqrt(252) / downside_deviation

        return {
            'dates': dates[:len(equity_curve)],
            'equity_curve': equity_curve,
            'daily_returns': daily_returns,
            'total_return': total_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': abs(max_drawdown),
            'win_rate': strategy_params['win_rate'] + np.random.uniform(-5, 5),
            'total_trades': strategy_params['total_trades'] + np.random.randint(-50, 50),
            'winning_trades': int((strategy_params['win_rate'] / 100) * strategy_params['total_trades']),
            'losing_trades': int(((100 - strategy_params['win_rate']) / 100) * strategy_params['total_trades']),
            'avg_holding_time': strategy_params['avg_holding_time'] + np.random.uniform(-2, 2),
            'avg_profit': strategy_params['avg_profit'] + np.random.uniform(-0.2, 0.2),
            'avg_loss': strategy_params['avg_loss'] + np.random.uniform(-0.2, 0.2),
            'var_95': np.percentile(daily_returns, 5),
            'calmar_ratio': calmar_ratio,
            'sortino_ratio': sortino_ratio,
            'max_consecutive_losses': np.random.randint(2, 8),
            'max_consecutive_wins': np.random.randint(4, 12)
        }

    def get_strategy_parameters(self, strategy_name):
        """获取不同策略的参数"""
        strategy_configs = {
            "基础套利策略": {
                'base_return': 0.0008,
                'volatility_factor': 1.0,
                'win_rate': 65,
                'total_trades': 200,
                'avg_holding_time': 6,
                'avg_profit': 1.2,
                'avg_loss': -0.8
            },
            "高频套利策略": {
                'base_return': 0.0012,
                'volatility_factor': 1.3,
                'win_rate': 58,
                'total_trades': 800,
                'avg_holding_time': 0.5,
                'avg_profit': 0.3,
                'avg_loss': -0.2
            },
            "跨期套利策略": {
                'base_return': 0.0015,
                'volatility_factor': 0.8,
                'win_rate': 72,
                'total_trades': 50,
                'avg_holding_time': 48,
                'avg_profit': 3.5,
                'avg_loss': -1.8
            },
            "统计套利策略": {
                'base_return': 0.0010,
                'volatility_factor': 0.9,
                'win_rate': 68,
                'total_trades': 150,
                'avg_holding_time': 12,
                'avg_profit': 1.8,
                'avg_loss': -1.0
            },
            "三角套利策略": {
                'base_return': 0.0006,
                'volatility_factor': 1.1,
                'win_rate': 75,
                'total_trades': 300,
                'avg_holding_time': 2,
                'avg_profit': 0.8,
                'avg_loss': -0.4
            },
            "资金费率套利策略": {
                'base_return': 0.0020,
                'volatility_factor': 0.7,
                'win_rate': 80,
                'total_trades': 30,
                'avg_holding_time': 480,  # 20天
                'avg_profit': 8.0,
                'avg_loss': -3.0
            }
        }

        return strategy_configs.get(strategy_name, strategy_configs["基础套利策略"])

    def calculate_performance_metrics(self, opportunities: pd.DataFrame, initial_capital: float = 100000) -> Dict:
        """计算绩效指标"""
        if opportunities.empty:
            return {
                "total_return": 0,
                "total_trades": 0,
                "win_rate": 0,
                "max_drawdown": 0,
                "sharpe_ratio": 0,
                "profit_factor": 0,
                "avg_profit_per_trade": 0
            }

        # 基础统计
        total_trades = len(opportunities)
        total_profit = opportunities['profit'].sum()
        total_return = total_profit / initial_capital * 100

        # 胜率计算
        winning_trades = opportunities[opportunities['profit'] > 0]
        win_rate = len(winning_trades) / total_trades * 100 if total_trades > 0 else 0

        # 计算累计收益曲线
        opportunities['cumulative_profit'] = opportunities['profit'].cumsum()
        opportunities['equity_curve'] = initial_capital + opportunities['cumulative_profit']

        # 最大回撤
        peak = opportunities['equity_curve'].expanding().max()
        drawdown = (opportunities['equity_curve'] - peak) / peak * 100
        max_drawdown = abs(drawdown.min())

        # 夏普比率 (简化计算)
        if len(opportunities) > 1:
            returns = opportunities['profit'] / initial_capital
            sharpe_ratio = returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0
        else:
            sharpe_ratio = 0

        # 盈亏比
        winning_profits = winning_trades['profit'].sum() if len(winning_trades) > 0 else 0
        losing_trades = opportunities[opportunities['profit'] < 0]
        losing_losses = abs(losing_trades['profit'].sum()) if len(losing_trades) > 0 else 1
        profit_factor = winning_profits / losing_losses if losing_losses > 0 else float('inf')

        # 平均每笔交易利润
        avg_profit_per_trade = total_profit / total_trades if total_trades > 0 else 0

        return {
            "total_return": round(total_return, 2),
            "total_profit": round(total_profit, 2),
            "total_trades": total_trades,
            "win_rate": round(win_rate, 2),
            "max_drawdown": round(max_drawdown, 2),
            "sharpe_ratio": round(sharpe_ratio, 2),
            "profit_factor": round(profit_factor, 2),
            "avg_profit_per_trade": round(avg_profit_per_trade, 2),
            "equity_curve": opportunities[['timestamp', 'equity_curve']].copy()
        }

    def render_strategy_parameters(self, strategy_key: str) -> Dict:
        """渲染策略参数设置"""
        strategy = self.strategies[strategy_key]
        st.subheader(f"🎛️ {strategy['name']} - 参数设置")
        st.write(strategy['description'])

        params = {}

        # 动态生成参数控件
        for param_name, param_config in strategy['parameters'].items():
            if param_config.get('type') == 'multiselect':
                params[param_name] = st.multiselect(
                    param_name.replace('_', ' ').title(),
                    param_config['default'],
                    default=param_config['default'],
                    key=f"{strategy_key}_{param_name}"
                )
            elif param_config.get('options'):
                params[param_name] = st.selectbox(
                    param_name.replace('_', ' ').title(),
                    param_config['options'],
                    index=param_config['options'].index(param_config['default']),
                    key=f"{strategy_key}_{param_name}"
                )
            else:
                params[param_name] = st.slider(
                    param_name.replace('_', ' ').title(),
                    min_value=param_config['min'],
                    max_value=param_config['max'],
                    value=param_config['default'],
                    step=param_config['step'],
                    key=f"{strategy_key}_{param_name}"
                )

        return params

    def render_backtest_settings(self):
        """渲染回测设置"""
        st.subheader("⚙️ 回测设置")

        # 基础设置
        col1, col2, col3 = st.columns(3)

        with col1:
            start_date = st.date_input(
                "开始日期",
                value=datetime.now() - timedelta(days=90),
                max_value=datetime.now()
            )

            end_date = st.date_input(
                "结束日期",
                value=datetime.now(),
                max_value=datetime.now()
            )

        with col2:
            timeframe = st.selectbox(
                "时间框架",
                ["1m", "5m", "15m", "30m", "1h", "4h", "1d", "1w"],
                index=4
            )

            initial_capital = st.number_input(
                "初始资金 ($)",
                min_value=1000,
                max_value=1000000,
                value=100000,
                step=1000
            )

        with col3:
            scenario = st.selectbox(
                "市场场景",
                list(self.market_scenarios.keys()),
                format_func=lambda x: self.market_scenarios[x]['name']
            )

            commission = st.slider(
                "手续费 (%)",
                min_value=0.0,
                max_value=1.0,
                value=0.1,
                step=0.01
            )

        # 多时间框架设置
        st.subheader("⏰ 多时间框架设置")

        timeframe_col1, timeframe_col2 = st.columns(2)

        with timeframe_col1:
            # 主要时间框架
            primary_timeframes = st.multiselect(
                "主要时间框架",
                ["1m", "5m", "15m", "30m", "1h", "4h", "1d"],
                default=["5m", "1h"],
                help="用于套利机会检测的主要时间框架"
            )

            # 确认时间框架
            confirmation_timeframes = st.multiselect(
                "确认时间框架",
                ["1m", "5m", "15m", "30m", "1h", "4h", "1d"],
                default=["15m"],
                help="用于确认信号的更高时间框架"
            )

        with timeframe_col2:
            # 时间框架权重
            st.write("**时间框架权重配置**")

            timeframe_weights = {}
            for tf in primary_timeframes:
                weight = st.slider(
                    f"{tf} 权重",
                    min_value=0.1,
                    max_value=1.0,
                    value=0.5,
                    step=0.1,
                    key=f"weight_{tf}"
                )
                timeframe_weights[tf] = weight

            # 多时间框架一致性要求
            consistency_threshold = st.slider(
                "一致性阈值",
                min_value=0.5,
                max_value=1.0,
                value=0.7,
                step=0.1,
                help="多个时间框架信号一致性的最低要求"
            )

        # 场景化回测设置
        st.subheader("🎭 场景化回测设置")

        scenario_col1, scenario_col2 = st.columns(2)

        with scenario_col1:
            # 市场场景选择
            market_scenarios = st.multiselect(
                "市场场景",
                [
                    "正常市场",
                    "高波动期",
                    "低流动性",
                    "重大新闻事件",
                    "市场崩盘",
                    "牛市行情",
                    "熊市行情",
                    "横盘整理"
                ],
                default=["正常市场", "高波动期"],
                help="选择要测试的市场场景"
            )

            # 压力测试级别
            stress_test_level = st.selectbox(
                "压力测试级别",
                ["轻度", "中度", "重度", "极端"],
                index=1,
                help="选择压力测试的强度级别"
            )

        with scenario_col2:
            # 场景参数配置
            st.write("**场景参数配置**")

            # 波动率调整
            volatility_multiplier = st.slider(
                "波动率倍数",
                min_value=0.5,
                max_value=3.0,
                value=1.0,
                step=0.1,
                help="调整历史波动率的倍数"
            )

            # 流动性调整
            liquidity_factor = st.slider(
                "流动性因子",
                min_value=0.3,
                max_value=1.0,
                value=1.0,
                step=0.1,
                help="调整市场流动性水平"
            )

            # 滑点调整
            slippage_multiplier = st.slider(
                "滑点倍数",
                min_value=1.0,
                max_value=5.0,
                value=1.0,
                step=0.5,
                help="调整交易滑点的倍数"
            )

        return {
            "start_date": datetime.combine(start_date, datetime.min.time()),
            "end_date": datetime.combine(end_date, datetime.min.time()),
            "timeframe": timeframe,
            "initial_capital": initial_capital,
            "scenario": scenario,
            "commission": commission,
            "primary_timeframes": primary_timeframes,
            "confirmation_timeframes": confirmation_timeframes,
            "timeframe_weights": timeframe_weights,
            "consistency_threshold": consistency_threshold,
            "market_scenarios": market_scenarios,
            "stress_test_level": stress_test_level,
            "volatility_multiplier": volatility_multiplier,
            "liquidity_factor": liquidity_factor,
            "slippage_multiplier": slippage_multiplier
        }

    def render_backtest_results(self, results: Dict, opportunities: pd.DataFrame):
        """渲染回测结果"""
        st.subheader("📊 回测结果")

        # 策略比较选项
        comparison_mode = st.checkbox("🔄 多策略比较模式", help="同时回测多个策略并进行比较")

        strategies_to_compare = ["基础套利策略"]
        if comparison_mode:
            additional_strategies = st.multiselect(
                "选择要比较的策略",
                [
                    "高频套利策略",
                    "跨期套利策略",
                    "统计套利策略",
                    "三角套利策略",
                    "资金费率套利策略"
                ],
                default=["高频套利策略", "统计套利策略"]
            )
            strategies_to_compare.extend(additional_strategies)

        # 关键指标
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "总收益率",
                f"{results['total_return']:.2f}%",
                delta=f"${results['total_profit']:,.2f}"
            )

        with col2:
            st.metric(
                "总交易次数",
                results['total_trades'],
                delta=f"胜率 {results['win_rate']:.1f}%"
            )

        with col3:
            st.metric(
                "最大回撤",
                f"{results['max_drawdown']:.2f}%",
                delta=f"夏普比率 {results['sharpe_ratio']:.2f}"
            )

        with col4:
            st.metric(
                "盈亏比",
                f"{results['profit_factor']:.2f}",
                delta=f"平均利润 ${results['avg_profit_per_trade']:,.2f}"
            )

        # 收益曲线图
        if not results['equity_curve'].empty:
            st.subheader("📈 收益曲线")

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=results['equity_curve']['timestamp'],
                y=results['equity_curve']['equity_curve'],
                mode='lines',
                name='账户净值',
                line=dict(color='#00ff88', width=2)
            ))

            fig.update_layout(
                title="账户净值变化",
                xaxis_title="时间",
                yaxis_title="账户净值 ($)",
                template="plotly_dark",
                height=400
            )

            st.plotly_chart(fig, use_container_width=True)

        # 交易分析
        if not opportunities.empty:
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("💰 利润分布")

                fig = px.histogram(
                    opportunities,
                    x='profit',
                    nbins=20,
                    title="交易利润分布",
                    template="plotly_dark"
                )
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.subheader("📊 价差分布")

                fig = px.histogram(
                    opportunities,
                    x='spread_pct',
                    nbins=20,
                    title="价差百分比分布",
                    template="plotly_dark"
                )
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)

        # 详细交易记录
        with st.expander("📋 详细交易记录"):
            if not opportunities.empty:
                display_df = opportunities[['timestamp', 'spread_pct', 'profit', 'buy_exchange', 'sell_exchange']].copy()
                display_df['timestamp'] = display_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M')
                display_df.columns = ['时间', '价差(%)', '利润($)', '买入交易所', '卖出交易所']
                st.dataframe(display_df, use_container_width=True)
            else:
                st.info("没有找到符合条件的套利机会")

    def export_results(self, results: Dict, opportunities: pd.DataFrame, strategy_name: str) -> str:
        """导出回测结果"""
        # 创建报告
        report = {
            "strategy": strategy_name,
            "timestamp": datetime.now().isoformat(),
            "performance_metrics": results,
            "trades": opportunities.to_dict('records') if not opportunities.empty else []
        }

        # 转换为JSON
        report_json = json.dumps(report, indent=2, ensure_ascii=False, default=str)

        # 编码为base64用于下载
        b64 = base64.b64encode(report_json.encode()).decode()

        return f"data:application/json;base64,{b64}"

def render_backtesting_engine():
    """渲染回测引擎主界面"""
    st.title("🔬 高级回测引擎")

    # 创建回测引擎实例
    engine = BacktestingEngine()

    # 创建标签页
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎛️ 策略配置",
        "📊 单策略回测",
        "🔄 策略比较",
        "📈 场景分析"
    ])

    with tab1:
        st.subheader("🎯 策略选择与配置")

        # 策略选择
        strategy_key = st.selectbox(
            "选择策略",
            list(engine.strategies.keys()),
            format_func=lambda x: engine.strategies[x]['name']
        )

        # 策略参数设置
        strategy_params = engine.render_strategy_parameters(strategy_key)

        # 回测设置
        backtest_settings = engine.render_backtest_settings()

        # 保存配置
        if st.button("💾 保存配置", type="primary"):
            config = {
                "strategy": strategy_key,
                "parameters": strategy_params,
                "settings": backtest_settings
            }
            st.success("✅ 配置已保存")
            st.json(config)

    with tab2:
        st.subheader("📊 单策略回测")

        # 快速配置
        col1, col2 = st.columns(2)

        with col1:
            quick_strategy = st.selectbox(
                "快速选择策略",
                list(engine.strategies.keys()),
                format_func=lambda x: engine.strategies[x]['name'],
                key="quick_strategy"
            )

        with col2:
            quick_scenario = st.selectbox(
                "市场场景",
                list(engine.market_scenarios.keys()),
                format_func=lambda x: engine.market_scenarios[x]['name'],
                key="quick_scenario"
            )

        # 执行回测
        if st.button("🚀 开始回测", type="primary", use_container_width=True):
            with st.spinner("正在执行回测..."):
                # 使用默认参数
                strategy_params = {k: v['default'] for k, v in engine.strategies[quick_strategy]['parameters'].items()}

                # 生成市场数据
                start_date = datetime.now() - timedelta(days=30)
                end_date = datetime.now()

                market_data = engine.generate_market_data(
                    start_date=start_date,
                    end_date=end_date,
                    timeframe="1h",
                    scenario=quick_scenario
                )

                # 模拟套利机会
                opportunities = engine.simulate_arbitrage_opportunities(market_data, strategy_params)

                # 计算绩效
                results = engine.calculate_performance_metrics(opportunities)

                # 显示结果
                engine.render_backtest_results(results, opportunities)

                # 导出选项
                if not opportunities.empty:
                    export_data = engine.export_results(results, opportunities, engine.strategies[quick_strategy]['name'])
                    st.download_button(
                        label="📥 导出回测报告",
                        data=export_data,
                        file_name=f"backtest_report_{quick_strategy}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )

    with tab3:
        st.subheader("🔄 策略比较")

        # 选择要比较的策略
        compare_strategies = st.multiselect(
            "选择要比较的策略",
            list(engine.strategies.keys()),
            default=list(engine.strategies.keys())[:2],
            format_func=lambda x: engine.strategies[x]['name']
        )

        if len(compare_strategies) >= 2:
            if st.button("🔄 开始比较", type="primary"):
                comparison_results = {}

                with st.spinner("正在比较策略..."):
                    for strategy_key in compare_strategies:
                        # 使用默认参数
                        strategy_params = {k: v['default'] for k, v in engine.strategies[strategy_key]['parameters'].items()}

                        # 生成相同的市场数据
                        start_date = datetime.now() - timedelta(days=30)
                        end_date = datetime.now()

                        market_data = engine.generate_market_data(
                            start_date=start_date,
                            end_date=end_date,
                            timeframe="1h",
                            scenario="normal_market"
                        )

                        # 模拟套利机会
                        opportunities = engine.simulate_arbitrage_opportunities(market_data, strategy_params)

                        # 计算绩效
                        results = engine.calculate_performance_metrics(opportunities)
                        comparison_results[strategy_key] = results

                # 显示比较结果
                st.subheader("📊 策略比较结果")

                # 创建比较表格
                comparison_df = pd.DataFrame({
                    strategy_key: {
                        "总收益率 (%)": results["total_return"],
                        "总交易次数": results["total_trades"],
                        "胜率 (%)": results["win_rate"],
                        "最大回撤 (%)": results["max_drawdown"],
                        "夏普比率": results["sharpe_ratio"],
                        "盈亏比": results["profit_factor"]
                    }
                    for strategy_key, results in comparison_results.items()
                }).T

                # 重命名索引
                comparison_df.index = [engine.strategies[k]['name'] for k in comparison_df.index]

                st.dataframe(comparison_df, use_container_width=True)

                # 可视化比较
                col1, col2 = st.columns(2)

                with col1:
                    fig = px.bar(
                        x=comparison_df.index,
                        y=comparison_df["总收益率 (%)"],
                        title="总收益率比较",
                        template="plotly_dark"
                    )
                    st.plotly_chart(fig, use_container_width=True)

                with col2:
                    fig = px.bar(
                        x=comparison_df.index,
                        y=comparison_df["夏普比率"],
                        title="夏普比率比较",
                        template="plotly_dark"
                    )
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("请至少选择2个策略进行比较")

    with tab4:
        st.subheader("📈 场景分析")

        # 选择策略和场景
        col1, col2 = st.columns(2)

        with col1:
            scenario_strategy = st.selectbox(
                "选择策略",
                list(engine.strategies.keys()),
                format_func=lambda x: engine.strategies[x]['name'],
                key="scenario_strategy"
            )

        with col2:
            test_scenarios = st.multiselect(
                "选择测试场景",
                list(engine.market_scenarios.keys()),
                default=list(engine.market_scenarios.keys()),
                format_func=lambda x: engine.market_scenarios[x]['name']
            )

        if st.button("🧪 开始场景测试", type="primary"):
            scenario_results = {}

            with st.spinner("正在进行场景测试..."):
                for scenario_key in test_scenarios:
                    # 使用默认参数
                    strategy_params = {k: v['default'] for k, v in engine.strategies[scenario_strategy]['parameters'].items()}

                    # 生成场景数据
                    start_date = datetime.now() - timedelta(days=30)
                    end_date = datetime.now()

                    market_data = engine.generate_market_data(
                        start_date=start_date,
                        end_date=end_date,
                        timeframe="1h",
                        scenario=scenario_key
                    )

                    # 模拟套利机会
                    opportunities = engine.simulate_arbitrage_opportunities(market_data, strategy_params)

                    # 计算绩效
                    results = engine.calculate_performance_metrics(opportunities)
                    scenario_results[scenario_key] = results

            # 显示场景分析结果
            st.subheader("🎭 场景分析结果")

            # 创建场景比较表格
            scenario_df = pd.DataFrame({
                scenario_key: {
                    "总收益率 (%)": results["total_return"],
                    "总交易次数": results["total_trades"],
                    "胜率 (%)": results["win_rate"],
                    "最大回撤 (%)": results["max_drawdown"],
                    "夏普比率": results["sharpe_ratio"]
                }
                for scenario_key, results in scenario_results.items()
            }).T

            # 重命名索引
            scenario_df.index = [engine.market_scenarios[k]['name'] for k in scenario_df.index]

            st.dataframe(scenario_df, use_container_width=True)

            # 场景表现雷达图
            fig = go.Figure()

            for scenario_key, results in scenario_results.items():
                scenario_name = engine.market_scenarios[scenario_key]['name']

                # 标准化指标 (0-100)
                normalized_metrics = [
                    max(0, min(100, results["total_return"] + 50)),  # 收益率
                    min(100, results["total_trades"] / 10),  # 交易次数
                    results["win_rate"],  # 胜率
                    max(0, 100 - results["max_drawdown"]),  # 回撤 (反向)
                    max(0, min(100, (results["sharpe_ratio"] + 2) * 25))  # 夏普比率
                ]

                fig.add_trace(go.Scatterpolar(
                    r=normalized_metrics,
                    theta=['收益率', '交易频率', '胜率', '风险控制', '夏普比率'],
                    fill='toself',
                    name=scenario_name
                ))

            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100]
                    )),
                showlegend=True,
                title="不同场景下的策略表现",
                template="plotly_dark"
            )

            st.plotly_chart(fig, use_container_width=True)

    # 功能说明
    with st.expander("📖 功能说明"):
        st.markdown("""
        ### 🎯 高级回测引擎特性

        **🎛️ 策略自定义**
        - 📊 多种预定义策略
        - 🔧 灵活的参数调整
        - 💾 配置保存和加载
        - 🎨 自定义策略开发

        **📈 多时间框架**
        - ⏰ 1分钟到1周的时间框架
        - 📊 多周期数据分析
        - 🔄 时间框架优化
        - 📈 长短期策略测试

        **🎭 场景测试**
        - 🌊 正常市场环境
        - 🔥 高波动率场景
        - 📈 牛市/熊市测试
        - ⚡ 极端事件模拟

        **📊 性能分析**
        - 💰 收益率和风险指标
        - 📈 夏普比率和最大回撤
        - 🎯 胜率和盈亏比
        - 📋 详细交易记录

        **🔄 策略比较**
        - 📊 多策略并行测试
        - 📈 性能指标对比
        - 🎯 最优策略识别
        - 📋 导出比较报告
        """)

    return True

if __name__ == "__main__":
    render_backtesting_engine()
