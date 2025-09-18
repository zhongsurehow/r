"""
UI/UX增强组件
提供现代化的用户界面组件、交互效果和用户体验优化功能
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
import time


class ModernUI:
    """现代化UI组件类"""
    
    @staticmethod
    def create_metric_card(
        title: str,
        value: Union[str, int, float],
        delta: Optional[Union[str, int, float]] = None,
        delta_color: str = "normal",
        icon: str = "📊",
        help_text: str = ""
    ):
        """创建现代化指标卡片"""
        with st.container():
            col1, col2 = st.columns([1, 4])
            
            with col1:
                st.markdown(f"<div style='font-size: 2em; text-align: center;'>{icon}</div>", 
                           unsafe_allow_html=True)
            
            with col2:
                st.metric(
                    label=title,
                    value=value,
                    delta=delta,
                    delta_color=delta_color,
                    help=help_text
                )
    
    @staticmethod
    def create_progress_ring(
        value: float,
        max_value: float = 100,
        title: str = "",
        color: str = "#1f77b4",
        size: int = 200
    ):
        """创建环形进度条"""
        percentage = (value / max_value) * 100 if max_value > 0 else 0
        
        fig = go.Figure(data=[
            go.Pie(
                values=[percentage, 100 - percentage],
                hole=0.7,
                marker_colors=[color, "#f0f0f0"],
                textinfo="none",
                hoverinfo="none",
                showlegend=False
            )
        ])
        
        fig.update_layout(
            title={
                'text': f"<b>{title}</b><br><span style='font-size:24px'>{value:.1f}%</span>",
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'middle'
            },
            height=size,
            width=size,
            margin=dict(t=50, b=0, l=0, r=0),
            annotations=[
                dict(
                    text=f"{value:.1f}%",
                    x=0.5, y=0.5,
                    font_size=20,
                    showarrow=False
                )
            ]
        )
        
        return fig
    
    @staticmethod
    def create_status_badge(
        status: str,
        color_map: Dict[str, str] = None
    ) -> str:
        """创建状态徽章"""
        default_colors = {
            "success": "#28a745",
            "warning": "#ffc107", 
            "error": "#dc3545",
            "info": "#17a2b8",
            "active": "#007bff",
            "inactive": "#6c757d"
        }
        
        colors = color_map or default_colors
        color = colors.get(status.lower(), "#6c757d")
        
        return f"""
        <span style="
            background-color: {color};
            color: white;
            padding: 0.25rem 0.5rem;
            border-radius: 0.25rem;
            font-size: 0.875rem;
            font-weight: 500;
            text-transform: uppercase;
        ">{status}</span>
        """
    
    @staticmethod
    def create_animated_counter(
        target_value: Union[int, float],
        duration: float = 2.0,
        prefix: str = "",
        suffix: str = "",
        decimal_places: int = 0
    ):
        """创建动画计数器"""
        placeholder = st.empty()
        
        steps = 50
        step_value = target_value / steps
        step_duration = duration / steps
        
        for i in range(steps + 1):
            current_value = step_value * i
            if decimal_places > 0:
                display_value = f"{current_value:.{decimal_places}f}"
            else:
                display_value = f"{int(current_value)}"
            
            placeholder.markdown(
                f"<h2 style='text-align: center; color: #1f77b4;'>"
                f"{prefix}{display_value}{suffix}</h2>",
                unsafe_allow_html=True
            )
            
            if i < steps:
                time.sleep(step_duration)
    
    @staticmethod
    def create_gradient_background(
        gradient_colors: List[str] = ["#667eea", "#764ba2"],
        height: str = "200px"
    ) -> str:
        """创建渐变背景"""
        gradient = f"linear-gradient(135deg, {', '.join(gradient_colors)})"
        
        return f"""
        <div style="
            background: {gradient};
            height: {height};
            border-radius: 10px;
            margin: 1rem 0;
        "></div>
        """
    
    @staticmethod
    def create_floating_action_button(
        icon: str = "➕",
        tooltip: str = "添加",
        color: str = "#007bff"
    ) -> str:
        """创建浮动操作按钮"""
        return f"""
        <div style="
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 56px;
            height: 56px;
            background-color: {color};
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            cursor: pointer;
            z-index: 1000;
            transition: all 0.3s ease;
        " title="{tooltip}">
            <span style="font-size: 24px; color: white;">{icon}</span>
        </div>
        """


class InteractiveCharts:
    """交互式图表组件类"""
    
    @staticmethod
    def create_real_time_line_chart(
        data: pd.DataFrame,
        x_col: str,
        y_col: str,
        title: str = "实时数据",
        color: str = "#1f77b4"
    ):
        """创建实时折线图"""
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=data[x_col],
            y=data[y_col],
            mode='lines+markers',
            line=dict(color=color, width=3),
            marker=dict(size=6),
            name=title,
            hovertemplate='<b>%{y:.2f}</b><br>%{x}<extra></extra>'
        ))
        
        fig.update_layout(
            title=dict(
                text=title,
                x=0.5,
                font=dict(size=20, color='#2c3e50')
            ),
            xaxis=dict(
                showgrid=True,
                gridcolor='rgba(128,128,128,0.2)',
                title_font=dict(size=14)
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='rgba(128,128,128,0.2)',
                title_font=dict(size=14)
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            hovermode='x unified',
            margin=dict(t=60, b=40, l=40, r=40)
        )
        
        return fig
    
    @staticmethod
    def create_gauge_chart(
        value: float,
        title: str = "指标",
        min_val: float = 0,
        max_val: float = 100,
        threshold_ranges: List[Dict] = None
    ):
        """创建仪表盘图表"""
        if threshold_ranges is None:
            threshold_ranges = [
                {'range': [0, 30], 'color': "#dc3545"},
                {'range': [30, 70], 'color': "#ffc107"},
                {'range': [70, 100], 'color': "#28a745"}
            ]
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=value,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': title, 'font': {'size': 20}},
            delta={'reference': (min_val + max_val) / 2},
            gauge={
                'axis': {'range': [min_val, max_val], 'tickwidth': 1},
                'bar': {'color': "#1f77b4"},
                'steps': [
                    {'range': [r['range'][0], r['range'][1]], 'color': r['color']}
                    for r in threshold_ranges
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': value
                }
            }
        ))
        
        fig.update_layout(
            height=300,
            margin=dict(t=40, b=40, l=40, r=40),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig
    
    @staticmethod
    def create_heatmap_calendar(
        data: pd.DataFrame,
        date_col: str,
        value_col: str,
        title: str = "活动热力图"
    ):
        """创建日历热力图"""
        # 准备数据
        data[date_col] = pd.to_datetime(data[date_col])
        data['day_of_week'] = data[date_col].dt.day_name()
        data['week_of_year'] = data[date_col].dt.isocalendar().week
        
        # 创建透视表
        pivot_data = data.pivot_table(
            values=value_col,
            index='day_of_week',
            columns='week_of_year',
            aggfunc='mean',
            fill_value=0
        )
        
        fig = go.Figure(data=go.Heatmap(
            z=pivot_data.values,
            x=pivot_data.columns,
            y=pivot_data.index,
            colorscale='Viridis',
            hoverongaps=False,
            hovertemplate='周 %{x}<br>%{y}<br>值: %{z:.2f}<extra></extra>'
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title="周数",
            yaxis_title="星期",
            height=300
        )
        
        return fig


class NotificationSystem:
    """通知系统类"""
    
    @staticmethod
    def show_toast(
        message: str,
        type: str = "info",
        duration: int = 3000,
        position: str = "top-right"
    ):
        """显示Toast通知"""
        type_colors = {
            "success": "#28a745",
            "warning": "#ffc107",
            "error": "#dc3545",
            "info": "#17a2b8"
        }
        
        color = type_colors.get(type, "#17a2b8")
        
        toast_html = f"""
        <div id="toast-{int(time.time())}" style="
            position: fixed;
            {position.split('-')[0]}: 20px;
            {position.split('-')[1]}: 20px;
            background-color: {color};
            color: white;
            padding: 12px 20px;
            border-radius: 6px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 9999;
            font-weight: 500;
            animation: slideIn 0.3s ease-out;
        ">
            {message}
        </div>
        
        <style>
        @keyframes slideIn {{
            from {{ opacity: 0; transform: translateX(100%); }}
            to {{ opacity: 1; transform: translateX(0); }}
        }}
        </style>
        
        <script>
        setTimeout(function() {{
            var toast = document.getElementById('toast-{int(time.time())}');
            if (toast) {{
                toast.style.animation = 'slideOut 0.3s ease-in';
                setTimeout(function() {{
                    toast.remove();
                }}, 300);
            }}
        }}, {duration});
        </script>
        """
        
        st.markdown(toast_html, unsafe_allow_html=True)
    
    @staticmethod
    def show_modal(
        title: str,
        content: str,
        show_close: bool = True
    ):
        """显示模态框"""
        modal_html = f"""
        <div id="modal-overlay" style="
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.5);
            z-index: 10000;
            display: flex;
            align-items: center;
            justify-content: center;
        ">
            <div style="
                background: white;
                border-radius: 8px;
                padding: 24px;
                max-width: 500px;
                width: 90%;
                box-shadow: 0 8px 32px rgba(0,0,0,0.3);
                animation: modalIn 0.3s ease-out;
            ">
                <div style="
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 16px;
                ">
                    <h3 style="margin: 0; color: #2c3e50;">{title}</h3>
                    {f'<button onclick="closeModal()" style="background: none; border: none; font-size: 24px; cursor: pointer;">&times;</button>' if show_close else ''}
                </div>
                <div style="color: #555;">
                    {content}
                </div>
            </div>
        </div>
        
        <style>
        @keyframes modalIn {{
            from {{ opacity: 0; transform: scale(0.8); }}
            to {{ opacity: 1; transform: scale(1); }}
        }}
        </style>
        
        <script>
        function closeModal() {{
            document.getElementById('modal-overlay').remove();
        }}
        </script>
        """
        
        st.markdown(modal_html, unsafe_allow_html=True)


class LoadingAnimations:
    """加载动画类"""
    
    @staticmethod
    def show_spinner(
        text: str = "加载中...",
        color: str = "#1f77b4"
    ):
        """显示旋转加载动画"""
        spinner_html = f"""
        <div style="
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        ">
            <div style="
                border: 4px solid #f3f3f3;
                border-top: 4px solid {color};
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin-right: 12px;
            "></div>
            <span style="color: {color}; font-weight: 500;">{text}</span>
        </div>
        
        <style>
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        </style>
        """
        
        return st.markdown(spinner_html, unsafe_allow_html=True)
    
    @staticmethod
    def show_progress_bar(
        progress: float,
        text: str = "",
        color: str = "#1f77b4",
        height: str = "8px"
    ):
        """显示进度条"""
        progress_html = f"""
        <div style="margin: 16px 0;">
            {f'<div style="margin-bottom: 8px; color: #555; font-weight: 500;">{text}</div>' if text else ''}
            <div style="
                width: 100%;
                background-color: #f0f0f0;
                border-radius: 4px;
                overflow: hidden;
                height: {height};
            ">
                <div style="
                    width: {progress}%;
                    height: 100%;
                    background-color: {color};
                    transition: width 0.3s ease;
                "></div>
            </div>
            <div style="
                text-align: right;
                margin-top: 4px;
                font-size: 12px;
                color: #666;
            ">{progress:.1f}%</div>
        </div>
        """
        
        return st.markdown(progress_html, unsafe_allow_html=True)


def apply_custom_css():
    """应用自定义CSS样式"""
    custom_css = """
    <style>
    /* 主题色彩 */
    :root {
        --primary-color: #1f77b4;
        --secondary-color: #ff7f0e;
        --success-color: #28a745;
        --warning-color: #ffc107;
        --error-color: #dc3545;
        --info-color: #17a2b8;
        --light-bg: #f8f9fa;
        --dark-text: #2c3e50;
    }
    
    /* 隐藏Streamlit默认元素 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 自定义容器样式 */
    .main-container {
        padding: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    /* 卡片样式 */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-left: 4px solid var(--primary-color);
        margin: 1rem 0;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0,0,0,0.15);
    }
    
    /* 按钮样式 */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    
    /* 侧边栏样式 */
    .css-1d391kg {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    /* 指标样式 */
    [data-testid="metric-container"] {
        background: white;
        border: 1px solid #e0e0e0;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* 表格样式 */
    .dataframe {
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* 动画效果 */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.5s ease-out;
    }
    
    /* 响应式设计 */
    @media (max-width: 768px) {
        .main-container {
            padding: 0.5rem;
            margin: 0.5rem 0;
        }
        
        .metric-card {
            padding: 1rem;
            margin: 0.5rem 0;
        }
    }
    </style>
    """
    
    st.markdown(custom_css, unsafe_allow_html=True)


def create_enhanced_dashboard():
    """创建增强版仪表板"""
    apply_custom_css()
    
    # 页面标题
    st.markdown("""
    <div class="main-container fade-in">
        <h1 style="color: white; text-align: center; margin: 0;">
            🚀 交易智能分析平台
        </h1>
        <p style="color: rgba(255,255,255,0.8); text-align: center; margin: 0.5rem 0 0 0;">
            专业级加密货币套利交易系统
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 创建指标卡片
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        ModernUI.create_metric_card(
            title="活跃交易所",
            value=5,
            delta="+1",
            icon="🏢",
            help_text="当前连接的交易所数量"
        )
    
    with col2:
        ModernUI.create_metric_card(
            title="监控币种",
            value=12,
            delta="+3",
            icon="💰",
            help_text="正在监控的交易对数量"
        )
    
    with col3:
        ModernUI.create_metric_card(
            title="套利机会",
            value=8,
            delta="+2",
            delta_color="normal",
            icon="⚡",
            help_text="当前可用的套利机会"
        )
    
    with col4:
        ModernUI.create_metric_card(
            title="预期收益",
            value="2.3%",
            delta="+0.5%",
            delta_color="normal",
            icon="📈",
            help_text="预期年化收益率"
        )
    
    # 创建图表区域
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📊 实时价格走势")
        # 这里可以添加实时价格图表
        sample_data = pd.DataFrame({
            'time': pd.date_range('2024-01-01', periods=100, freq='1H'),
            'price': np.random.randn(100).cumsum() + 100
        })
        
        fig = InteractiveCharts.create_real_time_line_chart(
            sample_data, 'time', 'price', 'BTC/USDT价格'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎯 性能指标")
        
        # 创建仪表盘
        gauge_fig = InteractiveCharts.create_gauge_chart(
            value=75.5,
            title="系统健康度",
            min_val=0,
            max_val=100
        )
        st.plotly_chart(gauge_fig, use_container_width=True)
        
        # 创建环形进度条
        progress_fig = ModernUI.create_progress_ring(
            value=85.2,
            title="缓存命中率",
            color="#28a745"
        )
        st.plotly_chart(progress_fig, use_container_width=True)