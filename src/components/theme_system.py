"""
主题系统和明暗模式调度
支持多种视觉主题、自动切换和个性化定制
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime, time
from typing import Dict, List, Optional, Any, Tuple
import uuid
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class ThemeSystem:
    """主题系统和模式调度器"""

    def __init__(self):
        self.themes = self._load_themes()
        self.schedule_rules = self._load_schedule_rules()

        # 初始化主题设置 - 使用浅色主题作为默认
        if 'current_theme' not in st.session_state:
            st.session_state['current_theme'] = 'light_professional'

        if 'theme_settings' not in st.session_state:
            st.session_state['theme_settings'] = self._get_default_settings()

        if 'auto_schedule_enabled' not in st.session_state:
            st.session_state['auto_schedule_enabled'] = False

    def _load_themes(self) -> Dict[str, Dict]:
        """加载主题配置"""
        return {
            # 深色主题
            "dark_professional": {
                "name": "专业深色",
                "description": "适合长时间交易的专业深色主题",
                "category": "dark",
                "colors": {
                    "primary": "#1f77b4",
                    "secondary": "#ff7f0e",
                    "success": "#2ca02c",
                    "danger": "#d62728",
                    "warning": "#ff7f0e",
                    "info": "#17a2b8",
                    "background": "#0e1117",
                    "surface": "#262730",
                    "text_primary": "#fafafa",
                    "text_secondary": "#a6a6a6",
                    "border": "#3d3d3d",
                    "accent": "#00d4aa"
                },
                "chart_theme": "plotly_dark",
                "font_family": "Arial, sans-serif",
                "font_size": "14px",
                "border_radius": "8px",
                "shadow": "0 2px 4px rgba(0,0,0,0.3)"
            },

            "dark_neon": {
                "name": "霓虹深色",
                "description": "充满活力的霓虹深色主题",
                "category": "dark",
                "colors": {
                    "primary": "#00ffff",
                    "secondary": "#ff00ff",
                    "success": "#00ff00",
                    "danger": "#ff0040",
                    "warning": "#ffff00",
                    "info": "#0080ff",
                    "background": "#000000",
                    "surface": "#1a1a1a",
                    "text_primary": "#ffffff",
                    "text_secondary": "#cccccc",
                    "border": "#333333",
                    "accent": "#ff6b6b"
                },
                "chart_theme": "plotly_dark",
                "font_family": "Courier New, monospace",
                "font_size": "14px",
                "border_radius": "4px",
                "shadow": "0 0 10px rgba(0,255,255,0.3)"
            },

            "dark_minimal": {
                "name": "极简深色",
                "description": "简洁优雅的极简深色主题",
                "category": "dark",
                "colors": {
                    "primary": "#6c757d",
                    "secondary": "#495057",
                    "success": "#28a745",
                    "danger": "#dc3545",
                    "warning": "#ffc107",
                    "info": "#17a2b8",
                    "background": "#212529",
                    "surface": "#343a40",
                    "text_primary": "#f8f9fa",
                    "text_secondary": "#adb5bd",
                    "border": "#495057",
                    "accent": "#6f42c1"
                },
                "chart_theme": "plotly_dark",
                "font_family": "Helvetica, Arial, sans-serif",
                "font_size": "14px",
                "border_radius": "6px",
                "shadow": "0 1px 3px rgba(0,0,0,0.2)"
            },

            # 浅色主题
            "light_professional": {
                "name": "专业浅色",
                "description": "清晰明亮的专业浅色主题",
                "category": "light",
                "colors": {
                    "primary": "#007bff",
                    "secondary": "#6c757d",
                    "success": "#28a745",
                    "danger": "#dc3545",
                    "warning": "#ffc107",
                    "info": "#17a2b8",
                    "background": "#ffffff",
                    "surface": "#f8f9fa",
                    "text_primary": "#212529",
                    "text_secondary": "#6c757d",
                    "border": "#dee2e6",
                    "accent": "#20c997"
                },
                "chart_theme": "plotly_white",
                "font_family": "Arial, sans-serif",
                "font_size": "14px",
                "border_radius": "8px",
                "shadow": "0 2px 4px rgba(0,0,0,0.1)"
            },

            "light_modern": {
                "name": "现代浅色",
                "description": "时尚现代的浅色主题",
                "category": "light",
                "colors": {
                    "primary": "#3f51b5",
                    "secondary": "#9c27b0",
                    "success": "#4caf50",
                    "danger": "#f44336",
                    "warning": "#ff9800",
                    "info": "#2196f3",
                    "background": "#fafafa",
                    "surface": "#ffffff",
                    "text_primary": "#263238",
                    "text_secondary": "#546e7a",
                    "border": "#e0e0e0",
                    "accent": "#ff5722"
                },
                "chart_theme": "plotly_white",
                "font_family": "Roboto, Arial, sans-serif",
                "font_size": "14px",
                "border_radius": "12px",
                "shadow": "0 4px 8px rgba(0,0,0,0.1)"
            },

            "light_soft": {
                "name": "柔和浅色",
                "description": "温和护眼的柔和浅色主题",
                "category": "light",
                "colors": {
                    "primary": "#5d4e75",
                    "secondary": "#b39ddb",
                    "success": "#81c784",
                    "danger": "#e57373",
                    "warning": "#ffb74d",
                    "info": "#64b5f6",
                    "background": "#f5f5f5",
                    "surface": "#ffffff",
                    "text_primary": "#424242",
                    "text_secondary": "#757575",
                    "border": "#e8eaf6",
                    "accent": "#ab47bc"
                },
                "chart_theme": "plotly_white",
                "font_family": "Georgia, serif",
                "font_size": "14px",
                "border_radius": "10px",
                "shadow": "0 2px 6px rgba(0,0,0,0.08)"
            },

            # 特殊主题
            "high_contrast": {
                "name": "高对比度",
                "description": "高对比度主题，适合视觉辅助",
                "category": "accessibility",
                "colors": {
                    "primary": "#0000ff",
                    "secondary": "#800080",
                    "success": "#008000",
                    "danger": "#ff0000",
                    "warning": "#ffff00",
                    "info": "#00ffff",
                    "background": "#ffffff",
                    "surface": "#f0f0f0",
                    "text_primary": "#000000",
                    "text_secondary": "#333333",
                    "border": "#000000",
                    "accent": "#ff00ff"
                },
                "chart_theme": "plotly_white",
                "font_family": "Arial Black, Arial, sans-serif",
                "font_size": "16px",
                "border_radius": "4px",
                "shadow": "0 2px 4px rgba(0,0,0,0.5)"
            },

            "trading_floor": {
                "name": "交易大厅",
                "description": "模拟传统交易大厅的经典主题",
                "category": "special",
                "colors": {
                    "primary": "#b8860b",
                    "secondary": "#8b4513",
                    "success": "#228b22",
                    "danger": "#dc143c",
                    "warning": "#daa520",
                    "info": "#4682b4",
                    "background": "#2f4f4f",
                    "surface": "#696969",
                    "text_primary": "#f5deb3",
                    "text_secondary": "#d2b48c",
                    "border": "#a0522d",
                    "accent": "#ffd700"
                },
                "chart_theme": "plotly_dark",
                "font_family": "Times New Roman, serif",
                "font_size": "14px",
                "border_radius": "6px",
                "shadow": "0 3px 6px rgba(0,0,0,0.4)"
            },

            "matrix": {
                "name": "矩阵风格",
                "description": "科幻风格的矩阵主题",
                "category": "special",
                "colors": {
                    "primary": "#00ff41",
                    "secondary": "#008f11",
                    "success": "#00ff41",
                    "danger": "#ff0000",
                    "warning": "#ffff00",
                    "info": "#00ffff",
                    "background": "#000000",
                    "surface": "#001100",
                    "text_primary": "#00ff41",
                    "text_secondary": "#008f11",
                    "border": "#003300",
                    "accent": "#00ff41"
                },
                "chart_theme": "plotly_dark",
                "font_family": "Courier New, monospace",
                "font_size": "13px",
                "border_radius": "2px",
                "shadow": "0 0 8px rgba(0,255,65,0.3)"
            }
        }

    def _load_schedule_rules(self) -> List[Dict]:
        """加载调度规则"""
        return [
            {
                "id": "work_hours",
                "name": "工作时间",
                "description": "工作时间使用浅色主题",
                "start_time": time(9, 0),
                "end_time": time(17, 0),
                "theme": "light_professional",
                "days": [0, 1, 2, 3, 4],  # 周一到周五
                "enabled": True
            },
            {
                "id": "evening_trading",
                "name": "晚间交易",
                "description": "晚间交易使用深色主题",
                "start_time": time(18, 0),
                "end_time": time(23, 59),
                "theme": "dark_professional",
                "days": [0, 1, 2, 3, 4, 5, 6],  # 每天
                "enabled": True
            },
            {
                "id": "weekend_relaxed",
                "name": "周末休闲",
                "description": "周末使用柔和主题",
                "start_time": time(0, 0),
                "end_time": time(23, 59),
                "theme": "light_soft",
                "days": [5, 6],  # 周六周日
                "enabled": False
            }
        ]

    def _get_default_settings(self) -> Dict:
        """获取默认设置"""
        return {
            "auto_schedule": False,
            "transition_animation": True,
            "remember_preference": True,
            "sync_with_system": False,
            "custom_css_enabled": False,
            "custom_css": "",
            "font_scaling": 1.0,
            "compact_mode": False,
            "high_contrast_mode": False,
            "reduce_motion": False
        }

    def apply_theme(self, theme_id: str, force_apply: bool = False) -> bool:
        """应用主题"""
        if theme_id not in self.themes:
            st.error(f"主题 {theme_id} 不存在")
            return False

        # 避免重复应用相同主题
        if not force_apply and st.session_state.get('current_theme') == theme_id and st.session_state.get('last_applied_theme') == theme_id:
            return True

        try:
            theme = self.themes[theme_id]
            st.session_state['current_theme'] = theme_id
            st.session_state['last_applied_theme'] = theme_id

            # 应用CSS样式
            self._inject_theme_css(theme)

            # 更新图表主题
            if 'chart_theme' in theme:
                st.session_state['chart_theme'] = theme['chart_theme']

            # 显示切换反馈（只在用户主动切换时显示）
            if force_apply and st.session_state['theme_settings'].get('transition_animation', True):
                st.success(f"✨ 已切换到 {theme['name']} 主题")

            return True

        except Exception as e:
            st.error(f"应用主题时出错: {str(e)}")
            return False

    def _inject_theme_css(self, theme: Dict):
        """注入主题CSS"""
        colors = theme['colors']

        css = f"""
        <style>
        /* 主题CSS变量 */
        :root {{
            --primary-color: {colors['primary']};
            --secondary-color: {colors['secondary']};
            --success-color: {colors['success']};
            --danger-color: {colors['danger']};
            --warning-color: {colors['warning']};
            --info-color: {colors['info']};
            --background-color: {colors['background']};
            --surface-color: {colors['surface']};
            --text-primary: {colors['text_primary']};
            --text-secondary: {colors['text_secondary']};
            --border-color: {colors['border']};
            --accent-color: {colors['accent']};
            --font-family: {theme['font_family']};
            --font-size: {theme['font_size']};
            --border-radius: {theme['border_radius']};
            --shadow: {theme['shadow']};
        }}

        /* Streamlit组件样式 */
        .stApp {{
            background-color: var(--background-color);
            color: var(--text-primary);
            font-family: var(--font-family);
            font-size: var(--font-size);
        }}

        .stSidebar {{
            background-color: var(--surface-color);
            border-right: 1px solid var(--border-color);
        }}

        .stMetric {{
            background-color: var(--surface-color);
            border: 1px solid var(--border-color);
            border-radius: var(--border-radius);
            padding: 1rem;
            box-shadow: var(--shadow);
        }}

        .stButton > button {{
            background-color: var(--primary-color);
            color: white;
            border: none;
            border-radius: var(--border-radius);
            font-family: var(--font-family);
            transition: all 0.3s ease;
        }}

        .stButton > button:hover {{
            background-color: var(--accent-color);
            transform: translateY(-2px);
            box-shadow: var(--shadow);
        }}

        .stSelectbox > div > div {{
            background-color: var(--surface-color);
            border: 1px solid var(--border-color);
            border-radius: var(--border-radius);
        }}

        .stTextInput > div > div > input {{
            background-color: var(--surface-color);
            border: 1px solid var(--border-color);
            border-radius: var(--border-radius);
            color: var(--text-primary);
        }}

        .stDataFrame {{
            border: 1px solid var(--border-color);
            border-radius: var(--border-radius);
            overflow: hidden;
        }}

        /* 自定义组件样式 */
        .theme-card {{
            background-color: var(--surface-color);
            border: 1px solid var(--border-color);
            border-radius: var(--border-radius);
            padding: 1rem;
            margin: 0.5rem 0;
            box-shadow: var(--shadow);
            transition: all 0.3s ease;
        }}

        .theme-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }}

        .color-preview {{
            width: 20px;
            height: 20px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 8px;
            border: 2px solid var(--border-color);
        }}

        .schedule-rule {{
            background-color: var(--surface-color);
            border-left: 4px solid var(--accent-color);
            padding: 1rem;
            margin: 0.5rem 0;
            border-radius: 0 var(--border-radius) var(--border-radius) 0;
        }}

        /* 动画效果 */
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        .fade-in {{
            animation: fadeIn 0.5s ease-out;
        }}

        /* 响应式设计 */
        @media (max-width: 768px) {{
            .stApp {{
                font-size: calc(var(--font-size) * 0.9);
            }}

            .theme-card {{
                padding: 0.75rem;
            }}
        }}
        </style>
        """

        # 添加自定义CSS
        if st.session_state['theme_settings'].get('custom_css_enabled', False):
            custom_css = st.session_state['theme_settings'].get('custom_css', '')
            if custom_css:
                css += f"\n<style>\n{custom_css}\n</style>"

        st.markdown(css, unsafe_allow_html=True)

    def check_auto_schedule(self):
        """检查自动调度"""
        if not st.session_state['theme_settings'].get('auto_schedule', False):
            return

        current_time = datetime.now().time()
        current_day = datetime.now().weekday()

        for rule in self.schedule_rules:
            if not rule.get('enabled', True):
                continue

            if current_day not in rule['days']:
                continue

            start_time = rule['start_time']
            end_time = rule['end_time']

            # 处理跨天的时间范围
            if start_time <= end_time:
                if start_time <= current_time <= end_time:
                    if st.session_state['current_theme'] != rule['theme']:
                        self.apply_theme(rule['theme'])
                        st.info(f"🕐 根据调度规则 '{rule['name']}' 自动切换到 {self.themes[rule['theme']]['name']} 主题")
                    break
            else:
                if current_time >= start_time or current_time <= end_time:
                    if st.session_state['current_theme'] != rule['theme']:
                        self.apply_theme(rule['theme'])
                        st.info(f"🕐 根据调度规则 '{rule['name']}' 自动切换到 {self.themes[rule['theme']]['name']} 主题")
                    break

    def render_theme_selector(self):
        """渲染主题选择器"""
        st.subheader("🎨 主题选择")

        # 主题分类
        categories = {
            "dark": "🌙 深色主题",
            "light": "☀️ 浅色主题",
            "accessibility": "♿ 无障碍主题",
            "special": "✨ 特殊主题"
        }

        # 当前主题信息
        current_theme = self.themes[st.session_state['current_theme']]

        col1, col2 = st.columns([2, 1])

        with col1:
            st.write(f"**当前主题:** {current_theme['name']}")
            st.caption(current_theme['description'])

        with col2:
            if st.button("🔄 刷新主题", help="重新应用当前主题"):
                self.apply_theme(st.session_state['current_theme'])

        # 主题预览和选择
        for category, category_name in categories.items():
            category_themes = {k: v for k, v in self.themes.items() if v['category'] == category}

            if category_themes:
                with st.expander(category_name):
                    cols = st.columns(2)

                    for i, (theme_id, theme) in enumerate(category_themes.items()):
                        with cols[i % 2]:
                            self._render_theme_card(theme_id, theme)

    def _render_theme_card(self, theme_id: str, theme: Dict):
        """渲染主题卡片"""
        is_current = theme_id == st.session_state['current_theme']

        # 主题卡片容器
        card_class = "theme-card"
        if is_current:
            card_class += " current-theme"

        with st.container():
            st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)

            col1, col2 = st.columns([3, 1])

            with col1:
                st.write(f"**{theme['name']}**")
                st.caption(theme['description'])

                # 颜色预览
                colors_html = ""
                for color_name, color_value in theme['colors'].items():
                    if color_name in ['primary', 'secondary', 'success', 'danger']:
                        colors_html += f'<span class="color-preview" style="background-color: {color_value};" title="{color_name}"></span>'

                st.markdown(colors_html, unsafe_allow_html=True)

            with col2:
                if is_current:
                    st.success("✅ 当前")
                else:
                    if st.button("应用", key=f"apply_{theme_id}"):
                        self.apply_theme(theme_id, force_apply=True)
                        st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

    def render_schedule_manager(self):
        """渲染调度管理器"""
        st.subheader("⏰ 自动调度")

        # 自动调度开关
        auto_schedule = st.checkbox(
            "启用自动主题调度",
            value=st.session_state['theme_settings'].get('auto_schedule', False),
            help="根据时间和规则自动切换主题"
        )

        st.session_state['theme_settings']['auto_schedule'] = auto_schedule

        if auto_schedule:
            st.info("🕐 自动调度已启用，系统将根据下方规则自动切换主题")

            # 立即检查调度
            if st.button("🔍 立即检查调度"):
                self.check_auto_schedule()

        # 调度规则管理
        st.subheader("📋 调度规则")

        for i, rule in enumerate(self.schedule_rules):
            with st.expander(f"{rule['name']} - {self.themes[rule['theme']]['name']}"):
                col1, col2, col3 = st.columns([2, 2, 1])

                with col1:
                    # 时间设置
                    start_time = st.time_input(
                        "开始时间",
                        value=rule['start_time'],
                        key=f"start_{i}"
                    )

                    end_time = st.time_input(
                        "结束时间",
                        value=rule['end_time'],
                        key=f"end_{i}"
                    )

                with col2:
                    # 主题选择
                    theme_options = list(self.themes.keys())
                    theme_names = [self.themes[t]['name'] for t in theme_options]

                    current_index = theme_options.index(rule['theme'])

                    selected_theme = st.selectbox(
                        "主题",
                        theme_options,
                        index=current_index,
                        format_func=lambda x: self.themes[x]['name'],
                        key=f"theme_{i}"
                    )

                    # 星期选择
                    days_options = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
                    selected_days = st.multiselect(
                        "适用星期",
                        range(7),
                        default=rule['days'],
                        format_func=lambda x: days_options[x],
                        key=f"days_{i}"
                    )

                with col3:
                    # 启用开关
                    enabled = st.checkbox(
                        "启用",
                        value=rule.get('enabled', True),
                        key=f"enabled_{i}"
                    )

                    # 删除按钮
                    if st.button("🗑️ 删除", key=f"delete_{i}"):
                        self.schedule_rules.pop(i)
                        st.rerun()

                # 更新规则
                self.schedule_rules[i].update({
                    'start_time': start_time,
                    'end_time': end_time,
                    'theme': selected_theme,
                    'days': selected_days,
                    'enabled': enabled
                })

        # 添加新规则
        if st.button("➕ 添加新规则"):
            new_rule = {
                "id": f"rule_{len(self.schedule_rules)}",
                "name": f"规则 {len(self.schedule_rules) + 1}",
                "description": "新的调度规则",
                "start_time": time(9, 0),
                "end_time": time(17, 0),
                "theme": "light_professional",
                "days": [0, 1, 2, 3, 4],
                "enabled": True
            }
            self.schedule_rules.append(new_rule)
            st.rerun()

    def render_theme_customizer(self):
        """渲染主题定制器"""
        st.subheader("🛠️ 主题定制")

        # 基础主题选择
        base_theme = st.selectbox(
            "选择基础主题",
            list(self.themes.keys()),
            index=list(self.themes.keys()).index(st.session_state['current_theme']),
            format_func=lambda x: self.themes[x]['name']
        )

        theme = self.themes[base_theme].copy()

        # 颜色定制
        st.subheader("🎨 颜色定制")

        color_cols = st.columns(3)

        color_names = {
            'primary': '主色',
            'secondary': '次色',
            'success': '成功色',
            'danger': '危险色',
            'warning': '警告色',
            'info': '信息色',
            'background': '背景色',
            'surface': '表面色',
            'text_primary': '主文字色',
            'text_secondary': '次文字色',
            'border': '边框色',
            'accent': '强调色'
        }

        for i, (color_key, color_name) in enumerate(color_names.items()):
            with color_cols[i % 3]:
                new_color = st.color_picker(
                    color_name,
                    value=theme['colors'][color_key],
                    key=f"color_{color_key}"
                )
                theme['colors'][color_key] = new_color

        # 字体定制
        st.subheader("🔤 字体设置")

        font_col1, font_col2 = st.columns(2)

        with font_col1:
            font_families = [
                "Arial, sans-serif",
                "Helvetica, Arial, sans-serif",
                "Roboto, Arial, sans-serif",
                "Times New Roman, serif",
                "Georgia, serif",
                "Courier New, monospace",
                "Arial Black, Arial, sans-serif"
            ]

            theme['font_family'] = st.selectbox(
                "字体族",
                font_families,
                index=font_families.index(theme['font_family']) if theme['font_family'] in font_families else 0
            )

        with font_col2:
            font_size = st.slider(
                "字体大小",
                min_value=10,
                max_value=20,
                value=int(theme['font_size'].replace('px', '')),
                step=1
            )
            theme['font_size'] = f"{font_size}px"

        # 样式定制
        st.subheader("🎭 样式设置")

        style_col1, style_col2 = st.columns(2)

        with style_col1:
            border_radius = st.slider(
                "圆角大小",
                min_value=0,
                max_value=20,
                value=int(theme['border_radius'].replace('px', '')),
                step=1
            )
            theme['border_radius'] = f"{border_radius}px"

        with style_col2:
            chart_themes = ["plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white"]
            theme['chart_theme'] = st.selectbox(
                "图表主题",
                chart_themes,
                index=chart_themes.index(theme['chart_theme']) if theme['chart_theme'] in chart_themes else 0
            )

        # 预览和应用
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("🔍 预览主题", type="primary"):
                # 创建临时主题ID
                temp_theme_id = f"custom_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                self.themes[temp_theme_id] = theme
                self.apply_theme(temp_theme_id, force_apply=True)

        with col2:
            if st.button("💾 保存为新主题"):
                theme_name = st.text_input("主题名称", value="我的自定义主题")
                if theme_name:
                    custom_theme_id = f"custom_{uuid.uuid4().hex[:8]}"
                    theme['name'] = theme_name
                    theme['description'] = "用户自定义主题"
                    theme['category'] = "custom"
                    self.themes[custom_theme_id] = theme
                    st.success(f"✅ 主题 '{theme_name}' 已保存")

        with col3:
            if st.button("🔄 重置为默认"):
                self.apply_theme(base_theme)

    def render_accessibility_settings(self):
        """渲染无障碍设置"""
        st.subheader("♿ 无障碍设置")

        # 高对比度模式
        high_contrast = st.checkbox(
            "高对比度模式",
            value=st.session_state['theme_settings'].get('high_contrast_mode', False),
            help="启用高对比度以提高可读性"
        )

        if high_contrast != st.session_state['theme_settings'].get('high_contrast_mode', False):
            st.session_state['theme_settings']['high_contrast_mode'] = high_contrast
            if high_contrast:
                self.apply_theme('high_contrast')

        # 字体缩放
        font_scaling = st.slider(
            "字体缩放",
            min_value=0.8,
            max_value=1.5,
            value=st.session_state['theme_settings'].get('font_scaling', 1.0),
            step=0.1,
            help="调整全局字体大小"
        )
        st.session_state['theme_settings']['font_scaling'] = font_scaling

        # 减少动画
        reduce_motion = st.checkbox(
            "减少动画效果",
            value=st.session_state['theme_settings'].get('reduce_motion', False),
            help="减少或禁用动画效果"
        )
        st.session_state['theme_settings']['reduce_motion'] = reduce_motion

        # 紧凑模式
        compact_mode = st.checkbox(
            "紧凑模式",
            value=st.session_state['theme_settings'].get('compact_mode', False),
            help="减少界面元素间距"
        )
        st.session_state['theme_settings']['compact_mode'] = compact_mode

        # 系统主题同步
        sync_with_system = st.checkbox(
            "跟随系统主题",
            value=st.session_state['theme_settings'].get('sync_with_system', False),
            help="自动跟随操作系统的明暗主题设置"
        )
        st.session_state['theme_settings']['sync_with_system'] = sync_with_system

    def render_advanced_settings(self):
        """渲染高级设置"""
        st.subheader("⚙️ 高级设置")

        # 自定义CSS
        custom_css_enabled = st.checkbox(
            "启用自定义CSS",
            value=st.session_state['theme_settings'].get('custom_css_enabled', False),
            help="允许添加自定义CSS样式"
        )
        st.session_state['theme_settings']['custom_css_enabled'] = custom_css_enabled

        if custom_css_enabled:
            custom_css = st.text_area(
                "自定义CSS代码",
                value=st.session_state['theme_settings'].get('custom_css', ''),
                height=200,
                help="输入自定义CSS代码来进一步定制界面"
            )
            st.session_state['theme_settings']['custom_css'] = custom_css

            if st.button("应用自定义CSS"):
                self.apply_theme(st.session_state['current_theme'])

        # 过渡动画
        transition_animation = st.checkbox(
            "主题切换动画",
            value=st.session_state['theme_settings'].get('transition_animation', True),
            help="主题切换时显示过渡动画"
        )
        st.session_state['theme_settings']['transition_animation'] = transition_animation

        # 记住偏好
        remember_preference = st.checkbox(
            "记住主题偏好",
            value=st.session_state['theme_settings'].get('remember_preference', True),
            help="在下次访问时记住您的主题选择"
        )
        st.session_state['theme_settings']['remember_preference'] = remember_preference

        # 导入导出设置
        st.subheader("📁 导入导出")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("📤 导出主题设置"):
                settings_data = {
                    'current_theme': st.session_state['current_theme'],
                    'theme_settings': st.session_state['theme_settings'],
                    'schedule_rules': self.schedule_rules,
                    'custom_themes': {k: v for k, v in self.themes.items() if v.get('category') == 'custom'}
                }

                settings_json = json.dumps(settings_data, indent=2, ensure_ascii=False, default=str)

                st.download_button(
                    label="下载设置文件",
                    data=settings_json,
                    file_name=f"theme_settings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )

        with col2:
            uploaded_file = st.file_uploader(
                "📥 导入主题设置",
                type=['json'],
                help="上传之前导出的主题设置文件"
            )

            if uploaded_file is not None:
                try:
                    settings_data = json.load(uploaded_file)

                    # 导入设置
                    if 'current_theme' in settings_data:
                        st.session_state['current_theme'] = settings_data['current_theme']

                    if 'theme_settings' in settings_data:
                        st.session_state['theme_settings'].update(settings_data['theme_settings'])

                    if 'schedule_rules' in settings_data:
                        self.schedule_rules = settings_data['schedule_rules']

                    if 'custom_themes' in settings_data:
                        self.themes.update(settings_data['custom_themes'])

                    st.success("✅ 主题设置导入成功")
                    st.rerun()

                except Exception as e:
                    st.error(f"导入设置时出错: {str(e)}")

def render_theme_system():
    """渲染主题系统主界面"""
    st.title("🎨 主题系统")

    # 创建主题系统实例
    theme_system = ThemeSystem()

    # 检查自动调度
    theme_system.check_auto_schedule()

    # 只在主题系统页面首次加载或用户主动选择时应用主题
    # 避免每次滑动到此区域都自动应用主题
    if 'theme_system_initialized' not in st.session_state:
        st.session_state['theme_system_initialized'] = True
        # 只有当前主题不是默认的浅色主题时才应用
        if st.session_state['current_theme'] != 'light_professional':
            theme_system.apply_theme(st.session_state['current_theme'])

    # 创建标签页
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎨 主题选择",
        "⏰ 自动调度",
        "🛠️ 主题定制",
        "♿ 无障碍",
        "⚙️ 高级设置"
    ])

    with tab1:
        theme_system.render_theme_selector()

    with tab2:
        theme_system.render_schedule_manager()

    with tab3:
        theme_system.render_theme_customizer()

    with tab4:
        theme_system.render_accessibility_settings()

    with tab5:
        theme_system.render_advanced_settings()

    # 侧边栏快速控制
    st.sidebar.subheader("🎨 快速主题切换")

    # 快速主题选择
    quick_themes = {
        'dark_professional': '🌙 专业深色',
        'light_professional': '☀️ 专业浅色',
        'dark_neon': '🌈 霓虹深色',
        'light_modern': '✨ 现代浅色',
        'high_contrast': '♿ 高对比度'
    }

    for theme_id, theme_name in quick_themes.items():
        if st.sidebar.button(theme_name, key=f"quick_{theme_id}"):
            theme_system.apply_theme(theme_id, force_apply=True)
            st.rerun()

    # 当前主题信息
    current_theme = theme_system.themes[st.session_state['current_theme']]
    st.sidebar.write(f"**当前:** {current_theme['name']}")

    # 自动调度状态
    if st.session_state['theme_settings'].get('auto_schedule', False):
        st.sidebar.success("🕐 自动调度已启用")
    else:
        st.sidebar.info("⏰ 自动调度已禁用")

    # 功能说明
    with st.expander("📖 功能说明"):
        st.markdown("""
        ### 🎨 主题系统特性

        **🎨 丰富的主题选择**
        - 🌙 专业深色主题 (适合长时间使用)
        - ☀️ 清晰浅色主题 (明亮清晰)
        - 🌈 霓虹风格主题 (充满活力)
        - ♿ 高对比度主题 (无障碍支持)
        - ✨ 特殊风格主题 (交易大厅、矩阵等)

        **⏰ 智能自动调度**
        - 🕐 基于时间自动切换
        - 📅 工作日/周末不同主题
        - 🌅 日出日落模式
        - 🎯 自定义调度规则

        **🛠️ 深度定制功能**
        - 🎨 颜色完全自定义
        - 🔤 字体和大小调整
        - 🎭 样式和圆角设置
        - 📊 图表主题同步

        **♿ 无障碍支持**
        - 🔍 高对比度模式
        - 📏 字体缩放功能
        - 🎬 减少动画选项
        - 📱 紧凑模式支持

        **⚙️ 高级功能**
        - 💻 自定义CSS支持
        - 🔄 设置导入导出
        - 💾 偏好记忆功能
        - 🖥️ 系统主题同步

        **🚀 使用技巧**
        - 使用侧边栏快速切换常用主题
        - 设置自动调度减少手动操作
        - 自定义主题满足个性化需求
        - 启用无障碍功能提升使用体验
        """)

    return True

if __name__ == "__main__":
    render_theme_system()
