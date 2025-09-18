"""
货币概览主页
独立网页 - 可通过 /货币概览 直接访问
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import random
import sys
import os
import asyncio

# Add the src directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ui.navigation import render_navigation, render_page_header, render_footer
from src.providers.free_api import free_api_provider
from utils.data_safety import (
    safe_format, safe_abs, safe_float, safe_get, safe_percentage, 
    safe_currency, validate_api_response, safe_calculate_change
)

# 页面配置
st.set_page_config(
    page_title="货币概览",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义样式
st.markdown("""
<style>
.main-header {
    background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
    color: white;
    padding: 2rem;
    border-radius: 15px;
    text-align: center;
    margin-bottom: 2rem;
}

.metric-card {
    background: white;
    padding: 1.5rem;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    border-left: 4px solid #2a5298;
}

.currency-row {
    padding: 0.5rem;
    border-radius: 5px;
    margin: 0.2rem 0;
}

.currency-row:hover {
    background-color: #f0f2f6;
}

.positive {
    color: #00d4aa;
    font-weight: bold;
}

.negative {
    color: #ff6b6b;
    font-weight: bold;
}

.quick-nav {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 10px;
    margin: 1rem 0;
}

.nav-button {
    background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 0.8rem 1.5rem;
    border: none;
    border-radius: 8px;
    text-decoration: none;
    display: inline-block;
    margin: 0.5rem;
    font-weight: bold;
    transition: transform 0.2s;
}

.nav-button:hover {
    transform: translateY(-2px);
}
</style>
""", unsafe_allow_html=True)

async def get_real_market_data():
    """获取真实市场数据"""
    try:
        # 主要货币列表
        symbols = [
            'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'ADA/USDT', 'SOL/USDT', 'DOT/USDT', 
            'AVAX/USDT', 'MATIC/USDT', 'LINK/USDT', 'UNI/USDT', 'ATOM/USDT', 'FIL/USDT',
            'ALGO/USDT', 'VET/USDT', 'XTZ/USDT', 'THETA/USDT', 'AAVE/USDT', 'MKR/USDT',
            'COMP/USDT', 'SNX/USDT', 'YFI/USDT', 'CRV/USDT', 'SUSHI/USDT', 'LTC/USDT',
            'XRP/USDT', 'DOGE/USDT', 'NEAR/USDT', 'MANA/USDT', 'SAND/USDT', 'AXS/USDT'
        ]
        
        # 从CoinGecko获取真实数据
        real_data = await free_api_provider.get_coingecko_prices(symbols)
        
        if not validate_api_response(real_data):
            st.warning("API返回空数据，使用虚拟数据")
            return None
        
        # 市值排名映射（基于实际市值排名）
        market_cap_ranks = {
            'BTC': 1, 'ETH': 2, 'BNB': 4, 'SOL': 5, 'XRP': 6, 'ADA': 8, 'AVAX': 12,
            'DOT': 13, 'MATIC': 14, 'LINK': 15, 'UNI': 18, 'LTC': 20, 'NEAR': 25,
            'ATOM': 28, 'VET': 35, 'FIL': 40, 'ALGO': 45, 'MANA': 50, 'SAND': 55,
            'AXS': 60, 'THETA': 65, 'XTZ': 70, 'AAVE': 75, 'MKR': 80, 'COMP': 85,
            'SNX': 90, 'YFI': 95, 'CRV': 100, 'SUSHI': 105, 'DOGE': 10
        }
        
        # 估算流通量
        estimated_supply = {
            'BTC': 19.7e6, 'ETH': 120e6, 'BNB': 150e6, 'ADA': 35e9, 'SOL': 400e6,
            'DOT': 1.2e9, 'AVAX': 350e6, 'MATIC': 9e9, 'LINK': 500e6, 'UNI': 750e6,
            'LTC': 73e6, 'XRP': 50e9, 'DOGE': 140e9, 'ATOM': 290e6, 'NEAR': 1e9,
            'FIL': 400e6, 'ALGO': 7e9, 'VET': 86e9, 'XTZ': 900e6, 'THETA': 1e9,
            'AAVE': 16e6, 'MKR': 1e6, 'COMP': 10e6, 'SNX': 300e6, 'YFI': 36000,
            'CRV': 3e9, 'SUSHI': 250e6, 'MANA': 2e9, 'SAND': 3e9, 'AXS': 270e6
        }
        
        data = []
        for symbol, price_data in real_data.items():
            if validate_api_response(price_data) and safe_float(safe_get(price_data, 'price_usd', 0)) > 0:
                base_symbol = symbol.split('/')[0]
                price = safe_float(safe_get(price_data, 'price_usd', 0))
                change_24h = safe_float(safe_get(price_data, 'change_24h', 0))
                volume_24h = safe_float(safe_get(price_data, 'volume_24h', 0))
                
                # 计算市值
                supply = estimated_supply.get(base_symbol, 1e9)
                market_cap = price * supply
                
                data.append({
                    '排名': market_cap_ranks.get(base_symbol, 999),
                    '货币': base_symbol,
                    '价格': price,
                    '价格显示': safe_currency(price) if price >= 1 else safe_format("${:.6f}", price),
                    '24h涨跌': change_24h,
                    '24h涨跌显示': safe_percentage(change_24h),
                    '24h交易量': safe_format("${:.2f}B", volume_24h/1e9) if volume_24h > 0 else "N/A",
                    '市值': safe_format("${:.2f}B", market_cap/1e9),
                    '流通量': safe_format("{:.1f}M", supply/1e6) if supply >= 1e6 else safe_format("{:.0f}", supply),
                })
        
        # 按排名排序
        data.sort(key=lambda x: x['排名'])
        return pd.DataFrame(data)
        
    except Exception as e:
        st.error(safe_format("获取真实数据失败: {}", str(e)))
        return None

def generate_market_data():
    """生成市场数据（虚拟数据作为备用）"""
    currencies = [
        'BTC', 'ETH', 'BNB', 'ADA', 'SOL', 'DOT', 'AVAX', 'MATIC', 'LINK', 'UNI',
        'ATOM', 'ICP', 'FTM', 'ALGO', 'XTZ', 'EGLD', 'THETA', 'VET', 'FIL', 'TRX',
        'EOS', 'AAVE', 'MKR', 'COMP', 'SNX', 'YFI', 'UMA', 'BAL', 'CRV', 'SUSHI'
    ]

    data = []
    for i, currency in enumerate(currencies):
        price = random.uniform(0.1, 50000)
        change_24h = random.uniform(-15, 15)
        volume = random.uniform(1e6, 1e10)
        market_cap = random.uniform(1e8, 1e12)

        data.append({
            '排名': i + 1,
            '货币': currency,
            '价格': price,
            '价格显示': safe_currency(price),
            '24h涨跌': change_24h,
            '24h涨跌显示': safe_percentage(change_24h),
            '24h交易量': safe_format("${:.2f}B", volume/1e9),
            '市值': safe_format("${:.2f}B", market_cap/1e9),
            '流通量': safe_format("{:.0f}", random.uniform(1e6, 1e9)),
        })

    return pd.DataFrame(data)

def main():
    # 渲染导航栏
    render_navigation()

    # 渲染页面标题
    render_page_header(
        title="全球货币市场概览",
        description="实时监控全球货币市场动态，掌握投资先机",
        icon="🌍"
    )

    # 快速导航
    st.markdown("""
    <div class="quick-nav">
        <h3>🚀 快速导航</h3>
        <p>选择您需要的功能模块：</p>
    </div>
    """, unsafe_allow_html=True)

    nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)

    with nav_col1:
        if st.button("📈 详细分析", key="overview_nav_analysis", help="深入分析单个货币"):
            st.switch_page("pages/2_chart_detailed_analysis.py")

    with nav_col2:
        if st.button("⚖️ 货币比较", key="overview_nav_compare", help="对比多个货币"):
            st.switch_page("pages/3_balance_currency_comparison.py")

    with nav_col3:
        if st.button("🔍 高级筛选", key="overview_nav_filter", help="自定义筛选条件"):
            st.switch_page("pages/4_search_advanced_filter.py")

    with nav_col4:
        if st.button("📊 实时仪表盘", key="overview_nav_dashboard", help="返回主仪表盘"):
            st.switch_page("pages/5_dashboard_realtime_dashboard.py")

    # 市场统计
    st.header("📊 市场统计")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="总市值",
            value="$2.1T",
            delta="2.3%",
            help="全球加密货币总市值"
        )

    with col2:
        st.metric(
            label="24h交易量",
            value="$89.2B",
            delta="-1.2%",
            help="过去24小时总交易量"
        )

    with col3:
        st.metric(
            label="活跃货币",
            value="100",
            delta="0",
            help="当前追踪的货币数量"
        )

    with col4:
        st.metric(
            label="涨跌比",
            value="67:33",
            delta="5.2%",
            help="上涨vs下跌货币比例"
        )

    # 筛选器
    st.header("🔍 快速筛选")

    filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)

    with filter_col1:
        market_cap_filter = st.selectbox(
            "市值范围",
            ["全部", "大盘股 (>$10B)", "中盘股 ($1B-$10B)", "小盘股 (<$1B)"],
            help="按市值大小筛选"
        )

    with filter_col2:
        change_filter = st.selectbox(
            "24h涨跌",
            ["全部", "上涨 (>0%)", "下跌 (<0%)", "大涨 (>5%)", "大跌 (<-5%)"],
            help="按涨跌幅筛选"
        )

    with filter_col3:
        category_filter = st.selectbox(
            "货币类别",
            ["全部", "主流币", "DeFi", "Layer1", "Layer2", "Meme币"],
            help="按货币类别筛选"
        )

    with filter_col4:
        sort_by = st.selectbox(
            "排序方式",
            ["市值", "价格", "24h涨跌", "交易量"],
            help="选择排序依据"
        )

    # 主要货币列表
    st.header("💰 主要货币")

    # 获取数据（优先使用真实数据）
    if 'market_data' not in st.session_state or st.button("🔄 刷新数据", key="refresh_market_data"):
        with st.spinner("正在获取最新市场数据..."):
            try:
                # 尝试获取真实数据
                real_df = asyncio.run(get_real_market_data())
                if real_df is not None and not real_df.empty:
                    st.session_state['market_data'] = real_df
                    st.session_state['data_source'] = 'real'
                    st.success(f"✅ 已获取 {len(real_df)} 个货币的真实市场数据")
                else:
                    # 如果真实数据获取失败，使用虚拟数据
                    st.session_state['market_data'] = generate_market_data()
                    st.session_state['data_source'] = 'mock'
                    st.warning("⚠️ 真实数据获取失败，使用模拟数据")
            except Exception as e:
                # 异常情况下使用虚拟数据
                st.session_state['market_data'] = generate_market_data()
                st.session_state['data_source'] = 'mock'
                st.error(f"❌ 数据获取异常: {e}，使用模拟数据")

    df = st.session_state['market_data']
    
    # 显示数据源信息
    if st.session_state.get('data_source') == 'real':
        st.info("📊 当前显示真实市场数据")
    else:
        st.warning("📊 当前显示模拟数据")

    # 应用筛选（简化版）
    if change_filter == "上涨 (>0%)":
        df = df[df['24h涨跌'] > 0]
    elif change_filter == "下跌 (<0%)":
        df = df[df['24h涨跌'] < 0]
    elif change_filter == "大涨 (>5%)":
        df = df[df['24h涨跌'] > 5]
    elif change_filter == "大跌 (<-5%)":
        df = df[df['24h涨跌'] < -5]

    # 显示表格
    display_df = df[['排名', '货币', '价格显示', '24h涨跌显示', '24h交易量', '市值', '流通量']].copy()
    display_df.columns = ['排名', '货币', '价格', '24h涨跌', '24h交易量', '市值', '流通量']

    # 可选择的表格
    selected_rows = st.dataframe(
        display_df,
        use_container_width=True,
        on_select="rerun",
        selection_mode="single-row",
        hide_index=True
    )

    # 处理选择
    if selected_rows.selection.rows:
        selected_idx = selected_rows.selection.rows[0]
        selected_currency = df.iloc[selected_idx]['货币']

        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            st.success(f"已选择: {selected_currency}")

        with col2:
            if st.button("📈 查看详细分析", key="view_detail"):
                # 保存选择的货币到session state
                st.session_state['selected_currency'] = selected_currency
                st.switch_page("pages/2_chart_detailed_analysis.py")

        with col3:
            if st.button("⚖️ 添加到比较", key="add_compare"):
                # 添加到比较列表
                if 'comparison_list' not in st.session_state:
                    st.session_state['comparison_list'] = []

                if selected_currency not in st.session_state['comparison_list']:
                    st.session_state['comparison_list'].append(selected_currency)
                    st.success(f"已添加 {selected_currency} 到比较列表")
                else:
                    st.warning(f"{selected_currency} 已在比较列表中")

    # 市场热力图
    st.header("🔥 市场热力图")

    # 创建热力图数据
    heatmap_data = df.head(20).copy()
    heatmap_data['size'] = heatmap_data['价格'] / heatmap_data['价格'].max() * 100

    fig = px.treemap(
        heatmap_data,
        path=['货币'],
        values='size',
        color='24h涨跌',
        color_continuous_scale='RdYlGn',
        title="市场热力图 - 按市值大小和涨跌幅着色"
    )

    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

    # 侧边栏信息
    with st.sidebar:
        st.header("📋 页面信息")
        st.info("""
        **当前页面**: 货币概览

        **功能**:
        - 市场总体统计
        - 快速筛选和排序
        - 货币列表浏览
        - 市场热力图

        **操作提示**:
        - 点击表格行选择货币
        - 使用导航按钮跳转到其他功能
        - 筛选器可以快速过滤数据
        """)

        st.header("🔗 快速链接")
        st.markdown("""
        - [详细分析](/详细分析)
        - [货币比较](/货币比较)
        - [高级筛选](/高级筛选)
        - [实时仪表盘](/)
        """)

        # 显示比较列表
        if 'comparison_list' in st.session_state and st.session_state['comparison_list']:
            st.header("⚖️ 比较列表")
            for currency in st.session_state['comparison_list']:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(currency)
                with col2:
                    if st.button("❌", key=f"remove_{currency}"):
                        st.session_state['comparison_list'].remove(currency)
                        st.rerun()

            if st.button("🔍 开始比较", key="start_compare"):
                st.switch_page("pages/3_balance_currency_comparison.py")

    # 渲染页面底部
    render_footer()

if __name__ == "__main__":
    main()
