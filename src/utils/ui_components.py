"""
统一UI组件工具
整合重复的Streamlit组件模式
"""

import streamlit as st
from typing import List, Dict, Any, Optional, Union, Tuple
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

class UIComponents:
    """统一UI组件类"""

    @staticmethod
    def create_metrics_row(metrics: Dict[str, Any], columns: int = 4, deltas: Dict[str, str] = None) -> None:
        """
        创建指标行

        Args:
            metrics: 指标字典 {label: value}
            columns: 列数
            deltas: 变化值字典 {label: delta}
        """
        if not metrics:
            return

        cols = st.columns(columns)
        metric_items = list(metrics.items())

        for i, (label, value) in enumerate(metric_items):
            col_index = i % columns
            delta = deltas.get(label) if deltas else None

            with cols[col_index]:
                st.metric(label, value, delta=delta)

    @staticmethod
    def create_kpi_dashboard(kpi_data: Dict[str, Any], title: str = "关键指标") -> None:
        """
        创建KPI仪表盘

        Args:
            kpi_data: KPI数据字典
            title: 标题
        """
        st.subheader(title)

        # 分组显示KPI
        if len(kpi_data) <= 4:
            UIComponents.create_metrics_row(kpi_data, len(kpi_data))
        else:
            # 分两行显示
            items = list(kpi_data.items())
            mid = len(items) // 2

            first_half = dict(items[:mid])
            second_half = dict(items[mid:])

            UIComponents.create_metrics_row(first_half, len(first_half))
            UIComponents.create_metrics_row(second_half, len(second_half))

    @staticmethod
    def create_filter_section(
        filters: Dict[str, Any],
        columns: int = 3,
        title: str = "筛选条件"
    ) -> Dict[str, Any]:
        """
        创建筛选区域

        Args:
            filters: 筛选器配置
            columns: 列数
            title: 标题

        Returns:
            筛选结果字典
        """
        st.subheader(title)
        cols = st.columns(columns)
        results = {}

        filter_items = list(filters.items())
        for i, (key, config) in enumerate(filter_items):
            col_index = i % columns

            with cols[col_index]:
                if config['type'] == 'selectbox':
                    results[key] = st.selectbox(
                        config['label'],
                        config['options'],
                        index=config.get('index', 0)
                    )
                elif config['type'] == 'multiselect':
                    results[key] = st.multiselect(
                        config['label'],
                        config['options'],
                        default=config.get('default', [])
                    )
                elif config['type'] == 'slider':
                    results[key] = st.slider(
                        config['label'],
                        min_value=config['min_value'],
                        max_value=config['max_value'],
                        value=config.get('value', config['min_value'])
                    )
                elif config['type'] == 'number_input':
                    results[key] = st.number_input(
                        config['label'],
                        min_value=config.get('min_value'),
                        max_value=config.get('max_value'),
                        value=config.get('value', 0)
                    )

        return results

    @staticmethod
    def create_data_table(
        data: pd.DataFrame,
        title: str = "数据表格",
        show_metrics: bool = True,
        height: int = 400
    ) -> None:
        """
        创建数据表格

        Args:
            data: DataFrame数据
            title: 标题
            show_metrics: 是否显示统计指标
            height: 表格高度
        """
        st.subheader(title)

        if show_metrics and not data.empty:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("总记录数", len(data))
            with col2:
                st.metric("列数", len(data.columns))
            with col3:
                if 'timestamp' in data.columns:
                    st.metric("时间范围", f"{data['timestamp'].min().strftime('%m-%d')} 至 {data['timestamp'].max().strftime('%m-%d')}")
                else:
                    st.metric("数据类型", "静态数据")
            with col4:
                numeric_cols = data.select_dtypes(include=['number']).columns
                st.metric("数值列", len(numeric_cols))

        # 显示表格
        st.dataframe(data, height=height, use_container_width=True)

    @staticmethod
    def create_chart_container(
        chart_func,
        title: str,
        description: str = None,
        full_width: bool = True
    ) -> None:
        """
        创建图表容器

        Args:
            chart_func: 图表生成函数
            title: 标题
            description: 描述
            full_width: 是否全宽
        """
        with st.container():
            st.subheader(title)
            if description:
                st.caption(description)

            if full_width:
                chart_func()
            else:
                col1, col2 = st.columns([3, 1])
                with col1:
                    chart_func()

    @staticmethod
    def create_status_indicators(
        statuses: Dict[str, str],
        title: str = "状态监控"
    ) -> None:
        """
        创建状态指示器

        Args:
            statuses: 状态字典 {name: status}
            title: 标题
        """
        st.subheader(title)
        cols = st.columns(len(statuses))

        status_colors = {
            '正常': '🟢',
            '健康': '🟢',
            '警告': '🟡',
            '延迟': '🟡',
            '异常': '🔴',
            '错误': '🔴',
            '离线': '⚫'
        }

        for i, (name, status) in enumerate(statuses.items()):
            with cols[i]:
                color = status_colors.get(status, '⚪')
                st.metric(name, f"{color} {status}")

    @staticmethod
    def create_action_buttons(
        actions: Dict[str, Dict[str, Any]],
        columns: int = 3
    ) -> Dict[str, bool]:
        """
        创建操作按钮组

        Args:
            actions: 操作配置 {key: {label, type, help}}
            columns: 列数

        Returns:
            按钮点击状态字典
        """
        cols = st.columns(columns)
        results = {}

        action_items = list(actions.items())
        for i, (key, config) in enumerate(action_items):
            col_index = i % columns

            with cols[col_index]:
                button_type = config.get('type', 'secondary')
                help_text = config.get('help', '')

                if button_type == 'primary':
                    results[key] = st.button(
                        config['label'],
                        type='primary',
                        help=help_text,
                        use_container_width=True
                    )
                else:
                    results[key] = st.button(
                        config['label'],
                        help=help_text,
                        use_container_width=True
                    )

        return results

    @staticmethod
    def create_progress_section(
        progress_data: Dict[str, float],
        title: str = "进度监控"
    ) -> None:
        """
        创建进度条区域

        Args:
            progress_data: 进度数据 {label: progress_value}
            title: 标题
        """
        st.subheader(title)

        for label, progress in progress_data.items():
            st.text(label)
            st.progress(min(max(progress, 0.0), 1.0))

    @staticmethod
    def create_info_cards(
        cards: List[Dict[str, Any]],
        columns: int = 2
    ) -> None:
        """
        创建信息卡片

        Args:
            cards: 卡片列表 [{title, content, type}]
            columns: 列数
        """
        cols = st.columns(columns)

        for i, card in enumerate(cards):
            col_index = i % columns

            with cols[col_index]:
                card_type = card.get('type', 'info')

                if card_type == 'success':
                    st.success(f"**{card['title']}**\n\n{card['content']}")
                elif card_type == 'warning':
                    st.warning(f"**{card['title']}**\n\n{card['content']}")
                elif card_type == 'error':
                    st.error(f"**{card['title']}**\n\n{card['content']}")
                else:
                    st.info(f"**{card['title']}**\n\n{card['content']}")

    @staticmethod
    def create_expandable_section(
        title: str,
        content_func,
        expanded: bool = False
    ) -> None:
        """
        创建可展开区域

        Args:
            title: 标题
            content_func: 内容生成函数
            expanded: 是否默认展开
        """
        with st.expander(title, expanded=expanded):
            content_func()

    @staticmethod
    def create_sidebar_navigation(
        nav_items: Dict[str, str],
        current_page: str = None
    ) -> str:
        """
        创建侧边栏导航

        Args:
            nav_items: 导航项目 {key: label}
            current_page: 当前页面

        Returns:
            选中的页面key
        """
        st.sidebar.title("导航菜单")

        selected = st.sidebar.radio(
            "选择页面",
            list(nav_items.keys()),
            format_func=lambda x: nav_items[x],
            index=list(nav_items.keys()).index(current_page) if current_page in nav_items else 0
        )

        return selected

    @staticmethod
    def create_comparison_table(
        data: Dict[str, Dict[str, Any]],
        title: str = "对比分析"
    ) -> None:
        """
        创建对比表格

        Args:
            data: 对比数据 {item_name: {metric: value}}
            title: 标题
        """
        st.subheader(title)

        if not data:
            st.warning("暂无对比数据")
            return

        # 转换为DataFrame
        df = pd.DataFrame(data).T

        # 显示表格
        st.dataframe(df, use_container_width=True)

        # 显示统计信息
        if len(df) > 1:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("对比项目", len(df))
            with col2:
                st.metric("对比指标", len(df.columns))
            with col3:
                numeric_cols = df.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 0:
                    best_item = df[numeric_cols[0]].idxmax()
                    st.metric("最佳表现", best_item)

# 便利函数
def show_metrics(metrics: Dict[str, Any], columns: int = 4) -> None:
    """显示指标的便利函数"""
    UIComponents.create_metrics_row(metrics, columns)

def show_kpi_dashboard(kpi_data: Dict[str, Any], title: str = "关键指标") -> None:
    """显示KPI仪表盘的便利函数"""
    UIComponents.create_kpi_dashboard(kpi_data, title)

def show_data_table(data: pd.DataFrame, title: str = "数据表格") -> None:
    """显示数据表格的便利函数"""
    UIComponents.create_data_table(data, title)

def show_status_indicators(statuses: Dict[str, str], title: str = "状态监控") -> None:
    """显示状态指示器的便利函数"""
    UIComponents.create_status_indicators(statuses, title)
