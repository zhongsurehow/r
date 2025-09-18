"""
通用图表工具模块
提供标准化的图表创建函数，减少代码重复
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple, Union
import streamlit as st

# 统一的颜色主题
class ChartTheme:
    """图表主题配置"""

    # 主要颜色
    PRIMARY = '#1f77b4'
    SUCCESS = '#2ca02c'
    WARNING = '#ff7f0e'
    DANGER = '#d62728'
    INFO = '#17a2b8'

    # 颜色序列
    COLORS = [
        '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
        '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
    ]

    # 背景和网格
    BACKGROUND = '#ffffff'
    GRID_COLOR = '#e6e6e6'

    # 字体
    FONT_FAMILY = 'Arial, sans-serif'
    FONT_SIZE = 12
    TITLE_SIZE = 16

def get_base_layout(title: str = "", height: int = 400) -> Dict[str, Any]:
    """获取基础布局配置"""
    return {
        'title': {
            'text': title,
            'font': {'size': ChartTheme.TITLE_SIZE, 'family': ChartTheme.FONT_FAMILY},
            'x': 0.5,
            'xanchor': 'center'
        },
        'height': height,
        'plot_bgcolor': ChartTheme.BACKGROUND,
        'paper_bgcolor': ChartTheme.BACKGROUND,
        'font': {'family': ChartTheme.FONT_FAMILY, 'size': ChartTheme.FONT_SIZE},
        'xaxis': {
            'gridcolor': ChartTheme.GRID_COLOR,
            'showgrid': True,
            'zeroline': False
        },
        'yaxis': {
            'gridcolor': ChartTheme.GRID_COLOR,
            'showgrid': True,
            'zeroline': False
        },
        'margin': {'l': 50, 'r': 50, 't': 80, 'b': 50}
    }

def create_styled_line_chart(
    x: List[Any],
    y: List[float],
    title: str = "",
    x_title: str = "",
    y_title: str = "",
    color: str = ChartTheme.PRIMARY,
    height: int = 400,
    show_markers: bool = False
) -> go.Figure:
    """创建标准化的线图"""

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=x,
        y=y,
        mode='lines+markers' if show_markers else 'lines',
        line=dict(color=color, width=2),
        marker=dict(size=6, color=color) if show_markers else None,
        name=title or "数据"
    ))

    layout = get_base_layout(title, height)
    layout['xaxis']['title'] = x_title
    layout['yaxis']['title'] = y_title

    fig.update_layout(**layout)
    return fig

def create_styled_bar_chart(
    x: List[Any],
    y: List[float],
    title: str = "",
    x_title: str = "",
    y_title: str = "",
    colors: Optional[List[str]] = None,
    height: int = 400,
    orientation: str = 'v'
) -> go.Figure:
    """创建标准化的柱状图"""

    fig = go.Figure()

    if colors is None:
        colors = [ChartTheme.PRIMARY] * len(x)
    elif len(colors) == 1:
        colors = colors * len(x)

    if orientation == 'v':
        fig.add_trace(go.Bar(
            x=x,
            y=y,
            marker_color=colors,
            name=title or "数据"
        ))
    else:
        fig.add_trace(go.Bar(
            x=y,
            y=x,
            orientation='h',
            marker_color=colors,
            name=title or "数据"
        ))

    layout = get_base_layout(title, height)
    layout['xaxis']['title'] = x_title
    layout['yaxis']['title'] = y_title

    fig.update_layout(**layout)
    return fig

def create_styled_pie_chart(
    values: List[float],
    labels: List[str],
    title: str = "",
    colors: Optional[List[str]] = None,
    height: int = 400,
    show_legend: bool = True
) -> go.Figure:
    """创建标准化的饼图"""

    if colors is None:
        colors = ChartTheme.COLORS[:len(values)]

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        marker_colors=colors,
        textinfo='label+percent',
        textposition='auto'
    )])

    layout = get_base_layout(title, height)
    layout['showlegend'] = show_legend

    fig.update_layout(**layout)
    return fig

def create_styled_heatmap(
    z: np.ndarray,
    x_labels: List[str],
    y_labels: List[str],
    title: str = "",
    colorscale: str = 'RdYlBu_r',
    height: int = 400,
    show_text: bool = True
) -> go.Figure:
    """创建标准化的热力图"""

    fig = go.Figure(data=go.Heatmap(
        z=z,
        x=x_labels,
        y=y_labels,
        colorscale=colorscale,
        text=z if show_text else None,
        texttemplate='%{text:.2f}' if show_text else None,
        textfont={"size": 10},
        hoverongaps=False
    ))

    layout = get_base_layout(title, height)
    fig.update_layout(**layout)
    return fig

def create_styled_scatter_chart(
    x: List[float],
    y: List[float],
    title: str = "",
    x_title: str = "",
    y_title: str = "",
    colors: Optional[List[str]] = None,
    sizes: Optional[List[float]] = None,
    text: Optional[List[str]] = None,
    height: int = 400
) -> go.Figure:
    """创建标准化的散点图"""

    fig = go.Figure()

    marker_dict = {
        'color': colors or ChartTheme.PRIMARY,
        'size': sizes or 8,
        'line': dict(width=1, color='white')
    }

    fig.add_trace(go.Scatter(
        x=x,
        y=y,
        mode='markers',
        marker=marker_dict,
        text=text,
        textposition='top center',
        name=title or "数据"
    ))

    layout = get_base_layout(title, height)
    layout['xaxis']['title'] = x_title
    layout['yaxis']['title'] = y_title

    fig.update_layout(**layout)
    return fig

def create_multi_line_chart(
    data: Dict[str, Tuple[List[Any], List[float]]],
    title: str = "",
    x_title: str = "",
    y_title: str = "",
    height: int = 400
) -> go.Figure:
    """创建多线图"""

    fig = go.Figure()

    for i, (name, (x_data, y_data)) in enumerate(data.items()):
        color = ChartTheme.COLORS[i % len(ChartTheme.COLORS)]

        fig.add_trace(go.Scatter(
            x=x_data,
            y=y_data,
            mode='lines',
            line=dict(color=color, width=2),
            name=name
        ))

    layout = get_base_layout(title, height)
    layout['xaxis']['title'] = x_title
    layout['yaxis']['title'] = y_title

    fig.update_layout(**layout)
    return fig

def create_candlestick_chart(
    df: pd.DataFrame,
    title: str = "",
    height: int = 400,
    volume: bool = False
) -> go.Figure:
    """创建K线图"""

    if volume:
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            subplot_titles=('价格', '成交量'),
            row_width=[0.2, 0.7]
        )

        # K线图
        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name="价格"
        ), row=1, col=1)

        # 成交量
        fig.add_trace(go.Bar(
            x=df.index,
            y=df['volume'],
            name="成交量",
            marker_color=ChartTheme.INFO
        ), row=2, col=1)

    else:
        fig = go.Figure(data=[go.Candlestick(
            x=df.index,
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close']
        )])

    layout = get_base_layout(title, height)
    fig.update_layout(**layout)
    fig.update_xaxes(rangeslider_visible=False)

    return fig

def create_gauge_chart(
    value: float,
    title: str = "",
    min_val: float = 0,
    max_val: float = 100,
    threshold_colors: Optional[Dict[str, Tuple[float, float]]] = None,
    height: int = 300
) -> go.Figure:
    """创建仪表盘图"""

    if threshold_colors is None:
        threshold_colors = {
            ChartTheme.SUCCESS: (0, 0.5),
            ChartTheme.WARNING: (0.5, 0.8),
            ChartTheme.DANGER: (0.8, 1.0)
        }

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title},
        delta={'reference': (max_val + min_val) / 2},
        gauge={
            'axis': {'range': [min_val, max_val]},
            'bar': {'color': ChartTheme.PRIMARY},
            'steps': [
                {'range': [min_val, max_val], 'color': ChartTheme.GRID_COLOR}
            ],
            'threshold': {
                'line': {'color': ChartTheme.DANGER, 'width': 4},
                'thickness': 0.75,
                'value': max_val * 0.9
            }
        }
    ))

    fig.update_layout(
        height=height,
        font={'family': ChartTheme.FONT_FAMILY, 'size': ChartTheme.FONT_SIZE}
    )

    return fig

def display_metric_cards(metrics: Dict[str, Dict[str, Any]], columns: int = 4):
    """显示指标卡片"""
    cols = st.columns(columns)

    for i, (key, metric) in enumerate(metrics.items()):
        with cols[i % columns]:
            st.metric(
                label=metric.get('label', key),
                value=metric.get('value', 0),
                delta=metric.get('delta'),
                delta_color=metric.get('delta_color', 'normal'),
                help=metric.get('help')
            )

def create_comparison_table(
    data: List[Dict[str, Any]],
    columns: List[str],
    title: str = "",
    sortable: bool = True,
    highlight_best: bool = False
) -> None:
    """创建对比表格"""

    if title:
        st.subheader(title)

    df = pd.DataFrame(data)

    if highlight_best and len(df) > 0:
        # 高亮最佳值（假设数值越大越好）
        for col in df.select_dtypes(include=[np.number]).columns:
            max_idx = df[col].idxmax()
            df.loc[max_idx, col] = f"**{df.loc[max_idx, col]}**"

    st.dataframe(
        df[columns] if columns else df,
        use_container_width=True,
        hide_index=True
    )

def add_chart_controls(
    chart_type: str = "line",
    show_grid: bool = True,
    show_legend: bool = True
) -> Dict[str, Any]:
    """添加图表控制选项"""

    with st.expander("📊 图表设置", expanded=False):
        col1, col2, col3 = st.columns(3)

        with col1:
            height = st.slider("图表高度", 300, 800, 400, 50)

        with col2:
            if chart_type in ['line', 'bar']:
                show_markers = st.checkbox("显示数据点", value=False)
            else:
                show_markers = False

        with col3:
            color_theme = st.selectbox(
                "颜色主题",
                ["默认", "蓝色", "绿色", "红色", "紫色"],
                index=0
            )

    theme_colors = {
        "默认": ChartTheme.COLORS,
        "蓝色": ['#1f77b4', '#aec7e8', '#c5dbf1'],
        "绿色": ['#2ca02c', '#98df8a', '#c4e8c4'],
        "红色": ['#d62728', '#ff9896', '#ffb3b3'],
        "紫色": ['#9467bd', '#c5b0d5', '#d4c4e8']
    }

    return {
        'height': height,
        'show_markers': show_markers,
        'colors': theme_colors[color_theme],
        'show_grid': show_grid,
        'show_legend': show_legend
    }
