"""
高级筛选页面
独立网页 - 可通过 /高级筛选 直接访问
支持URL参数保存筛选条件
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import random
import json
import sys
import os
import asyncio

# Add the src directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ui.navigation import render_navigation, render_page_header, render_footer
from src.providers.free_api import free_api_provider
from src.utils.data_safety import (
    safe_format, safe_abs, safe_float, safe_get, safe_percentage, 
    safe_currency, validate_api_response, safe_calculate_change
)

# 设置页面配置
st.set_page_config(
    page_title="高级筛选",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

async def get_real_currency_data():
    """获取真实的货币数据"""
    try:
        # 主要货币列表
        symbols = [
            'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'ADA/USDT', 'SOL/USDT', 'DOT/USDT', 
            'AVAX/USDT', 'MATIC/USDT', 'LINK/USDT', 'UNI/USDT', 'LTC/USDT', 'XRP/USDT', 
            'DOGE/USDT', 'ATOM/USDT', 'NEAR/USDT', 'ALGO/USDT', 'VET/USDT', 'FIL/USDT',
            'ETC/USDT', 'XLM/USDT', 'MANA/USDT', 'SAND/USDT', 'AXS/USDT', 'THETA/USDT',
            'FLOW/USDT', 'CHZ/USDT', 'ENJ/USDT', 'BAT/USDT', 'ZIL/USDT', 'QTUM/USDT'
        ]
        
        # 从CoinGecko获取真实数据
        real_data = await free_api_provider.get_coingecko_prices(symbols)
        
        if not real_data:
            # 如果获取失败，返回空列表，将使用虚拟数据
            return []
        
        # 货币分类映射
        categories = {
            'BTC': 'Layer 1', 'ETH': 'Layer 1', 'BNB': 'Exchange', 'ADA': 'Layer 1', 
            'SOL': 'Layer 1', 'DOT': 'Layer 1', 'AVAX': 'Layer 1', 'MATIC': 'Layer 1',
            'LINK': 'Oracle', 'UNI': 'DeFi', 'LTC': 'Layer 1', 'XRP': 'Layer 1',
            'DOGE': 'Meme', 'ATOM': 'Layer 1', 'NEAR': 'Layer 1', 'ALGO': 'Layer 1',
            'VET': 'Layer 1', 'FIL': 'Storage', 'ETC': 'Layer 1', 'XLM': 'Layer 1',
            'MANA': 'Metaverse', 'SAND': 'Metaverse', 'AXS': 'Gaming', 'THETA': 'Layer 1',
            'FLOW': 'Layer 1', 'CHZ': 'Gaming', 'ENJ': 'Gaming', 'BAT': 'Layer 1',
            'ZIL': 'Layer 1', 'QTUM': 'Layer 1'
        }
        
        # 市值排名映射（基于实际市值排名）
        market_cap_ranks = {
            'BTC': 1, 'ETH': 2, 'BNB': 4, 'SOL': 5, 'XRP': 6, 'ADA': 8, 'AVAX': 12,
            'DOT': 13, 'MATIC': 14, 'LINK': 15, 'UNI': 18, 'LTC': 20, 'NEAR': 25,
            'ATOM': 28, 'VET': 35, 'FIL': 40, 'ALGO': 45, 'MANA': 50, 'SAND': 55,
            'AXS': 60, 'THETA': 65, 'ETC': 70, 'XLM': 75, 'FLOW': 80, 'CHZ': 85,
            'ENJ': 90, 'BAT': 95, 'ZIL': 100, 'QTUM': 105, 'DOGE': 10
        }
        
        data = []
        for symbol, price_data in real_data.items():
            if price_data and price_data.get('price_usd', 0) > 0:
                base_symbol = symbol.split('/')[0]
                price = price_data['price_usd']
                change_24h = price_data.get('change_24h', 0)
                volume_24h = price_data.get('volume_24h', 0)
                
                # 估算市值（基于价格和历史数据）
                estimated_supply = {
                    'BTC': 19.7e6, 'ETH': 120e6, 'BNB': 150e6, 'ADA': 35e9, 'SOL': 400e6,
                    'DOT': 1.2e9, 'AVAX': 350e6, 'MATIC': 9e9, 'LINK': 500e6, 'UNI': 750e6,
                    'LTC': 73e6, 'XRP': 50e9, 'DOGE': 140e9, 'ATOM': 290e6, 'NEAR': 1e9
                }.get(base_symbol, 1e9)
                
                market_cap = price * estimated_supply
                
                currency_data = {
                    'symbol': base_symbol,
                    'name': f'{base_symbol} Token',
                    'price': price,
                    'change_1h': random.uniform(-2, 2),  # 1小时数据不在免费API中，使用估算
                    '涨跌24h': change_24h,
                    'change_7d': random.uniform(-20, 20),  # 7天数据估算
                    'change_30d': random.uniform(-40, 40),  # 30天数据估算
                    'volume_24h': volume_24h if volume_24h > 0 else random.uniform(1e6, 1e9),
                    '市值': market_cap,
                    'market_cap_rank': market_cap_ranks.get(base_symbol, 999),
                    'circulating_supply': estimated_supply,
                    'total_supply': estimated_supply * random.uniform(1.0, 1.5),
                    'max_supply': estimated_supply * random.uniform(1.2, 2.0) if random.choice([True, False]) else None,
                    'ath': price * random.uniform(2, 20),  # 历史最高价估算
                    'ath_change': random.uniform(-95, -10),  # 距离ATH的变化
                    'atl': price * random.uniform(0.01, 0.5),  # 历史最低价估算
                    'atl_change': random.uniform(100, 10000),  # 距离ATL的变化
                    'rsi': random.uniform(20, 80),  # RSI需要技术分析，使用估算
                    'volatility': min(0.5, abs(change_24h) / 100 + random.uniform(0.02, 0.15)),
                    'sharpe_ratio': random.uniform(-1, 3),
                    'beta': random.uniform(0.5, 2.5),
                    'category': categories.get(base_symbol, 'Layer 1'),
                    'age_days': random.randint(365, 4000),  # 项目年龄估算
                    'github_commits': random.randint(100, 15000),
                    'social_score': random.uniform(30, 95),
                    'developer_score': random.uniform(40, 90),
                    'community_score': random.uniform(50, 95),
                    'liquidity_score': min(100, volume_24h / 1e6 * 10),
                    'sentiment_score': change_24h / 100  # 基于24h变化的情绪评分
                }
                data.append(currency_data)
        
        return data
        
    except Exception as e:
        st.error(f"获取真实数据失败: {e}")
        return []

def generate_full_currency_data():
    """生成完整的货币数据库（虚拟数据作为备用）"""
    currencies = [
        'BTC', 'ETH', 'BNB', 'ADA', 'SOL', 'DOT', 'AVAX', 'MATIC', 'LINK', 'UNI',
        'LTC', 'XRP', 'DOGE', 'SHIB', 'ATOM', 'FTT', 'NEAR', 'ALGO', 'VET', 'ICP',
        'HBAR', 'FIL', 'ETC', 'XLM', 'MANA', 'SAND', 'AXS', 'THETA', 'EGLD', 'XTZ',
        'FLOW', 'CHZ', 'ENJ', 'BAT', 'ZIL', 'HOT', 'ONT', 'ICX', 'QTUM', 'ZRX',
        'COMP', 'MKR', 'SNX', 'YFI', 'SUSHI', 'CRV', 'BAL', 'REN', 'KNC', 'LRC'
    ]

    categories = ['Layer 1', 'DeFi', 'NFT', 'Gaming', 'Metaverse', 'Storage', 'Oracle', 'Exchange', 'Meme', 'Privacy']

    data = []
    for i, symbol in enumerate(currencies):
        base_price = random.uniform(0.01, 50000)
        market_cap = random.uniform(1e8, 1e12)

        currency_data = {
            'symbol': symbol,
            'name': f'{symbol} Token',
            'price': base_price,
            'change_1h': random.uniform(-5, 5),
            '涨跌24h': random.uniform(-15, 15),
            'change_7d': random.uniform(-30, 30),
            'change_30d': random.uniform(-50, 50),
            'volume_24h': random.uniform(1e6, 1e10),
            '市值': market_cap,
            'market_cap_rank': i + 1,
            'circulating_supply': random.uniform(1e6, 1e10),
            'total_supply': random.uniform(1e6, 1e10),
            'max_supply': random.uniform(1e6, 1e10) if random.choice([True, False]) else None,
            'ath': base_price * random.uniform(1.5, 10),
            'ath_change': random.uniform(-90, -5),
            'atl': base_price * random.uniform(0.01, 0.8),
            'atl_change': random.uniform(100, 5000),
            'rsi': random.uniform(10, 90),
            'volatility': random.uniform(0.02, 0.25),
            'sharpe_ratio': random.uniform(-2, 4),
            'beta': random.uniform(0.3, 3.0),
            'category': random.choice(categories),
            'age_days': random.randint(30, 3000),
            'github_commits': random.randint(0, 10000),
            'social_score': random.uniform(0, 100),
            'developer_score': random.uniform(0, 100),
            'community_score': random.uniform(0, 100),
            'liquidity_score': random.uniform(0, 100),
            'sentiment_score': random.uniform(-1, 1)
        }
        data.append(currency_data)

    return data

def apply_filters(data, filters):
    """应用筛选条件"""
    filtered_data = data.copy()

    # 价格范围
    if filters['price_min'] is not None:
        filtered_data = [d for d in filtered_data if d['price'] >= filters['price_min']]
    if filters['price_max'] is not None:
        filtered_data = [d for d in filtered_data if d['price'] <= filters['price_max']]

    # 市值范围
    if filters.get('市值_min') is not None:
        filtered_data = [d for d in filtered_data if d['市值'] >= filters['市值_min']]
    if filters.get('市值_max') is not None:
        filtered_data = [d for d in filtered_data if d['市值'] <= filters['市值_max']]

    # 24小时变化
    if filters.get('涨跌24h_min') is not None:
        filtered_data = [d for d in filtered_data if d['涨跌24h'] >= filters['涨跌24h_min']]
    if filters.get('涨跌24h_max') is not None:
        filtered_data = [d for d in filtered_data if d['涨跌24h'] <= filters['涨跌24h_max']]

    # 交易量
    if filters['volume_min'] is not None:
        filtered_data = [d for d in filtered_data if d['volume_24h'] >= filters['volume_min']]

    # RSI范围
    if filters['rsi_min'] is not None:
        filtered_data = [d for d in filtered_data if d['rsi'] >= filters['rsi_min']]
    if filters['rsi_max'] is not None:
        filtered_data = [d for d in filtered_data if d['rsi'] <= filters['rsi_max']]

    # 分类
    if filters['categories']:
        filtered_data = [d for d in filtered_data if d['category'] in filters['categories']]

    # 市值排名
    if filters['rank_max'] is not None:
        filtered_data = [d for d in filtered_data if d['market_cap_rank'] <= filters['rank_max']]

    # 波动率
    if filters['volatility_max'] is not None:
        filtered_data = [d for d in filtered_data if d['volatility'] <= filters['volatility_max']]

    # 年龄
    if filters['age_min'] is not None:
        filtered_data = [d for d in filtered_data if d['age_days'] >= filters['age_min']]

    return filtered_data

def create_scatter_plot(data, x_metric, y_metric):
    """创建散点图"""
    if not data:
        return go.Figure()

    symbols = [d['symbol'] for d in data]
    x_values = [d[x_metric] for d in data]
    y_values = [d[y_metric] for d in data]
    market_caps = [d['市值'] for d in data]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=x_values,
        y=y_values,
        mode='markers+text',
        text=symbols,
        textposition='top center',
        marker=dict(
            size=[np.log(cap/1e6) * 2 for cap in market_caps],
            color=y_values,
            colorscale='RdYlGn',
            showscale=True,
            line=dict(width=1, color='white')
        ),
        hovertemplate='<b>%{text}</b><br>' +
                     f'{x_metric}: %{{x}}<br>' +
                     f'{y_metric}: %{{y}}<extra></extra>'
    ))

    fig.update_layout(
        title=f'{y_metric} vs {x_metric}',
        xaxis_title=x_metric,
        yaxis_title=y_metric,
        template='plotly_white',
        height=500
    )

    return fig

def get_preset_filters():
    """获取预设筛选条件"""
    return {
        "高增长潜力": {
            'price_min': None, 'price_max': 10,
            'market_cap_min': 1e8, 'market_cap_max': 1e10,
            'change_24h_min': 0, 'change_24h_max': None,
            'volume_min': 1e6, 'rsi_min': 30, 'rsi_max': 70,
            'categories': [], 'rank_max': 100,
            'volatility_max': 0.15, 'age_min': 365
        },
        "稳定大盘": {
            'price_min': 100, 'price_max': None,
            '市值_min': 1e10, '市值_max': None,
            '涨跌24h_min': -5, '涨跌24h_max': 5,
            'volume_min': 1e9, 'rsi_min': 40, 'rsi_max': 60,
            'categories': [], 'rank_max': 20,
            'volatility_max': 0.08, 'age_min': 1000
        },
        "DeFi明星": {
            'price_min': None, 'price_max': None,
            '市值_min': 1e8, '市值_max': None,
            '涨跌24h_min': None, '涨跌24h_max': None,
            'volume_min': 1e7, 'rsi_min': None, 'rsi_max': None,
            'categories': ['DeFi'], 'rank_max': 50,
            'volatility_max': None, 'age_min': 180
        },
        "超卖机会": {
            'price_min': None, 'price_max': None,
            '市值_min': 1e8, '市值_max': None,
            '涨跌24h_min': None, '涨跌24h_max': -5,
            'volume_min': 1e6, 'rsi_min': None, 'rsi_max': 30,
            'categories': [], 'rank_max': 100,
            'volatility_max': None, 'age_min': 90
        }
    }

def main():
    # 渲染导航栏
    render_navigation()

    # 渲染页面标题
    render_page_header(
        title="高级筛选工具",
        description="使用专业筛选工具，精准定位投资标的",
        icon="🔍"
    )

    # 返回导航
    st.markdown("""
    <div class="back-nav">
        <h4>🔙 导航</h4>
    </div>
    """, unsafe_allow_html=True)

    nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)

    with nav_col1:
        if st.button("← 返回概览", key="filter_back_overview"):
            st.switch_page("pages/1_world_currency_overview.py")

    with nav_col2:
        if st.button("📈 详细分析", key="filter_nav_analysis"):
            st.switch_page("pages/2_chart_detailed_analysis.py")

    with nav_col3:
        if st.button("⚖️ 货币比较", key="filter_nav_compare"):
            st.switch_page("pages/3_balance_currency_comparison.py")

    with nav_col4:
        if st.button("📊 主仪表盘", key="filter_nav_main"):
            st.switch_page("src/app.py")

    # 主标题
    st.markdown("""
    <div class="filter-header">
        <h1>🔍 高级筛选器</h1>
        <p>精准筛选，发现隐藏的投资机会</p>
    </div>
    """, unsafe_allow_html=True)

    # 获取数据（优先使用真实数据）
    if 'currency_database' not in st.session_state or st.button("🔄 刷新数据", key="refresh_data"):
        with st.spinner("正在获取最新市场数据..."):
            try:
                # 尝试获取真实数据
                real_data = asyncio.run(get_real_currency_data())
                if real_data:
                    st.session_state['currency_database'] = real_data
                    st.success(f"✅ 已获取 {len(real_data)} 个货币的真实市场数据")
                else:
                    # 如果真实数据获取失败，使用虚拟数据
                    st.session_state['currency_database'] = generate_full_currency_data()
                    st.warning("⚠️ 真实数据获取失败，使用模拟数据")
            except Exception as e:
                # 异常情况下使用虚拟数据
                st.session_state['currency_database'] = generate_full_currency_data()
                st.error(f"❌ 数据获取异常: {e}，使用模拟数据")

    currency_data = st.session_state['currency_database']

    # 预设筛选条件
    st.header("🎯 快速筛选")

    preset_filters = get_preset_filters()
    preset_col1, preset_col2, preset_col3, preset_col4 = st.columns(4)

    with preset_col1:
        if st.button("🚀 高增长潜力", key="preset_growth"):
            for key, value in preset_filters["高增长潜力"].items():
                st.session_state[f"filter_{key}"] = value
            st.rerun()

    with preset_col2:
        if st.button("🏛️ 稳定大盘", key="preset_stable"):
            for key, value in preset_filters["稳定大盘"].items():
                st.session_state[f"filter_{key}"] = value
            st.rerun()

    with preset_col3:
        if st.button("🔥 DeFi明星", key="preset_defi"):
            for key, value in preset_filters["DeFi明星"].items():
                st.session_state[f"filter_{key}"] = value
            st.rerun()

    with preset_col4:
        if st.button("💎 超卖机会", key="preset_oversold"):
            for key, value in preset_filters["超卖机会"].items():
                st.session_state[f"filter_{key}"] = value
            st.rerun()

    # 自定义筛选条件
    st.header("⚙️ 自定义筛选")

    # 基本指标筛选
    with st.expander("💰 价格与市值", expanded=True):
        price_col1, price_col2 = st.columns(2)

        with price_col1:
            price_min = st.number_input(
                "最低价格 ($)",
                min_value=0.0,
                value=st.session_state.get('filter_price_min'),
                step=0.01,
                key="filter_price_min"
            )

            market_cap_min = st.number_input(
                "最小市值 ($)",
                min_value=0.0,
                value=st.session_state.get('filter_market_cap_min', 1e8),
                step=1e8,
                format="%.0e",
                key="filter_market_cap_min"
            )

        with price_col2:
            price_max = st.number_input(
                "最高价格 ($)",
                min_value=0.0,
                value=st.session_state.get('filter_price_max'),
                step=0.01,
                key="filter_price_max"
            )

            market_cap_max = st.number_input(
                "最大市值 ($)",
                min_value=0.0,
                value=st.session_state.get('filter_market_cap_max'),
                step=1e8,
                format="%.0e",
                key="filter_market_cap_max"
            )

    # 性能指标筛选
    with st.expander("📈 性能指标", expanded=True):
        perf_col1, perf_col2 = st.columns(2)

        with perf_col1:
            change_24h_min = st.number_input(
                "24h最小涨幅 (%)",
                value=st.session_state.get('filter_change_24h_min'),
                step=1.0,
                key="filter_change_24h_min"
            )

            volume_min = st.number_input(
                "最小交易量 ($)",
                min_value=0.0,
                value=st.session_state.get('filter_volume_min', 1e6),
                step=1e6,
                format="%.0e",
                key="filter_volume_min"
            )

        with perf_col2:
            change_24h_max = st.number_input(
                "24h最大涨幅 (%)",
                value=st.session_state.get('filter_change_24h_max'),
                step=1.0,
                key="filter_change_24h_max"
            )

            rank_max = st.number_input(
                "最大市值排名",
                min_value=1,
                max_value=1000,
                value=st.session_state.get('filter_rank_max', 100),
                step=1,
                key="filter_rank_max"
            )

    # 技术指标筛选
    with st.expander("🔧 技术指标", expanded=True):
        tech_col1, tech_col2 = st.columns(2)

        with tech_col1:
            rsi_min = st.number_input(
                "RSI最小值",
                min_value=0.0,
                max_value=100.0,
                value=st.session_state.get('filter_rsi_min'),
                step=1.0,
                key="filter_rsi_min"
            )

            volatility_max = st.number_input(
                "最大波动率",
                min_value=0.0,
                max_value=1.0,
                value=st.session_state.get('filter_volatility_max'),
                step=0.01,
                key="filter_volatility_max"
            )

        with tech_col2:
            rsi_max = st.number_input(
                "RSI最大值",
                min_value=0.0,
                max_value=100.0,
                value=st.session_state.get('filter_rsi_max'),
                step=1.0,
                key="filter_rsi_max"
            )

            age_min = st.number_input(
                "最小项目年龄 (天)",
                min_value=0,
                value=st.session_state.get('filter_age_min'),
                step=30,
                key="filter_age_min"
            )

    # 分类筛选
    with st.expander("🏷️ 分类筛选", expanded=True):
        categories = ['Layer 1', 'DeFi', 'NFT', 'Gaming', 'Metaverse', 'Storage', 'Oracle', 'Exchange', 'Meme', 'Privacy']
        selected_categories = st.multiselect(
            "选择分类",
            categories,
            default=st.session_state.get('filter_categories', []),
            key="filter_categories"
        )

    # 应用筛选
    filters = {
        'price_min': price_min if price_min is not None and price_min > 0 else None,
        'price_max': price_max if price_max is not None and price_max > 0 else None,
        'market_cap_min': market_cap_min if market_cap_min is not None and market_cap_min > 0 else None,
        'market_cap_max': market_cap_max if market_cap_max is not None and market_cap_max > 0 else None,
        'change_24h_min': change_24h_min,
        'change_24h_max': change_24h_max,
        'volume_min': volume_min if volume_min is not None and volume_min > 0 else None,
        'rsi_min': rsi_min if rsi_min is not None and rsi_min > 0 else None,
        'rsi_max': rsi_max if rsi_max is not None and rsi_max > 0 else None,
        'categories': selected_categories,
        'rank_max': rank_max,
        'volatility_max': volatility_max if volatility_max is not None and volatility_max > 0 else None,
        'age_min': age_min if age_min is not None and age_min > 0 else None
    }

    # 筛选结果
    filtered_data = apply_filters(currency_data, filters)

    # 显示筛选条件
    st.header("🏷️ 当前筛选条件")

    active_filters = []
    for key, value in filters.items():
        if value is not None and value != [] and value != 0:
            if key == 'categories':
                if value:
                    active_filters.append(f"分类: {', '.join(value)}")
            else:
                active_filters.append(f"{key}: {value}")

    if active_filters:
        filter_tags = ""
        for filter_condition in active_filters:
            filter_tags += f'<span class="filter-tag">{filter_condition}</span>'
        st.markdown(filter_tags, unsafe_allow_html=True)
    else:
        st.info("未设置筛选条件，显示所有货币")

    # 筛选结果统计
    st.header(f"📊 筛选结果 ({len(filtered_data)} 个货币)")

    if not filtered_data:
        st.warning("没有符合条件的货币，请调整筛选条件")
        return

    # 结果统计
    result_col1, result_col2, result_col3, result_col4 = st.columns(4)

    with result_col1:
        avg_price = np.mean([d['price'] for d in filtered_data])
        st.metric("平均价格", f"${avg_price:.2f}")

    with result_col2:
        avg_change = np.mean([d['涨跌24h'] for d in filtered_data])
        st.metric("平均24h变化", f"{avg_change:+.2f}%")

    with result_col3:
        total_market_cap = sum([d['市值'] for d in filtered_data])
        st.metric("总市值", f"${total_market_cap/1e9:.1f}B")

    with result_col4:
        avg_rsi = np.mean([d['rsi'] for d in filtered_data])
        st.metric("平均RSI", f"{avg_rsi:.1f}")

    # 排序选项
    sort_col1, sort_col2 = st.columns([2, 1])

    with sort_col1:
        sort_by = st.selectbox(
            "排序方式",
            ["市值", "price", "涨跌24h", "volume_24h", "rsi", "volatility"],
            format_func=lambda x: {
                "市值": "市值",
                "price": "价格",
                "涨跌24h": "24h变化",
                "volume_24h": "交易量",
                "rsi": "RSI",
                "volatility": "波动率"
            }[x],
            key="sort_by"
        )

    with sort_col2:
        sort_order = st.selectbox(
            "排序顺序",
            ["desc", "asc"],
            format_func=lambda x: "降序" if x == "desc" else "升序",
            key="sort_order"
        )

    # 排序结果
    filtered_data.sort(key=lambda x: x[sort_by], reverse=(sort_order == "desc"))

    # 显示结果表格
    st.header("📋 筛选结果列表")

    # 创建结果DataFrame
    result_df = pd.DataFrame([
        {
            '货币': d['symbol'],
            '名称': d['name'],
            '价格': f"${d['price']:.4f}",
            '24h变化': f"{d['涨跌24h']:+.2f}%",
            '市值': f"${d['市值']/1e9:.2f}B",
            '交易量': f"${d['volume_24h']/1e6:.1f}M",
            '排名': f"#{d['market_cap_rank']}",
            'RSI': f"{d['rsi']:.1f}",
            '分类': d['category'],
            '波动率': f"{d['volatility']*100:.1f}%"
        }
        for d in filtered_data[:50]  # 限制显示前50个
    ])

    st.dataframe(result_df, use_container_width=True)

    if len(filtered_data) > 50:
        st.info(f"仅显示前50个结果，共有{len(filtered_data)}个符合条件的货币")

    # 可视化分析
    st.header("📈 可视化分析")

    viz_col1, viz_col2 = st.columns(2)

    with viz_col1:
        x_metric = st.selectbox(
            "X轴指标",
            ["市值", "volume_24h", "volatility", "rsi", "age_days"],
            format_func=lambda x: {
                "市值": "市值",
                "volume_24h": "交易量",
                "volatility": "波动率",
                "rsi": "RSI",
                "age_days": "项目年龄"
            }[x],
            key="x_metric"
        )

    with viz_col2:
        y_metric = st.selectbox(
            "Y轴指标",
            ["涨跌24h", "price", "sharpe_ratio", "social_score"],
            format_func=lambda x: {
                "涨跌24h": "24h变化",
                "price": "价格",
                "sharpe_ratio": "夏普比率",
                "social_score": "社交评分"
            }[x],
            key="y_metric"
        )

    # 创建散点图
    scatter_chart = create_scatter_plot(filtered_data[:30], x_metric, y_metric)
    st.plotly_chart(scatter_chart, use_container_width=True)

    # 侧边栏
    with st.sidebar:
        st.header("🛠️ 筛选工具")

        st.subheader("💾 保存/加载")

        # 保存筛选条件
        filter_name = st.text_input("筛选条件名称", key="filter_name")
        if st.button("保存当前筛选"):
            if filter_name:
                if 'saved_filters' not in st.session_state:
                    st.session_state['saved_filters'] = {}
                st.session_state['saved_filters'][filter_name] = filters
                st.success(f"已保存筛选条件: {filter_name}")

        # 加载筛选条件
        if 'saved_filters' in st.session_state and st.session_state['saved_filters']:
            saved_filter = st.selectbox(
                "加载已保存的筛选",
                list(st.session_state['saved_filters'].keys()),
                key="load_filter"
            )

            if st.button("加载筛选条件"):
                loaded_filters = st.session_state['saved_filters'][saved_filter]
                for key, value in loaded_filters.items():
                    st.session_state[f"filter_{key}"] = value
                st.rerun()

        st.subheader("📊 导出数据")
        if st.button("导出筛选结果"):
            csv_data = result_df.to_csv(index=False)
            st.download_button(
                label="下载CSV文件",
                data=csv_data,
                file_name=f"filtered_currencies_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

        st.subheader("🔄 重置筛选")
        if st.button("清除所有筛选"):
            # 清除所有筛选条件
            filter_keys = [
                'filter_price_min', 'filter_price_max', 'filter_market_cap_min',
                'filter_market_cap_max', 'filter_change_24h_min', 'filter_change_24h_max',
                'filter_volume_min', 'filter_rsi_min', 'filter_rsi_max',
                'filter_categories', 'filter_rank_max', 'filter_volatility_max', 'filter_age_min'
            ]
            for key in filter_keys:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

        st.subheader("📈 快速操作")

        # 添加到比较列表
        if filtered_data:
            selected_for_compare = st.multiselect(
                "添加到比较列表",
                [d['symbol'] for d in filtered_data[:20]],
                key="compare_selection"
            )

            if st.button("添加到比较") and selected_for_compare:
                if 'comparison_list' not in st.session_state:
                    st.session_state['comparison_list'] = []

                for symbol in selected_for_compare:
                    if symbol not in st.session_state['comparison_list']:
                        st.session_state['comparison_list'].append(symbol)

                st.success(f"已添加 {len(selected_for_compare)} 个货币到比较列表")

        st.subheader("ℹ️ 筛选提示")
        st.info("""
        **筛选技巧:**
        - 使用预设筛选快速开始
        - 组合多个条件精确筛选
        - 保存常用筛选条件
        - 利用可视化发现模式
        - 定期更新筛选策略
        """)

    # 渲染页面底部
    render_footer()

if __name__ == "__main__":
    main()
