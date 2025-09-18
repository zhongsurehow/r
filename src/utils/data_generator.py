"""
统一数据生成工具
整合所有重复的数据生成逻辑
"""

import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple, Optional
import streamlit as st

class DataGenerator:
    """统一数据生成器"""

    # 常用的交易所和货币列表
    EXCHANGES = ['Binance', 'OKX', 'Huobi', 'KuCoin', 'Bybit', 'Gate.io', 'Coinbase', 'Kraken']
    CURRENCIES = ['BTC', 'ETH', 'BNB', 'ADA', 'SOL', 'DOT', 'MATIC', 'AVAX', 'LINK', 'UNI']
    TRADING_PAIRS = [f"{curr}/USDT" for curr in CURRENCIES]

    def __init__(self, seed: Optional[int] = None):
        """初始化数据生成器"""
        if seed:
            random.seed(seed)
            np.random.seed(seed)

    @staticmethod
    @st.cache_data(ttl=300)
    def generate_price_data(symbol: str = "BTC", days: int = 30, base_price: float = 45000) -> pd.DataFrame:
        """
        生成价格数据

        Args:
            symbol: 交易对符号
            days: 天数
            base_price: 基础价格

        Returns:
            包含OHLCV数据的DataFrame
        """
        dates = pd.date_range(end=datetime.now(), periods=days * 24, freq='H')

        # 生成价格走势
        returns = np.random.normal(0, 0.02, len(dates))
        prices = [base_price]

        for ret in returns[1:]:
            new_price = prices[-1] * (1 + ret)
            prices.append(max(new_price, base_price * 0.5))  # 防止价格过低

        # 生成OHLCV数据
        data = []
        for i, (date, price) in enumerate(zip(dates, prices)):
            volatility = random.uniform(0.01, 0.05)
            high = price * (1 + volatility)
            low = price * (1 - volatility)
            open_price = prices[i-1] if i > 0 else price
            close_price = price
            volume = random.uniform(1000000, 10000000)

            data.append({
                'timestamp': date,
                'symbol': symbol,
                'open': open_price,
                'high': high,
                'low': low,
                'close': close_price,
                'volume': volume
            })

        return pd.DataFrame(data)

    @staticmethod
    @st.cache_data(ttl=60)
    def generate_real_time_data(symbols: List[str] = None) -> pd.DataFrame:
        """
        生成实时数据

        Args:
            symbols: 交易对列表

        Returns:
            实时数据DataFrame
        """
        if symbols is None:
            symbols = DataGenerator.TRADING_PAIRS[:10]

        data = []
        for symbol in symbols:
            base_price = random.uniform(0.1, 50000)
            change_24h = random.uniform(-10, 10)
            volume_24h = random.uniform(1000000, 100000000)

            data.append({
                'symbol': symbol,
                'price': base_price,
                'change_24h': change_24h,
                'volume_24h': volume_24h,
                'high_24h': base_price * (1 + abs(change_24h) / 100),
                'low_24h': base_price * (1 - abs(change_24h) / 100),
                'timestamp': datetime.now()
            })

        return pd.DataFrame(data)

    @staticmethod
    @st.cache_data(ttl=300)
    def generate_arbitrage_opportunities(count: int = 50) -> pd.DataFrame:
        """
        生成套利机会数据

        Args:
            count: 生成数量

        Returns:
            套利机会DataFrame
        """
        data = []

        for _ in range(count):
            currency = random.choice(DataGenerator.CURRENCIES)
            buy_exchange = random.choice(DataGenerator.EXCHANGES)
            sell_exchange = random.choice([ex for ex in DataGenerator.EXCHANGES if ex != buy_exchange])

            buy_price = random.uniform(100, 50000)
            price_diff_pct = random.uniform(0.1, 5.0)
            sell_price = buy_price * (1 + price_diff_pct / 100)

            profit_margin = (sell_price - buy_price) / buy_price * 100
            volume = random.uniform(1000, 100000)

            data.append({
                'currency': currency,
                'buy_exchange': buy_exchange,
                'sell_exchange': sell_exchange,
                'buy_price': buy_price,
                'sell_price': sell_price,
                'price_difference': sell_price - buy_price,
                'profit_margin': profit_margin,
                'volume': volume,
                'timestamp': datetime.now()
            })

        return pd.DataFrame(data)

    @staticmethod
    @st.cache_data(ttl=300)
    def generate_market_health_data() -> Dict[str, Any]:
        """
        生成市场健康度数据

        Returns:
            市场健康度数据字典
        """
        exchanges = DataGenerator.EXCHANGES[:6]

        health_data = {}
        for exchange in exchanges:
            health_data[exchange] = {
                'status': random.choice(['正常', '延迟', '异常']),
                'latency': random.uniform(10, 200),
                'uptime': random.uniform(95, 100),
                'api_calls': random.randint(1000, 10000),
                'error_rate': random.uniform(0, 5),
                'last_update': datetime.now()
            }

        return health_data

    @staticmethod
    @st.cache_data(ttl=300)
    def generate_correlation_matrix(symbols: List[str] = None, days: int = 30) -> pd.DataFrame:
        """
        生成相关性矩阵数据

        Args:
            symbols: 交易对列表
            days: 天数

        Returns:
            相关性矩阵DataFrame
        """
        if symbols is None:
            symbols = DataGenerator.CURRENCIES[:10]

        # 生成价格数据
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        price_data = {}

        for symbol in symbols:
            returns = np.random.normal(0, 0.02, days)
            prices = np.cumprod(1 + returns) * random.uniform(100, 50000)
            price_data[symbol] = prices

        df = pd.DataFrame(price_data, index=dates)
        return df.corr()

    @staticmethod
    @st.cache_data(ttl=60)
    def generate_network_latency_data(exchanges: List[str] = None, hours: int = 24) -> pd.DataFrame:
        """
        生成网络延迟数据

        Args:
            exchanges: 交易所列表
            hours: 小时数

        Returns:
            网络延迟DataFrame
        """
        if exchanges is None:
            exchanges = DataGenerator.EXCHANGES[:4]

        base_time = datetime.now() - timedelta(hours=hours)
        timestamps = [base_time + timedelta(minutes=i) for i in range(hours * 60)]

        data = []
        for exchange in exchanges:
            # 向量化生成延迟数据
            hours_array = np.array([ts.hour for ts in timestamps])
            base_latencies = 30 + 20 * np.sin(2 * np.pi * hours_array / 24)
            noise = np.random.normal(0, 10, len(timestamps))
            latencies = np.maximum(5, base_latencies + noise)

            for timestamp, latency in zip(timestamps, latencies):
                data.append({
                    'timestamp': timestamp,
                    'exchange': exchange,
                    'latency': latency
                })

        return pd.DataFrame(data)

    @staticmethod
    @st.cache_data(ttl=300)
    def generate_portfolio_data(symbols: List[str] = None) -> Dict[str, Any]:
        """
        生成投资组合数据

        Args:
            symbols: 交易对列表

        Returns:
            投资组合数据字典
        """
        if symbols is None:
            symbols = DataGenerator.CURRENCIES[:8]

        total_value = 100000  # 总价值
        allocations = np.random.dirichlet(np.ones(len(symbols))) * total_value

        portfolio = {}
        for symbol, allocation in zip(symbols, allocations):
            price = random.uniform(0.1, 50000)
            quantity = allocation / price
            change_24h = random.uniform(-10, 10)

            portfolio[symbol] = {
                'quantity': quantity,
                'price': price,
                'value': allocation,
                'change_24h': change_24h,
                'allocation_pct': (allocation / total_value) * 100
            }

        return portfolio

    @staticmethod
    @st.cache_data(ttl=300)
    def generate_kpi_data() -> Dict[str, Any]:
        """
        生成KPI数据

        Returns:
            KPI数据字典
        """
        return {
            'total_profit': random.uniform(10000, 100000),
            'daily_profit': random.uniform(100, 5000),
            'success_rate': random.uniform(60, 95),
            'active_opportunities': random.randint(10, 100),
            'total_volume': random.uniform(1000000, 10000000),
            'avg_profit_margin': random.uniform(0.5, 3.0),
            'risk_score': random.uniform(1, 10),
            'sharpe_ratio': random.uniform(0.5, 2.5)
        }

    @staticmethod
    def generate_time_series_data(
        start_date: datetime,
        end_date: datetime,
        freq: str = 'H',
        base_value: float = 100,
        volatility: float = 0.02
    ) -> pd.DataFrame:
        """
        生成时间序列数据

        Args:
            start_date: 开始日期
            end_date: 结束日期
            freq: 频率
            base_value: 基础值
            volatility: 波动率

        Returns:
            时间序列DataFrame
        """
        dates = pd.date_range(start=start_date, end=end_date, freq=freq)
        returns = np.random.normal(0, volatility, len(dates))
        values = [base_value]

        for ret in returns[1:]:
            new_value = values[-1] * (1 + ret)
            values.append(max(new_value, base_value * 0.1))

        return pd.DataFrame({
            'timestamp': dates,
            'value': values[:len(dates)]
        })

# 全局数据生成器实例
data_generator = DataGenerator()

# 便利函数
def get_mock_price_data(symbol: str = "BTC", days: int = 30) -> pd.DataFrame:
    """获取模拟价格数据"""
    return data_generator.generate_price_data(symbol, days)

def get_mock_real_time_data(count: int = 10) -> pd.DataFrame:
    """获取模拟实时数据"""
    symbols = DataGenerator.TRADING_PAIRS[:count]
    return data_generator.generate_real_time_data(symbols)

def get_mock_arbitrage_data(count: int = 50) -> pd.DataFrame:
    """获取模拟套利数据"""
    return data_generator.generate_arbitrage_opportunities(count)
