"""
套利机会页面 - 专业套利交易系统
提供实时套利机会分析、市场健康监控、相关性分析和一键套利功能
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import random
import sys
import os
from typing import Dict, List, Tuple, Optional
import threading
import time

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from components.execution_monitor import render_execution_monitor, render_risk_dashboard
from components.network_monitor import render_network_monitor
from components.main_console import render_main_console
from components.market_health_dashboard import render_market_health_dashboard
from components.correlation_matrix import render_correlation_matrix_dashboard
from components.multi_exchange_comparison import render_multi_exchange_comparison
from components.historical_arbitrage_tracker import render_historical_arbitrage_tracker
from components.one_click_arbitrage import render_one_click_arbitrage
from components.realtime_risk_management import render_realtime_risk_management
from providers.real_data_service import real_data_service
from src.utils.dependency_manager import check_ccxt
import asyncio

# 配置常量
CURRENCIES = [
    "BTC", "ETH", "BNB", "XRP", "ADA", "SOL", "DOGE", "DOT", "MATIC", "SHIB",
    "AVAX", "LTC", "UNI", "LINK", "ATOM", "XLM", "BCH", "ALGO", "VET", "ICP",
    "FIL", "TRX", "ETC", "THETA", "XMR", "HBAR", "NEAR", "FLOW", "EGLD", "XTZ",
    "MANA", "SAND", "AXS", "CHZ", "ENJ", "BAT", "ZIL", "HOT", "IOTA", "QTUM",
    "OMG", "ZRX", "COMP", "MKR", "SNX", "SUSHI", "YFI", "AAVE", "CRV", "1INCH",
    "RUNE", "LUNA", "UST", "KLAY", "FTT", "HNT", "WAVES", "KSM", "DASH", "ZEC",
    "DCR", "RVN", "DGB", "SC", "BTG", "NANO", "ICX", "ONT", "LSK", "STEEM",
    "ARK", "STRAX", "NEM", "XEM", "MAID", "STORJ", "SIA", "GNT", "REP", "ANT",
    "MODE", "TAVA", "SUIAI", "LIVE", "AIC", "GEL", "PEPE", "FLOKI", "BONK", "WIF",
    "BOME", "SLERF", "MYRO", "POPCAT", "MOODENG", "GOAT", "PNUT", "ACT", "NEIRO", "TURBO"
]

EXCHANGES = ["Binance", "OKX", "Huobi", "KuCoin", "Gate.io", "Bybit", "Coinbase", "Kraken"]

NETWORK_FEATURES = {
    'ETH': {'avg_latency': 60, 'fee_level': '高', 'success_rate': 98},
    'BSC': {'avg_latency': 15, 'fee_level': '低', 'success_rate': 99},
    'TRX': {'avg_latency': 10, 'fee_level': '极低', 'success_rate': 97},
    'MATIC': {'avg_latency': 8, 'fee_level': '极低', 'success_rate': 99},
    'AVAX': {'avg_latency': 12, 'fee_level': '低', 'success_rate': 98},
    'SOL': {'avg_latency': 5, 'fee_level': '极低', 'success_rate': 96},
    'ATOM': {'avg_latency': 20, 'fee_level': '中', 'success_rate': 97},
    'DOT': {'avg_latency': 25, 'fee_level': '中', 'success_rate': 98}
}

QUICK_FILTERS = {
    "全部机会": {},
    "高收益低风险": {"min_profit": 2.0, "risk_level": "低风险", "executable_only": True},
    "快速执行": {"max_latency": 5, "difficulty": "简单", "executable_only": True},
    "高成功率": {"min_success_rate": 95, "executable_only": True},
    "简单操作": {"difficulty": "简单", "liquidity": "高", "executable_only": True}
}


def setup_page_config():
    """设置页面配置"""
    st.set_page_config(
        page_title="套利机会",
        page_icon="💰",
        layout="wide",
        initial_sidebar_state="expanded"
    )


def generate_arbitrage_opportunity(currency: str, buy_exchange: str, sell_exchange: str) -> Dict:
    """生成单个套利机会数据"""
    # 基础价格和价差
    base_price = random.uniform(0.1, 50000)
    price_diff = random.uniform(0.1, 4.0)

    # 网络选择
    networks = list(NETWORK_FEATURES.keys())
    withdraw_network = random.choice(networks)
    deposit_network = random.choice(networks)
    unified_network = withdraw_network if withdraw_network == deposit_network else "-"

    # 计算专业指标
    network_info = NETWORK_FEATURES.get(withdraw_network, NETWORK_FEATURES['ETH'])

    execution_difficulty = random.choices(
        ["🟢 简单", "🟡 中等", "🔴 困难"],
        weights=[0.4, 0.4, 0.2]
    )[0]

    success_rate = max(70, network_info['success_rate'] + random.gauss(0, 5))
    network_latency = max(1, network_info['avg_latency'] + random.gauss(0, 10))
    estimated_time = network_latency + random.uniform(30, 180)

    liquidity = random.choices(
        ["🟢 高", "🟡 中", "🔴 低"],
        weights=[0.3, 0.5, 0.2]
    )[0]

    risk_level = random.choices(
        ["🟢 低风险", "🟡 中风险", "🔴 高风险"],
        weights=[0.3, 0.5, 0.2]
    )[0]

    return {
        "币种": currency,
        "买入平台": buy_exchange,
        "卖出平台": sell_exchange,
        "买入价格": f"${base_price:.4f}",
        "卖出价格": f"${base_price * (1 + price_diff/100):.4f}",
        "价格差": f"{price_diff:.2f}%",
        "提现网络": withdraw_network,
        "充值网络": deposit_network,
        "充提合一": unified_network,
        "执行难度": execution_difficulty,
        "成功率": f"{success_rate:.1f}%",
        "网络延迟": f"{network_latency:.0f}秒",
        "预估时间": f"{estimated_time:.0f}秒",
        "流动性": liquidity,
        "风险等级": risk_level,
        "手续费等级": network_info['fee_level']
    }


@st.cache_data(ttl=60)
def is_cache_valid(cache_time, ttl_minutes=5):
    """检查缓存是否有效"""
    if cache_time is None:
        return False
    return (datetime.now() - cache_time).total_seconds() < ttl_minutes * 60

@st.cache_data(ttl=300, show_spinner=False)  # 缓存5分钟，不显示默认spinner
def get_real_arbitrage_opportunities_from_ccxt():
    """从CCXT获取真实套利机会数据 - 优化版本"""
    try:
        # 检查CCXT是否可用
        if not check_ccxt():
            return []
            
        # 使用线程池来避免阻塞主线程
        def fetch_data():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(
                    real_data_service.get_real_arbitrage_opportunities()
                )
            finally:
                loop.close()
        
        # 设置超时时间，避免长时间等待
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(fetch_data)
            try:
                opportunities_data = future.result(timeout=10)  # 10秒超时
            except concurrent.futures.TimeoutError:
                st.warning("⏱️ 数据获取超时，使用缓存数据")
                return []
        
        # 转换数据格式以匹配UI显示
        opportunities = []
        for opp in opportunities_data:
            opportunities.append({
                'symbol': opp.symbol.replace('/USDT', '').replace('/USD', ''),
                'buy_exchange': opp.buy_exchange.title(),
                'sell_exchange': opp.sell_exchange.title(),
                'buy_price': opp.buy_price,
                'sell_price': opp.sell_price,
                'profit_margin': opp.profit_margin,
                'available_volume': opp.available_volume,
                'risk_score': opp.risk_score,
                'estimated_time': opp.estimated_time
            })
        
        return opportunities
        
    except Exception as e:
        print(f"获取CCXT数据失败: {e}")
        return []

def get_optimized_arbitrage_data() -> pd.DataFrame:
    """优化的套利数据获取函数 - 立即返回数据，后台更新"""
    try:
        # 立即返回静态数据，确保界面不阻塞
        if 'arbitrage_data_cache' not in st.session_state:
            st.session_state.arbitrage_data_cache = get_static_data()
            st.session_state.arbitrage_cache_time = datetime.now()
        
        # 检查缓存是否有效（延长缓存时间以减少刷新频率）
        if (st.session_state.get('arbitrage_data_cache') is not None and 
            is_cache_valid(st.session_state.arbitrage_cache_time, ttl_minutes=10)):
            return st.session_state.arbitrage_data_cache
        
        # 后台尝试获取真实数据（不阻塞界面）
        real_opportunities = get_real_arbitrage_opportunities_from_ccxt()
        
        if real_opportunities:
            # 转换真实数据为表格格式
            data = []
            for opp in real_opportunities:
                # 计算网络信息
                networks = list(NETWORK_FEATURES.keys())
                withdraw_network = random.choice(networks)
                deposit_network = random.choice(networks)
                unified_network = withdraw_network if withdraw_network == deposit_network else "-"
                
                # 获取网络特性
                network_info = NETWORK_FEATURES.get(withdraw_network, NETWORK_FEATURES['ETH'])
                
                # 根据风险评分确定执行难度
                if opp['risk_score'] <= 3:
                    execution_difficulty = "🟢 简单"
                    risk_level = "🟢 低风险"
                    liquidity = "🟢 高"
                elif opp['risk_score'] <= 6:
                    execution_difficulty = "🟡 中等"
                    risk_level = "🟡 中风险"
                    liquidity = "🟡 中"
                else:
                    execution_difficulty = "🔴 困难"
                    risk_level = "🔴 高风险"
                    liquidity = "🔴 低"
                
                success_rate = max(70, network_info['success_rate'] + random.gauss(0, 5))
                network_latency = max(1, network_info['avg_latency'] + random.gauss(0, 10))
                
                data.append({
                    "币种": opp['symbol'],
                    "买入平台": opp['buy_exchange'],
                    "卖出平台": opp['sell_exchange'],
                    "买入价格": f"${opp['buy_price']:.4f}",
                    "卖出价格": f"${opp['sell_price']:.4f}",
                    "价格差": f"{opp['profit_margin']:.2f}%",
                    "提现网络": withdraw_network,
                    "充值网络": deposit_network,
                    "充提合一": unified_network,
                    "执行难度": execution_difficulty,
                    "成功率": f"{success_rate:.1f}%",
                    "网络延迟": f"{network_latency:.0f}秒",
                    "预估时间": f"{opp['estimated_time']:.0f}秒",
                    "流动性": liquidity,
                    "风险等级": risk_level,
                    "手续费等级": network_info['fee_level']
                })
            
            df = pd.DataFrame(data)
            
            # 缓存数据
            st.session_state.arbitrage_data_cache = df
            st.session_state.arbitrage_cache_time = datetime.now()
            
            return df
        else:
            # 使用备用数据
            df = generate_fallback_data()
            st.session_state.arbitrage_data_cache = df
            st.session_state.arbitrage_cache_time = datetime.now()
            return df
                
    except Exception as e:
        st.session_state.arbitrage_error = str(e)
        # 返回备用数据
        return generate_fallback_data()

# 预生成的静态数据，确保立即显示
STATIC_ARBITRAGE_DATA = [
    {"币种": "BTC", "买入平台": "Binance", "卖出平台": "OKX", "买入价格": "$43,250.00", "卖出价格": "$43,680.50", "价格差": "1.00%", "提现网络": "BTC", "充值网络": "BTC", "充提合一": "BTC", "执行难度": "🟢 简单", "成功率": "95.2%", "网络延迟": "45秒", "预估时间": "120秒", "流动性": "🟢 高", "风险等级": "🟢 低风险", "手续费等级": "低"},
    {"币种": "ETH", "买入平台": "KuCoin", "卖出平台": "Bybit", "买入价格": "$2,650.00", "卖出价格": "$2,703.50", "价格差": "2.02%", "提现网络": "ETH", "充值网络": "ETH", "充提合一": "ETH", "执行难度": "🟡 中等", "成功率": "88.7%", "网络延迟": "60秒", "预估时间": "180秒", "流动性": "🟢 高", "风险等级": "🟡 中风险", "手续费等级": "中"},
    {"币种": "BNB", "买入平台": "Gate.io", "卖出平台": "Binance", "买入价格": "$315.20", "卖出价格": "$321.45", "价格差": "1.98%", "提现网络": "BSC", "充值网络": "BSC", "充提合一": "BSC", "执行难度": "🟢 简单", "成功率": "92.1%", "网络延迟": "25秒", "预估时间": "90秒", "流动性": "🟡 中", "风险等级": "🟢 低风险", "手续费等级": "低"},
    {"币种": "SOL", "买入平台": "OKX", "卖出平台": "KuCoin", "买入价格": "$98.50", "卖出价格": "$101.20", "价格差": "2.74%", "提现网络": "SOL", "充值网络": "SOL", "充提合一": "SOL", "执行难度": "🟡 中等", "成功率": "85.3%", "网络延迟": "35秒", "预估时间": "150秒", "流动性": "🟡 中", "风险等级": "🟡 中风险", "手续费等级": "低"},
    {"币种": "MATIC", "买入平台": "Bybit", "卖出平台": "Gate.io", "买入价格": "$0.8520", "卖出价格": "$0.8745", "价格差": "2.64%", "提现网络": "POLYGON", "充值网络": "POLYGON", "充提合一": "POLYGON", "执行难度": "🟢 简单", "成功率": "90.8%", "网络延迟": "20秒", "预估时间": "75秒", "流动性": "🟡 中", "风险等级": "🟢 低风险", "手续费等级": "低"}
]

def get_static_data():
    """获取静态数据，立即返回"""
    return pd.DataFrame(STATIC_ARBITRAGE_DATA)

# 初始化session state用于数据缓存和加载状态
def initialize_data_cache():
    """初始化数据缓存"""
    if 'arbitrage_data_cache' not in st.session_state:
        st.session_state.arbitrage_data_cache = get_static_data()  # 立即设置静态数据
    if 'arbitrage_cache_time' not in st.session_state:
        st.session_state.arbitrage_cache_time = datetime.now()
    if 'arbitrage_loading' not in st.session_state:
        st.session_state.arbitrage_loading = False
    if 'arbitrage_error' not in st.session_state:
        st.session_state.arbitrage_error = None

def get_immediate_arbitrage_data() -> pd.DataFrame:
    """立即返回静态数据，不阻塞界面"""
    # 直接返回静态数据，确保立即显示
    return get_static_data()

def generate_arbitrage_data() -> pd.DataFrame:
    """生成完整的套利数据 - 使用优化版本"""
    return get_optimized_arbitrage_data()


def generate_fallback_data() -> pd.DataFrame:
    """生成备用数据（当无法获取真实数据时使用）"""
    try:
        # 生成少量高质量的示例数据
        num_opportunities = 20
        
        # 使用主要交易对和交易所
        main_currencies = ["BTC", "ETH", "BNB", "ADA", "SOL", "MATIC", "DOT", "AVAX"]
        main_exchanges = ["Binance", "OKX", "Bybit", "KuCoin", "Gate.io"]
        
        data = []
        for i in range(num_opportunities):
            currency = random.choice(main_currencies)
            buy_exchange = random.choice(main_exchanges)
            sell_exchange = random.choice([ex for ex in main_exchanges if ex != buy_exchange])
            
            opportunity = generate_arbitrage_opportunity(currency, buy_exchange, sell_exchange)
            data.append(opportunity)
        
        return pd.DataFrame(data)
    
    except Exception as e:
        st.error(f"生成备用数据失败: {str(e)}")
        return pd.DataFrame()


def apply_quick_filter(df: pd.DataFrame, filter_name: str) -> pd.DataFrame:
    """应用快速筛选"""
    if filter_name not in QUICK_FILTERS:
        return df

    filter_config = QUICK_FILTERS[filter_name]
    filtered_df = df.copy()

    # 转换数值列
    filtered_df["价格差_数值"] = filtered_df["价格差"].str.rstrip("%").astype(float)
    filtered_df["成功率_数值"] = filtered_df["成功率"].str.rstrip("%").astype(float)
    filtered_df["网络延迟_数值"] = filtered_df["网络延迟"].str.rstrip("秒").astype(float)

    # 应用筛选条件
    if "min_profit" in filter_config:
        filtered_df = filtered_df[filtered_df["价格差_数值"] >= filter_config["min_profit"]]

    if "risk_level" in filter_config:
        filtered_df = filtered_df[filtered_df["风险等级"].str.contains(filter_config["risk_level"])]

    if "max_latency" in filter_config:
        filtered_df = filtered_df[filtered_df["网络延迟_数值"] <= filter_config["max_latency"]]

    if "difficulty" in filter_config:
        filtered_df = filtered_df[filtered_df["执行难度"].str.contains(filter_config["difficulty"])]

    if "min_success_rate" in filter_config:
        filtered_df = filtered_df[filtered_df["成功率_数值"] >= filter_config["min_success_rate"]]

    if "liquidity" in filter_config:
        filtered_df = filtered_df[filtered_df["流动性"].str.contains(filter_config["liquidity"])]

    if filter_config.get("executable_only", False):
        filtered_df = filtered_df[filtered_df["充提合一"] != "-"]

    return filtered_df


def render_sidebar_filters(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
    """渲染侧边栏筛选器"""
    st.sidebar.header("🔍 智能筛选")

    # 快速筛选
    st.sidebar.subheader("⚡ 快速筛选")
    quick_filter = st.sidebar.selectbox(
        "选择预设筛选",
        list(QUICK_FILTERS.keys()),
        index=0
    )

    st.sidebar.markdown("---")

    # 基础筛选
    st.sidebar.subheader("📊 基础条件")

    min_diff = st.sidebar.slider("最小价格差 (%)", 0.0, 5.0, 0.0, 0.1)
    max_diff = st.sidebar.slider("最大价格差 (%)", 0.0, 5.0, 5.0, 0.1)

    exchanges = sorted(list(set(df["买入平台"].tolist() + df["卖出平台"].tolist())))
    selected_exchanges = st.sidebar.multiselect("选择交易所", exchanges, default=exchanges)

    networks = sorted(df["充提合一"].unique().tolist())
    selected_networks = st.sidebar.multiselect("选择网络", networks, default=networks)

    search_currency = st.sidebar.text_input("搜索币种", "").upper()

    st.sidebar.markdown("---")

    # 专业筛选
    st.sidebar.subheader("🎯 专业筛选")

    difficulty_options = ["🟢 简单", "🟡 中等", "🔴 困难"]
    selected_difficulty = st.sidebar.multiselect("执行难度", difficulty_options, default=difficulty_options)

    min_success_rate = st.sidebar.slider("最低成功率 (%)", 0, 100, 0, 5)

    risk_options = ["🟢 低风险", "🟡 中风险", "🔴 高风险"]
    selected_risk = st.sidebar.multiselect("风险等级", risk_options, default=risk_options)

    liquidity_options = ["🟢 高", "🟡 中", "🔴 低"]
    selected_liquidity = st.sidebar.multiselect("流动性要求", liquidity_options, default=liquidity_options)

    max_latency = st.sidebar.slider("最大网络延迟 (秒)", 1, 60, 60, 1)

    only_executable = st.sidebar.checkbox("只显示可执行机会", value=False)

    # 应用筛选
    filtered_df = apply_quick_filter(df, quick_filter)

    # 应用基础筛选
    if "价格差_数值" not in filtered_df.columns:
        filtered_df["价格差_数值"] = filtered_df["价格差"].str.rstrip("%").astype(float)
        filtered_df["成功率_数值"] = filtered_df["成功率"].str.rstrip("%").astype(float)
        filtered_df["网络延迟_数值"] = filtered_df["网络延迟"].str.rstrip("秒").astype(float)

    filtered_df = filtered_df[
        (filtered_df["价格差_数值"] >= min_diff) &
        (filtered_df["价格差_数值"] <= max_diff) &
        (filtered_df["买入平台"].isin(selected_exchanges)) &
        (filtered_df["卖出平台"].isin(selected_exchanges)) &
        (filtered_df["充提合一"].isin(selected_networks))
    ]

    # 应用专业筛选
    if search_currency:
        filtered_df = filtered_df[filtered_df["币种"].str.contains(search_currency)]

    if selected_difficulty:
        filtered_df = filtered_df[filtered_df["执行难度"].isin(selected_difficulty)]

    if min_success_rate > 0:
        filtered_df = filtered_df[filtered_df["成功率_数值"] >= min_success_rate]

    if selected_risk:
        filtered_df = filtered_df[filtered_df["风险等级"].isin(selected_risk)]

    if selected_liquidity:
        filtered_df = filtered_df[filtered_df["流动性"].isin(selected_liquidity)]

    if max_latency < 60:
        filtered_df = filtered_df[filtered_df["网络延迟_数值"] <= max_latency]

    if only_executable:
        filtered_df = filtered_df[filtered_df["充提合一"] != "-"]

    filter_info = {
        "quick_filter": quick_filter,
        "min_diff": min_diff,
        "max_diff": max_diff,
        "selected_exchanges": selected_exchanges,
        "search_currency": search_currency
    }

    return filtered_df, filter_info


def calculate_metrics(df: pd.DataFrame) -> Dict:
    """计算统计指标"""
    if len(df) == 0:
        return {
            "total_opportunities": 0,
            "avg_diff": 0,
            "max_diff": 0,
            "high_profit": 0,
            "executable": 0,
            "easy_ops": 0,
            "high_success": 0,
            "low_risk": 0,
            "high_liquidity": 0,
            "fast_networks": 0
        }

    price_diff_values = df["价格差_数值"] if "价格差_数值" in df.columns else df["价格差"].str.rstrip("%").astype(float)
    success_rate_values = df["成功率_数值"] if "成功率_数值" in df.columns else df["成功率"].str.rstrip("%").astype(float)
    latency_values = df["网络延迟_数值"] if "网络延迟_数值" in df.columns else df["网络延迟"].str.rstrip("秒").astype(float)

    return {
        "total_opportunities": len(df),
        "avg_diff": price_diff_values.mean(),
        "max_diff": price_diff_values.max(),
        "high_profit": len(df[price_diff_values > 2.0]),
        "executable": len(df[df["充提合一"] != "-"]),
        "easy_ops": len(df[df["执行难度"].str.contains("简单")]),
        "high_success": len(df[success_rate_values >= 95]),
        "low_risk": len(df[df["风险等级"].str.contains("低风险")]),
        "high_liquidity": len(df[df["流动性"].str.contains("高")]),
        "fast_networks": len(df[latency_values <= 5])
    }


def render_data_source_info():
    """显示数据来源信息 - 优化版本"""
    # 显示加载状态
    if st.session_state.get('arbitrage_loading', False):
        st.info("🔄 正在后台更新数据...")
    
    # 显示错误信息
    if st.session_state.get('arbitrage_error'):
        st.error(f"❌ 数据加载错误: {st.session_state.arbitrage_error}")
        if st.button("🔄 重试加载"):
            st.session_state.arbitrage_error = None
            st.session_state.arbitrage_loading = False
            st.session_state.arbitrage_data_cache = None
            st.rerun()
    
    try:
        # 检查缓存状态
        cache_valid = is_cache_valid(st.session_state.get('arbitrage_cache_time'))
        
        if cache_valid and st.session_state.get('arbitrage_data_cache') is not None:
            # 检查数据来源
            real_opportunities = get_real_arbitrage_opportunities_from_ccxt()
            
            if real_opportunities:
                st.success("✅ **真实数据模式** - 当前显示来自CCXT API的真实市场数据")
                with st.expander("📡 数据来源详情"):
                    st.write("**主要数据源：** CCXT API")
                    st.write("**支持的货币：** Bitcoin, Ethereum, BNB, Cardano, Solana, Polkadot, Avalanche, Polygon等")
                    st.write("**支持的交易所：** Binance, OKX, Bybit, KuCoin, Gate.io, Huobi, Coinbase, Kraken")
                    st.write("**数据更新频率：** 每5分钟缓存刷新")
                    st.write("**数据类型：** 实时价格、订单簿深度、24小时交易量")
                    st.write("**套利计算：** 基于真实价格计算不同交易所价差")
                    st.info("💡 **说明：** 套利机会基于真实价格数据，通过CCXT库获取真实交易所数据")
                return
        
        st.warning("⚠️ **示例数据模式** - 当前显示模拟数据，用于演示功能")
        with st.expander("ℹ️ 为什么显示示例数据？"):
            st.write("可能的原因：")
            st.write("- 网络连接问题")
            st.write("- CCXT API限制或不可用")
            st.write("- 交易所API限制")
            st.write("- CCXT库未正确安装")
            st.write("- 服务器负载过高")
            st.info("💡 **提示：** 安装 `ccxt` 库可启用更多真实数据功能：`pip install ccxt`")
            
    except Exception as e:
        st.error(f"检查数据源状态失败: {str(e)}")


def render_metrics_overview(metrics: Dict):
    """渲染指标概览"""
    st.subheader("📊 实时套利概览")

    # 第一行指标
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("总套利机会", metrics["total_opportunities"])

    with col2:
        st.metric("平均价格差", f"{metrics['avg_diff']:.2f}%")

    with col3:
        st.metric("最大价格差", f"{metrics['max_diff']:.2f}%")

    with col4:
        st.metric("高收益机会", f"{metrics['high_profit']}/{metrics['total_opportunities']}")

    with col5:
        st.metric("可执行机会", f"{metrics['executable']}/{metrics['total_opportunities']}")

    # 第二行专业指标
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("🟢 简单执行", metrics["easy_ops"])

    with col2:
        st.metric("高成功率(≥95%)", metrics["high_success"])

    with col3:
        st.metric("🟢 低风险", metrics["low_risk"])

    with col4:
        st.metric("🟢 高流动性", metrics["high_liquidity"])

    with col5:
        st.metric("快速网络(≤5s)", metrics["fast_networks"])


def highlight_rows(row):
    """为表格行添加颜色编码"""
    try:
        price_diff = float(row["价格差"].rstrip("%"))
        risk_level = row["风险等级"]
        difficulty = row["执行难度"]
        executable = row["充提合一"]

        if executable == "-":
            return ['background-color: #f8f9fa'] * len(row)  # 灰色
        elif price_diff >= 2.0 and "低风险" in risk_level and "简单" in difficulty:
            return ['background-color: #d4edda'] * len(row)  # 绿色
        elif price_diff < 1.0 or "高风险" in risk_level or "困难" in difficulty:
            return ['background-color: #f8d7da'] * len(row)  # 红色
        else:
            return ['background-color: #fff3cd'] * len(row)  # 黄色
    except:
        return [''] * len(row)


def render_opportunities_table(df: pd.DataFrame):
    """渲染套利机会表格"""
    if len(df) == 0:
        st.warning("没有找到符合条件的套利机会，请调整筛选条件。")
        return

    st.subheader(f"套利机会列表 ({len(df)} 个机会)")

    # 颜色说明
    st.markdown("""
    **颜色说明：**
    - 🟢 绿色：高收益 + 低风险 + 简单执行
    - 🟡 黄色：中等收益或中等风险
    - 🔴 红色：低收益或高风险或困难执行
    - ⚫ 灰色：网络不匹配，无法执行
    """)

    # 排序并清理数据
    df_sorted = df.sort_values("价格差_数值", ascending=False) if "价格差_数值" in df.columns else df
    df_display = df_sorted.drop(columns=["价格差_数值", "成功率_数值", "网络延迟_数值"], errors='ignore')

    # 应用样式并显示表格
    styled_df = df_display.style.apply(highlight_rows, axis=1)
    st.dataframe(styled_df, use_container_width=True)

    # 下载按钮
    csv = df_display.to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        label="📥 下载套利机会数据",
        data=csv,
        file_name=f"arbitrage_opportunities_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )


def render_arbitrage_explanation():
    """渲染套利说明"""
    with st.expander("📚 套利操作说明", expanded=False):
        st.markdown("""
        ### 🔗 网络概念解释

        **🔗 提现网络**
        提现网络是指从买入平台提取加密货币时使用的区块链网络。

        **📥 充值网络**
        充值网络是指向卖出平台充值加密货币时支持的区块链网络。

        **✅ 充提合一**
        充提合一表示提现网络和充值网络完全匹配，可以直接进行套利操作。

        ### 📋 完整套利流程

        1. **选择机会** → 找到充提合一显示具体网络的套利机会
        2. **买入** → 在买入平台购买加密货币
        3. **提现** → 使用指定的提现网络提取到个人钱包
        4. **充值** → 使用相同网络充值到卖出平台
        5. **卖出** → 在卖出平台以更高价格卖出
        6. **获利** → 扣除手续费后获得套利收益

        ### ⚠️ 风险提示

        - 数据仅供参考，实际交易前请验证价格
        - 考虑交易手续费、提币费用和时间成本
        - 注意市场波动风险和流动性风险
        - 建议小额测试后再进行大额套利
        """)


def render_arbitrage_opportunities():
    """渲染套利机会页面"""
    try:
        # 页面标题
        st.subheader("🔍 套利机会发现")

        # 获取优化的套利数据（立即返回静态数据，后台更新真实数据）
        df = get_optimized_arbitrage_data()

        # 快速筛选
        st.subheader("⚡ 快速筛选")
        filter_cols = st.columns(len(QUICK_FILTERS))
        selected_filter = "全部机会"

        for i, (filter_name, _) in enumerate(QUICK_FILTERS.items()):
            with filter_cols[i]:
                if st.button(filter_name, key=f"filter_{i}"):
                    selected_filter = filter_name

        # 应用筛选
        filtered_df = apply_quick_filter(df, selected_filter)

        # 计算指标
        metrics = calculate_metrics(filtered_df)

        # 渲染指标概览
        render_metrics_overview(metrics)

        # 渲染套利机会表格
        render_opportunities_table(filtered_df)

        # 渲染说明
        render_arbitrage_explanation()

        # 刷新按钮和状态
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("🔄 刷新数据", key="arbitrage_page_refresh"):
                st.session_state.arbitrage_data_cache = None
                st.session_state.arbitrage_cache_time = None
                st.cache_data.clear()
                st.rerun()

        with col2:
            last_update = st.session_state.get('arbitrage_cache_time', datetime.now())
            st.markdown(f"*最后更新时间: {last_update.strftime('%Y-%m-%d %H:%M:%S')}*")

    except Exception as e:
        st.error(f"❌ 页面渲染错误: {str(e)}")
        st.info("请尝试刷新页面或联系技术支持")
        
        # 提供恢复选项
        if st.button("🔧 重置页面状态"):
            # 清除所有相关的session state
            keys_to_clear = [k for k in st.session_state.keys() if 'arbitrage' in k]
            for key in keys_to_clear:
                del st.session_state[key]
            st.cache_data.clear()
            st.rerun()


def initialize_session_state():
    """初始化session state"""
    # 一键套利相关
    if 'arbitrage_trades' not in st.session_state:
        st.session_state.arbitrage_trades = []
    if 'active_trades' not in st.session_state:
        st.session_state.active_trades = []
    
    # 实时风控相关 - 使用不同的键名避免冲突
    if 'risk_portfolio_summary' not in st.session_state:
        st.session_state.risk_portfolio_summary = {
            'total_value': 100000,
            'positions': {
                'BTC': {'amount': 2.5, 'value': 125000, 'pnl': 25000},
                'ETH': {'amount': 50, 'value': 150000, 'pnl': 50000},
                'BNB': {'amount': 200, 'value': 80000, 'pnl': -5000}
            }
        }
    
    # 执行监控相关
    if 'execution_orders' not in st.session_state:
        st.session_state.execution_orders = []
    if 'execution_pnl' not in st.session_state:
        st.session_state.execution_pnl = []


def main():
    """主函数"""
    # 初始化session state
    initialize_session_state()
    
    st.title("💰 专业套利交易系统")
    
    # 添加自动刷新控制
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown("### 实时套利数据监控")
    with col2:
        auto_refresh = st.checkbox("🔄 自动刷新", value=True, key="arbitrage_auto_refresh")
    with col3:
        refresh_interval = st.selectbox(
            "刷新间隔", 
            options=[5, 10, 15, 30], 
            index=1,
            format_func=lambda x: f"{x}秒",
            key="arbitrage_refresh_interval"
        )
    
    st.markdown("---")

    # 创建标签页
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "🏠 主控制台",
        "🔍 套利机会",
        "💊 市场健康",
        "🔗 相关性分析",
        "💱 价格比较",
        "📈 历史追踪",
        "⚡ 一键套利"
    ])

    with tab1:
        render_main_console()

    with tab2:
        render_arbitrage_opportunities()

    with tab3:
        render_market_health_dashboard()

    with tab4:
        render_correlation_matrix_dashboard()

    with tab5:
        render_multi_exchange_comparison()

    with tab6:
        render_historical_arbitrage_tracker()

    with tab7:
        render_one_click_arbitrage()
    
    # 自动刷新逻辑
    if auto_refresh:
        import time
        import threading
        
        def auto_refresh_data():
            """后台自动刷新数据"""
            time.sleep(refresh_interval)
            # 清除缓存以强制刷新数据
            if 'arbitrage_data_cache' in st.session_state:
                st.session_state.arbitrage_data_cache = None
            if 'arbitrage_cache_time' in st.session_state:
                st.session_state.arbitrage_cache_time = None
            st.rerun()
        
        # 启动后台刷新线程
        if 'refresh_thread' not in st.session_state or not getattr(st.session_state.refresh_thread, 'is_alive', lambda: False)():
            st.session_state.refresh_thread = threading.Thread(target=auto_refresh_data, daemon=True)
            st.session_state.refresh_thread.start()
        
        # 显示刷新状态
        st.info(f"🔄 自动刷新已启用，每 {refresh_interval} 秒更新数据")


if __name__ == "__main__":
    main()
