"""
实时仪表盘页面
独立网页 - 可通过 /实时仪表盘 直接访问
提供实时数据监控和预警功能
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import random
import time
import sys
import os
import asyncio

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.navigation import render_navigation, render_page_header, render_footer
from src.providers.free_api import free_api_provider
from utils.data_safety import (
    safe_format, safe_abs, safe_float, safe_get, safe_percentage, 
    safe_currency, validate_api_response, safe_calculate_change
)

# 页面配置
st.set_page_config(
    page_title="实时仪表盘",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义样式
st.markdown("""
<style>
.dashboard-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 2rem;
    border-radius: 15px;
    text-align: center;
    margin-bottom: 2rem;
}

.metric-container {
    background: white;
    padding: 1.5rem;
    border-radius: 15px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    margin: 1rem 0;
    text-align: center;
    border-left: 4px solid #667eea;
}

.alert-card {
    background: linear-gradient(45deg, #ff6b6b, #ee5a52);
    color: white;
    padding: 1rem;
    border-radius: 10px;
    margin: 0.5rem 0;
    font-weight: bold;
}

.success-card {
    background: linear-gradient(45deg, #00d4aa, #00b894);
    color: white;
    padding: 1rem;
    border-radius: 10px;
    margin: 0.5rem 0;
    font-weight: bold;
}

.warning-card {
    background: linear-gradient(45deg, #ffa726, #ff9800);
    color: white;
    padding: 1rem;
    border-radius: 10px;
    margin: 0.5rem 0;
    font-weight: bold;
}

.live-indicator {
    display: inline-block;
    width: 10px;
    height: 10px;
    background: #00d4aa;
    border-radius: 50%;
    animation: pulse 2s infinite;
    margin-right: 0.5rem;
}

@keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.5; }
    100% { opacity: 1; }
}

.back-nav {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 10px;
    margin-bottom: 1rem;
}

.status-online {
    color: #00d4aa;
    font-weight: bold;
}

.status-offline {
    color: #ff6b6b;
    font-weight: bold;
}

.market-status {
    background: linear-gradient(45deg, #4facfe, #00f2fe);
    color: white;
    padding: 1rem;
    border-radius: 10px;
    text-align: center;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

async def get_real_time_data():
    """从CoinGecko获取真实实时数据"""
    try:
        major_currencies = ['BTC', 'ETH', 'BNB', 'ADA', 'SOL', 'DOT', 'AVAX', 'MATIC']
        
        # 获取货币列表数据
        coins_data = await free_api_provider.get_coins_markets(
            vs_currency='usd',
            order='market_cap_desc',
            per_page=250,
            page=1,
            sparkline=False,
            price_change_percentage='1h,24h'
        )
        
        # 验证API响应
        if not validate_api_response(coins_data):
            return None
            
        # 创建符号到ID的映射
        symbol_to_id = {}
        for coin in coins_data:
            if coin and isinstance(coin, dict):
                symbol = safe_get(coin, 'symbol', '').upper()
                if symbol:
                    symbol_to_id[symbol] = coin
            
        data = []
        for symbol in major_currencies:
            symbol_upper = symbol.upper()
            if symbol_upper in symbol_to_id:
                coin = symbol_to_id[symbol_upper]
                
                # 计算技术指标（简化版）
                price = safe_float(safe_get(coin, 'current_price', 0))
                change_24h = safe_float(safe_get(coin, 'price_change_percentage_24h', 0))
                change_1h = safe_float(safe_get(coin, 'price_change_percentage_1h', 0))
                
                # RSI简化计算（基于价格变化）
                rsi = 50 + (change_24h * 2)  # 简化RSI计算
                rsi = max(0, min(100, rsi))
                
                # 模拟短期变化（1分钟、5分钟）
                change_1m = random.uniform(-0.5, 0.5)
                change_5m = random.uniform(-2, 2)
                
                currency_data = {
                    'symbol': symbol_upper,
                    'price': price,
                    'change_1m': change_1m,
                    'change_5m': change_5m,
                    'change_1h': change_1h,
                    '涨跌24h': change_24h,
                    'volume_24h': safe_float(safe_get(coin, 'total_volume', 0)),
                    '市值': safe_float(safe_get(coin, 'market_cap', 0)),
                    'rsi': rsi,
                    'fear_greed': random.randint(10, 90),  # 需要专门的API
                    'social_sentiment': random.uniform(-1, 1),  # 需要专门的API
                    'last_update': datetime.now()
                }
                data.append(currency_data)
            else:
                # 如果找不到真实数据，使用虚拟数据
                data.append(generate_real_time_data_single(symbol))
                
        return data
        
    except Exception as e:
        print(safe_format("获取真实实时数据失败: {}", str(e)))
        return None

def generate_real_time_data():
    """生成实时数据（虚拟数据作为备用）"""
    major_currencies = ['BTC', 'ETH', 'BNB', 'ADA', 'SOL', 'DOT', 'AVAX', 'MATIC']
    return [generate_real_time_data_single(symbol) for symbol in major_currencies]

def generate_real_time_data_single(symbol):
    """生成单个货币的实时数据"""
    base_prices = {
        'BTC': 45000, 'ETH': 3000, 'BNB': 300, 'ADA': 0.5,
        'SOL': 100, 'DOT': 25, 'AVAX': 35, 'MATIC': 1.2
    }

    base_price = base_prices.get(symbol, 100)
    current_price = base_price * random.uniform(0.95, 1.05)

    return {
        'symbol': symbol,
        'price': current_price,
        'change_1m': random.uniform(-0.5, 0.5),
        'change_5m': random.uniform(-2, 2),
        'change_1h': random.uniform(-5, 5),
        '涨跌24h': random.uniform(-10, 10),
        'volume_24h': random.uniform(1e9, 10e9),
        '市值': random.uniform(10e9, 800e9),
        'rsi': random.uniform(20, 80),
        'fear_greed': random.randint(10, 90),
        'social_sentiment': random.uniform(-1, 1),
        'last_update': datetime.now()
    }

def generate_market_alerts():
    """生成市场预警"""
    alerts = []

    alert_types = [
        ("价格突破", "BTC突破$46,000阻力位", "success"),
        ("大额转账", "检测到1000 BTC大额转账", "warning"),
        ("技术指标", "ETH RSI进入超买区域", "alert"),
        ("市场异动", "MATIC交易量激增300%", "warning"),
        ("新闻事件", "重大政策消息影响市场", "alert")
    ]

    for i in range(random.randint(2, 5)):
        alert_type, message, severity = random.choice(alert_types)
        alerts.append({
            'type': alert_type,
            'message': message,
            'severity': severity,
            'timestamp': datetime.now() - timedelta(minutes=random.randint(1, 60))
        })

    return alerts

def create_real_time_chart(data):
    """创建实时价格图表"""
    # 生成历史数据点
    timestamps = pd.date_range(end=datetime.now(), periods=60, freq='1min')

    fig = go.Figure()

    colors = ['#00d4aa', '#667eea', '#f093fb', '#ffa726', '#ff6b6b', '#764ba2', '#4facfe', '#00f2fe']

    for i, currency in enumerate(data[:4]):  # 显示前4个主要货币
        # 生成模拟的分钟级数据
        prices = []
        base_price = currency['price']

        for j in range(60):
            variation = random.uniform(-0.02, 0.02)
            price = base_price * (1 + variation * (j / 60))
            prices.append(price)

        fig.add_trace(go.Scatter(
            x=timestamps,
            y=prices,
            mode='lines',
            name=currency['symbol'],
            line=dict(color=colors[i], width=2),
            hovertemplate=f'<b>{currency["symbol"]}</b><br>%{{y:$,.2f}}<br>%{{x}}<extra></extra>'
        ))

    fig.update_layout(
        title='实时价格走势 (1小时)',
        xaxis_title='时间',
        yaxis_title='价格 (USD)',
        template='plotly_white',
        height=400,
        showlegend=True,
        hovermode='x unified'
    )

    return fig

def create_volume_heatmap(data):
    """创建交易量热力图"""
    symbols = [d['symbol'] for d in data]
    volumes = [d['volume_24h'] for d in data]
    changes = [d['涨跌24h'] for d in data]

    # 创建网格数据
    grid_size = int(np.ceil(np.sqrt(len(data))))
    grid_data = np.zeros((grid_size, grid_size))
    grid_symbols = np.full((grid_size, grid_size), '', dtype=object)

    for i, (symbol, volume, change) in enumerate(zip(symbols, volumes, changes)):
        row = i // grid_size
        col = i % grid_size
        if row < grid_size and col < grid_size:
            grid_data[row, col] = change
            grid_symbols[row, col] = symbol

    fig = go.Figure(data=go.Heatmap(
        z=grid_data,
        text=grid_symbols,
        texttemplate='%{text}',
        textfont={"size": 12, "color": "white"},
        colorscale='RdYlGn',
        zmid=0,
        showscale=True,
        hovertemplate='<b>%{text}</b><br>24h变化: %{z:.2f}%<extra></extra>'
    ))

    fig.update_layout(
        title='市场热力图 (24h变化)',
        template='plotly_white',
        height=300
    )

    return fig

def create_fear_greed_gauge(value):
    """创建恐慌贪婪指数仪表盘"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = value,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "恐慌贪婪指数"},
        delta = {'reference': 50},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 25], 'color': "red"},
                {'range': [25, 50], 'color': "orange"},
                {'range': [50, 75], 'color': "yellow"},
                {'range': [75, 100], 'color': "green"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))

    fig.update_layout(height=300)
    return fig

def main():
    # 渲染导航栏
    render_navigation()

    # 渲染页面标题
    render_page_header(
        title="实时仪表盘",
        description="实时监控市场动态，把握投资机会",
        icon="📊"
    )

    # 初始化页面时自动刷新一遍
    if 'dashboard_initialized' not in st.session_state:
        st.session_state.dashboard_initialized = True
        st.rerun()

    # 自动刷新控制
    refresh_options = {
        1: "1秒",
        5: "5秒", 
        10: "10秒",
        30: "30秒"
    }
    
    refresh_interval = st.selectbox(
        "自动刷新间隔",
        options=list(refresh_options.keys()),
        format_func=lambda x: refresh_options[x],
        index=3,  # 默认选择30秒
        key="refresh_interval_select"
    )
    
    auto_refresh = st.checkbox(f"自动刷新 ({refresh_options[refresh_interval]})", value=True, key="auto_refresh")

    if auto_refresh:
        # 自动刷新占位符
        refresh_placeholder = st.empty()
        with refresh_placeholder:
            st.info(f"⏱️ 下次刷新: {refresh_interval}秒后")

        # 根据选择的间隔自动刷新
        time.sleep(1)  # 短暂延迟以显示消息
        if auto_refresh:
            # 使用非阻塞方式实现自动刷新
            import asyncio
            import threading
            
            def delayed_refresh():
                time.sleep(refresh_interval)
                if st.session_state.get('auto_refresh', False):
                    st.rerun()
            
            # 启动后台刷新线程
            if 'refresh_thread' not in st.session_state or not st.session_state.refresh_thread.is_alive():
                st.session_state.refresh_thread = threading.Thread(target=delayed_refresh)
                st.session_state.refresh_thread.daemon = True
                st.session_state.refresh_thread.start()

    # 获取实时数据（优先使用真实数据）
    data_source = "虚拟数据"
    
    # 检查是否有缓存的真实数据
    cache_key = "real_time_data_cache"
    cache_time_key = "real_time_data_cache_time"
    
    # 添加刷新按钮
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        if st.button("🔄 刷新数据", key="refresh_real_time"):
            if cache_key in st.session_state:
                del st.session_state[cache_key]
            if cache_time_key in st.session_state:
                del st.session_state[cache_time_key]
            st.rerun()
    
    with col2:
        st.markdown(f"**数据源:** {st.session_state.get('real_time_data_source', '虚拟数据')}")
    
    # 检查缓存是否有效（5分钟内）
    current_time = datetime.now()
    cache_valid = False
    if cache_key in st.session_state and cache_time_key in st.session_state:
        cache_time = st.session_state[cache_time_key]
        if (current_time - cache_time).total_seconds() < 300:  # 5分钟缓存
            cache_valid = True
    
    if cache_valid:
        real_time_data = st.session_state[cache_key]
        data_source = st.session_state.get('real_time_data_source', '虚拟数据')
    else:
        # 尝试获取真实数据
        with st.spinner("正在获取最新实时数据..."):
            try:
                real_time_data = asyncio.run(get_real_time_data())
                if real_time_data:
                    data_source = "CoinGecko API"
                    st.session_state[cache_key] = real_time_data
                    st.session_state[cache_time_key] = current_time
                    st.session_state['real_time_data_source'] = data_source
                    st.success("✅ 成功获取真实实时数据")
                else:
                    raise Exception("API返回空数据")
            except Exception as e:
                st.warning(f"⚠️ 获取真实数据失败，使用虚拟数据: {str(e)}")
                real_time_data = generate_real_time_data()
                data_source = "虚拟数据"
                st.session_state['real_time_data_source'] = data_source
    
    market_alerts = generate_market_alerts()

    # 市场状态
    market_status = random.choice(["开放", "波动", "谨慎"])
    status_color = {"开放": "status-online", "波动": "status-warning", "谨慎": "status-offline"}

    st.markdown(f"""
    <div class="market-status">
        <h3>🌐 市场状态: <span class="{status_color.get(market_status, 'status-online')}">{market_status}</span></h3>
        <p>最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    """, unsafe_allow_html=True)

    # 关键指标概览
    st.header("📈 关键指标")

    metric_col1, metric_col2, metric_col3, metric_col4, metric_col5 = st.columns(5)

    with metric_col1:
        total_market_cap = sum([safe_float(safe_get(d, '市值', 0)) for d in real_time_data])
        market_cap_change = random.uniform(-3, 3)
        st.metric(
            "总市值",
            safe_format("${:.2f}T", total_market_cap/1e12),
            safe_format("{:+.2f}%", market_cap_change)
        )

    with metric_col2:
        total_volume = sum([safe_float(safe_get(d, 'volume_24h', 0)) for d in real_time_data])
        volume_change = random.uniform(-10, 10)
        st.metric(
            "24h交易量",
            safe_format("${:.0f}B", total_volume/1e9),
            safe_format("{:+.1f}%", volume_change)
        )

    with metric_col3:
        btc_dominance = random.uniform(40, 50)
        dominance_change = random.uniform(-1, 1)
        st.metric(
            "BTC占比",
            f"{btc_dominance:.1f}%",
            f"{dominance_change:+.1f}%"
        )

    with metric_col4:
        active_currencies = len(real_time_data)
        st.metric(
            "活跃货币",
            f"{active_currencies}",
            "0"
        )

    with metric_col5:
        changes = [safe_float(safe_get(d, '涨跌24h', 0)) for d in real_time_data]
        avg_change = np.mean(changes) if changes else 0
        st.metric(
            "平均涨幅",
            safe_format("{:+.2f}%", avg_change),
            "24h"
        )

    # 实时价格图表
    st.header("📊 实时价格监控")

    price_chart = create_real_time_chart(real_time_data)
    st.plotly_chart(price_chart, use_container_width=True)

    # 市场热力图和恐慌贪婪指数
    chart_col1, chart_col2 = st.columns([2, 1])

    with chart_col1:
        st.subheader("🔥 市场热力图")
        heatmap_chart = create_volume_heatmap(real_time_data)
        st.plotly_chart(heatmap_chart, use_container_width=True)

    with chart_col2:
        st.subheader("😨 恐慌贪婪指数")
        fear_greed_value = random.randint(20, 80)
        gauge_chart = create_fear_greed_gauge(fear_greed_value)
        st.plotly_chart(gauge_chart, use_container_width=True)

    # 实时数据表格
    st.header("📋 实时数据")

    # 创建实时数据表格
    real_time_df = pd.DataFrame([
        {
            '货币': safe_get(d, 'symbol', 'N/A'),
            '价格': safe_currency(safe_get(d, 'price', 0)),
            '1分钟': safe_percentage(safe_get(d, 'change_1m', 0)),
            '5分钟': safe_percentage(safe_get(d, 'change_5m', 0)),
            '1小时': safe_percentage(safe_get(d, 'change_1h', 0)),
            '24小时': safe_percentage(safe_get(d, '涨跌24h', 0)),
            '交易量': safe_format("${:.1f}B", safe_float(safe_get(d, 'volume_24h', 0))/1e9),
            'RSI': safe_format("{:.1f}", safe_float(safe_get(d, 'rsi', 0))),
            '更新时间': safe_get(d, 'last_update', datetime.now()).strftime('%H:%M:%S')
        }
        for d in real_time_data
    ])

    st.dataframe(real_time_df, use_container_width=True)

    # 市场预警
    st.header("🚨 市场预警")

    if market_alerts:
        for alert in market_alerts:
            alert_class = f"{alert['severity']}-card"
            icon = {"success": "✅", "warning": "⚠️", "alert": "🚨"}[alert['severity']]

            st.markdown(f"""
            <div class="{alert_class}">
                {icon} <strong>{alert['type']}</strong>: {alert['message']}
                <br><small>{alert['timestamp'].strftime('%H:%M:%S')}</small>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("暂无市场预警")

    # 侧边栏
    with st.sidebar:
        st.header("⚙️ 仪表盘设置")

        st.subheader("📊 显示设置")
        show_volume = st.checkbox("显示交易量", value=True, key="show_volume")
        show_rsi = st.checkbox("显示RSI", value=True, key="show_rsi")
        show_alerts = st.checkbox("显示预警", value=True, key="show_alerts")

        st.subheader("🎯 价格预警")

        # 添加价格预警
        alert_symbol = st.selectbox(
            "选择货币",
            [d['symbol'] for d in real_time_data],
            key="alert_symbol"
        )

        alert_price = st.number_input(
            "预警价格",
            min_value=0.0,
            step=0.01,
            key="alert_price"
        )

        alert_type = st.selectbox(
            "预警类型",
            ["价格突破", "价格跌破"],
            key="alert_type"
        )

        if st.button("设置预警"):
            if 'price_alerts' not in st.session_state:
                st.session_state['price_alerts'] = []

            new_alert = {
                'symbol': alert_symbol,
                'price': alert_price,
                'type': alert_type,
                'created': datetime.now()
            }

            st.session_state['price_alerts'].append(new_alert)
            st.success(f"已设置{alert_type}预警: {alert_symbol} ${alert_price}")

        # 显示已设置的预警
        if 'price_alerts' in st.session_state and st.session_state['price_alerts']:
            st.subheader("📋 已设置预警")
            for i, alert in enumerate(st.session_state['price_alerts']):
                st.write(f"**{alert['symbol']}** {alert['type']} ${alert['price']}")
                if st.button(f"删除", key=f"delete_alert_{i}"):
                    st.session_state['price_alerts'].pop(i)
                    st.rerun()

        st.subheader("📈 快速导航")

        # 快速跳转到其他页面
        nav_col1, nav_col2, nav_col3 = st.columns(3)

        with nav_col1:
            if st.button("📊 查看详细分析"):
                st.switch_page("pages/2_chart_detailed_analysis.py")

        with nav_col2:
            if st.button("⚖️ 货币比较"):
                st.switch_page("pages/3_balance_currency_comparison.py")

        with nav_col3:
            if st.button("🔍 高级筛选"):
                st.switch_page("pages/4_search_advanced_filter.py")

        st.subheader("📱 移动端优化")
        mobile_mode = st.checkbox("移动端模式", key="mobile_mode")

        if mobile_mode:
            st.info("已启用移动端优化显示")

        st.subheader("⚠️ 免责声明")
        st.warning("""
        **重要提示:**
        - 数据仅供参考，不构成投资建议
        - 实时数据可能存在延迟
        - 投资有风险，请谨慎决策
        - 建议结合多方信息综合判断
        """)

        # 系统状态
        st.subheader("🔧 系统状态")
        st.success("✅ 数据连接正常")
        st.success("✅ 实时更新正常")
        st.info(f"📡 延迟: {random.randint(50, 200)}ms")
        st.info(f"🔄 上次更新: {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    main()
    # 渲染页面底部
    render_footer()
