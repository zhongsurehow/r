"""
可定制键盘快捷键系统
支持交易操作、导航和自定义快捷键配置
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
import uuid

class KeyboardShortcuts:
    """键盘快捷键系统"""

    def __init__(self):
        self.default_shortcuts = self._load_default_shortcuts()
        self.action_handlers = self._register_action_handlers()
        self.shortcut_history = []

        # 初始化用户快捷键设置
        if 'user_shortcuts' not in st.session_state:
            st.session_state['user_shortcuts'] = self.default_shortcuts.copy()

    def _load_default_shortcuts(self) -> Dict[str, Dict]:
        """加载默认快捷键配置"""
        return {
            # 交易操作
            "quick_buy": {
                "name": "快速买入",
                "description": "执行快速买入操作",
                "category": "trading",
                "default_key": "Ctrl+B",
                "action": "execute_quick_buy",
                "enabled": True,
                "icon": "🟢"
            },
            "quick_sell": {
                "name": "快速卖出",
                "description": "执行快速卖出操作",
                "category": "trading",
                "default_key": "Ctrl+S",
                "action": "execute_quick_sell",
                "enabled": True,
                "icon": "🔴"
            },
            "execute_arbitrage": {
                "name": "执行套利",
                "description": "执行选中的套利机会",
                "category": "arbitrage",
                "default_key": "Ctrl+A",
                "action": "execute_arbitrage_opportunity",
                "enabled": True,
                "icon": "⚡"
            },
            "cancel_all_orders": {
                "name": "取消所有订单",
                "description": "取消所有挂单",
                "category": "trading",
                "default_key": "Ctrl+X",
                "action": "cancel_all_orders",
                "enabled": True,
                "icon": "❌"
            },
            "emergency_stop": {
                "name": "紧急停止",
                "description": "紧急停止所有交易",
                "category": "risk",
                "default_key": "Ctrl+Shift+E",
                "action": "emergency_stop_trading",
                "enabled": True,
                "icon": "🚨"
            },

            # 导航操作
            "goto_dashboard": {
                "name": "跳转到仪表盘",
                "description": "快速跳转到主仪表盘",
                "category": "navigation",
                "default_key": "Ctrl+1",
                "action": "navigate_to_dashboard",
                "enabled": True,
                "icon": "🏠"
            },
            "goto_arbitrage": {
                "name": "跳转到套利页面",
                "description": "快速跳转到套利机会页面",
                "category": "navigation",
                "default_key": "Ctrl+2",
                "action": "navigate_to_arbitrage",
                "enabled": True,
                "icon": "⚡"
            },
            "goto_portfolio": {
                "name": "跳转到投资组合",
                "description": "快速跳转到投资组合页面",
                "category": "navigation",
                "default_key": "Ctrl+3",
                "action": "navigate_to_portfolio",
                "enabled": True,
                "icon": "💼"
            },
            "goto_risk": {
                "name": "跳转到风险管理",
                "description": "快速跳转到风险管理页面",
                "category": "navigation",
                "default_key": "Ctrl+4",
                "action": "navigate_to_risk",
                "enabled": True,
                "icon": "🛡️"
            },
            "goto_settings": {
                "name": "跳转到设置",
                "description": "快速跳转到设置页面",
                "category": "navigation",
                "default_key": "Ctrl+,",
                "action": "navigate_to_settings",
                "enabled": True,
                "icon": "⚙️"
            },

            # 图表操作
            "zoom_in": {
                "name": "放大图表",
                "description": "放大当前图表",
                "category": "chart",
                "default_key": "Ctrl++",
                "action": "chart_zoom_in",
                "enabled": True,
                "icon": "🔍"
            },
            "zoom_out": {
                "name": "缩小图表",
                "description": "缩小当前图表",
                "category": "chart",
                "default_key": "Ctrl+-",
                "action": "chart_zoom_out",
                "enabled": True,
                "icon": "🔍"
            },
            "reset_zoom": {
                "name": "重置缩放",
                "description": "重置图表缩放",
                "category": "chart",
                "default_key": "Ctrl+0",
                "action": "chart_reset_zoom",
                "enabled": True,
                "icon": "🎯"
            },
            "toggle_fullscreen": {
                "name": "全屏切换",
                "description": "切换图表全屏模式",
                "category": "chart",
                "default_key": "F11",
                "action": "toggle_chart_fullscreen",
                "enabled": True,
                "icon": "📺"
            },

            # 数据操作
            "refresh_data": {
                "name": "刷新数据",
                "description": "刷新所有数据",
                "category": "data",
                "default_key": "F5",
                "action": "refresh_all_data",
                "enabled": True,
                "icon": "🔄"
            },
            "export_data": {
                "name": "导出数据",
                "description": "导出当前数据",
                "category": "data",
                "default_key": "Ctrl+E",
                "action": "export_current_data",
                "enabled": True,
                "icon": "📤"
            },
            "search": {
                "name": "搜索",
                "description": "打开搜索功能",
                "category": "utility",
                "default_key": "Ctrl+F",
                "action": "open_search",
                "enabled": True,
                "icon": "🔍"
            },

            # 界面操作
            "toggle_sidebar": {
                "name": "切换侧边栏",
                "description": "显示/隐藏侧边栏",
                "category": "interface",
                "default_key": "Ctrl+\\",
                "action": "toggle_sidebar",
                "enabled": True,
                "icon": "📋"
            },
            "toggle_theme": {
                "name": "切换主题",
                "description": "切换明暗主题",
                "category": "interface",
                "default_key": "Ctrl+T",
                "action": "toggle_theme",
                "enabled": True,
                "icon": "🌓"
            },
            "help": {
                "name": "帮助",
                "description": "显示帮助信息",
                "category": "utility",
                "default_key": "F1",
                "action": "show_help",
                "enabled": True,
                "icon": "❓"
            }
        }

    def _register_action_handlers(self) -> Dict[str, Callable]:
        """注册动作处理器"""
        return {
            # 交易操作处理器
            "execute_quick_buy": self._handle_quick_buy,
            "execute_quick_sell": self._handle_quick_sell,
            "execute_arbitrage_opportunity": self._handle_execute_arbitrage,
            "cancel_all_orders": self._handle_cancel_all_orders,
            "emergency_stop_trading": self._handle_emergency_stop,

            # 导航操作处理器
            "navigate_to_dashboard": self._handle_navigate_dashboard,
            "navigate_to_arbitrage": self._handle_navigate_arbitrage,
            "navigate_to_portfolio": self._handle_navigate_portfolio,
            "navigate_to_risk": self._handle_navigate_risk,
            "navigate_to_settings": self._handle_navigate_settings,

            # 图表操作处理器
            "chart_zoom_in": self._handle_chart_zoom_in,
            "chart_zoom_out": self._handle_chart_zoom_out,
            "chart_reset_zoom": self._handle_chart_reset_zoom,
            "toggle_chart_fullscreen": self._handle_toggle_fullscreen,

            # 数据操作处理器
            "refresh_all_data": self._handle_refresh_data,
            "export_current_data": self._handle_export_data,
            "open_search": self._handle_open_search,

            # 界面操作处理器
            "toggle_sidebar": self._handle_toggle_sidebar,
            "toggle_theme": self._handle_toggle_theme,
            "show_help": self._handle_show_help
        }

    def execute_shortcut(self, shortcut_id: str) -> bool:
        """执行快捷键操作"""
        if shortcut_id not in st.session_state['user_shortcuts']:
            return False

        shortcut = st.session_state['user_shortcuts'][shortcut_id]

        if not shortcut.get('enabled', True):
            return False

        action = shortcut.get('action')
        if action not in self.action_handlers:
            st.error(f"未找到动作处理器: {action}")
            return False

        try:
            # 记录快捷键使用历史
            self.shortcut_history.append({
                'shortcut_id': shortcut_id,
                'timestamp': datetime.now(),
                'action': action,
                'key': shortcut.get('default_key', 'Unknown')
            })

            # 执行动作
            result = self.action_handlers[action]()

            # 显示执行反馈
            if result:
                st.success(f"✅ {shortcut['name']} 执行成功")
            else:
                st.warning(f"⚠️ {shortcut['name']} 执行失败")

            return result

        except Exception as e:
            st.error(f"执行快捷键时出错: {str(e)}")
            return False

    # 交易操作处理器
    def _handle_quick_buy(self) -> bool:
        """处理快速买入"""
        st.info("🟢 执行快速买入操作")
        # 这里应该连接到实际的交易系统
        return True

    def _handle_quick_sell(self) -> bool:
        """处理快速卖出"""
        st.info("🔴 执行快速卖出操作")
        # 这里应该连接到实际的交易系统
        return True

    def _handle_execute_arbitrage(self) -> bool:
        """处理执行套利"""
        st.info("⚡ 执行套利机会")
        # 这里应该连接到套利执行系统
        return True

    def _handle_cancel_all_orders(self) -> bool:
        """处理取消所有订单"""
        st.warning("❌ 取消所有挂单")
        # 这里应该连接到订单管理系统
        return True

    def _handle_emergency_stop(self) -> bool:
        """处理紧急停止"""
        st.error("🚨 紧急停止所有交易")
        # 这里应该连接到风险管理系统
        return True

    # 导航操作处理器
    def _handle_navigate_dashboard(self) -> bool:
        """导航到仪表盘"""
        st.info("🏠 跳转到仪表盘")
        st.session_state['current_page'] = 'dashboard'
        return True

    def _handle_navigate_arbitrage(self) -> bool:
        """导航到套利页面"""
        st.info("⚡ 跳转到套利页面")
        st.session_state['current_page'] = 'arbitrage'
        return True

    def _handle_navigate_portfolio(self) -> bool:
        """导航到投资组合"""
        st.info("💼 跳转到投资组合")
        st.session_state['current_page'] = 'portfolio'
        return True

    def _handle_navigate_risk(self) -> bool:
        """导航到风险管理"""
        st.info("🛡️ 跳转到风险管理")
        st.session_state['current_page'] = 'risk'
        return True

    def _handle_navigate_settings(self) -> bool:
        """导航到设置"""
        st.info("⚙️ 跳转到设置")
        st.session_state['current_page'] = 'settings'
        return True

    # 图表操作处理器
    def _handle_chart_zoom_in(self) -> bool:
        """处理图表放大"""
        st.info("🔍 放大图表")
        return True

    def _handle_chart_zoom_out(self) -> bool:
        """处理图表缩小"""
        st.info("🔍 缩小图表")
        return True

    def _handle_chart_reset_zoom(self) -> bool:
        """处理重置缩放"""
        st.info("🎯 重置图表缩放")
        return True

    def _handle_toggle_fullscreen(self) -> bool:
        """处理全屏切换"""
        st.info("📺 切换全屏模式")
        return True

    # 数据操作处理器
    def _handle_refresh_data(self) -> bool:
        """处理刷新数据"""
        st.info("🔄 刷新所有数据")
        return True

    def _handle_export_data(self) -> bool:
        """处理导出数据"""
        st.info("📤 导出当前数据")
        return True

    def _handle_open_search(self) -> bool:
        """处理打开搜索"""
        st.info("🔍 打开搜索功能")
        return True

    # 界面操作处理器
    def _handle_toggle_sidebar(self) -> bool:
        """处理切换侧边栏"""
        st.info("📋 切换侧边栏显示")
        return True

    def _handle_toggle_theme(self) -> bool:
        """处理切换主题"""
        st.info("🌓 切换明暗主题")
        return True

    def _handle_show_help(self) -> bool:
        """处理显示帮助"""
        st.info("❓ 显示帮助信息")
        return True

    def render_shortcut_manager(self):
        """渲染快捷键管理器"""
        st.subheader("⌨️ 快捷键管理")

        # 快捷键搜索和过滤
        col1, col2 = st.columns([2, 1])

        with col1:
            search_term = st.text_input("🔍 搜索快捷键", placeholder="输入快捷键名称或描述...")

        with col2:
            categories = list(set(shortcut['category'] for shortcut in self.default_shortcuts.values()))
            selected_category = st.selectbox("📂 按类别过滤", ['全部'] + categories)

        # 过滤快捷键
        filtered_shortcuts = {}
        for shortcut_id, shortcut in st.session_state['user_shortcuts'].items():
            # 类别过滤
            if selected_category != '全部' and shortcut['category'] != selected_category:
                continue

            # 搜索过滤
            if search_term:
                if (search_term.lower() not in shortcut['name'].lower() and
                    search_term.lower() not in shortcut['description'].lower() and
                    search_term.lower() not in shortcut.get('default_key', '').lower()):
                    continue

            filtered_shortcuts[shortcut_id] = shortcut

        # 显示快捷键列表
        st.write(f"找到 {len(filtered_shortcuts)} 个快捷键")

        for shortcut_id, shortcut in filtered_shortcuts.items():
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([1, 3, 2, 2, 1])

                with col1:
                    st.write(shortcut['icon'])

                with col2:
                    st.write(f"**{shortcut['name']}**")
                    st.caption(shortcut['description'])

                with col3:
                    # 快捷键编辑
                    new_key = st.text_input(
                        "快捷键",
                        value=shortcut.get('default_key', ''),
                        key=f"key_{shortcut_id}",
                        label_visibility="collapsed"
                    )

                    if new_key != shortcut.get('default_key', ''):
                        st.session_state['user_shortcuts'][shortcut_id]['default_key'] = new_key

                with col4:
                    # 启用/禁用
                    enabled = st.checkbox(
                        "启用",
                        value=shortcut.get('enabled', True),
                        key=f"enabled_{shortcut_id}",
                        label_visibility="collapsed"
                    )

                    if enabled != shortcut.get('enabled', True):
                        st.session_state['user_shortcuts'][shortcut_id]['enabled'] = enabled

                with col5:
                    # 测试按钮
                    if st.button("测试", key=f"test_{shortcut_id}"):
                        self.execute_shortcut(shortcut_id)

                st.divider()

    def render_shortcut_recorder(self):
        """渲染快捷键录制器"""
        st.subheader("🎙️ 快捷键录制")

        st.info("💡 点击下方按钮开始录制新的快捷键组合")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🔴 开始录制", type="primary"):
                st.session_state['recording'] = True
                st.success("正在录制... 请按下您想要的快捷键组合")

        with col2:
            if st.button("⏹️ 停止录制"):
                st.session_state['recording'] = False
                st.info("录制已停止")

        # 模拟录制状态
        if st.session_state.get('recording', False):
            st.warning("🎙️ 录制中... (这是模拟功能)")

            # 模拟录制的快捷键
            recorded_key = st.text_input("录制到的快捷键", value="Ctrl+Shift+R", disabled=True)

            if st.button("✅ 确认录制"):
                st.session_state['recording'] = False
                st.success(f"已录制快捷键: {recorded_key}")

    def render_shortcut_profiles(self):
        """渲染快捷键配置文件"""
        st.subheader("👤 快捷键配置文件")

        # 预设配置文件
        profiles = {
            "default": {
                "name": "默认配置",
                "description": "系统默认快捷键配置",
                "shortcuts": self.default_shortcuts
            },
            "trader": {
                "name": "交易员配置",
                "description": "专为活跃交易员优化的快捷键",
                "shortcuts": self._get_trader_profile()
            },
            "analyst": {
                "name": "分析师配置",
                "description": "专为市场分析师优化的快捷键",
                "shortcuts": self._get_analyst_profile()
            },
            "minimal": {
                "name": "极简配置",
                "description": "只包含最基本的快捷键",
                "shortcuts": self._get_minimal_profile()
            }
        }

        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            selected_profile = st.selectbox(
                "选择配置文件",
                list(profiles.keys()),
                format_func=lambda x: profiles[x]['name']
            )

        with col2:
            if st.button("应用配置", type="primary"):
                st.session_state['user_shortcuts'] = profiles[selected_profile]['shortcuts'].copy()
                st.success(f"已应用 {profiles[selected_profile]['name']}")

        with col3:
            if st.button("导出配置"):
                config_json = json.dumps(st.session_state['user_shortcuts'], indent=2, ensure_ascii=False)
                st.download_button(
                    label="下载配置文件",
                    data=config_json,
                    file_name=f"shortcuts_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )

        # 显示配置文件详情
        profile = profiles[selected_profile]
        st.write(f"**{profile['name']}**")
        st.caption(profile['description'])

        # 显示配置文件中的快捷键
        with st.expander("查看配置详情"):
            for shortcut_id, shortcut in profile['shortcuts'].items():
                col1, col2, col3 = st.columns([1, 3, 2])

                with col1:
                    st.write(shortcut['icon'])

                with col2:
                    st.write(f"**{shortcut['name']}**")

                with col3:
                    st.code(shortcut.get('default_key', 'N/A'))

    def _get_trader_profile(self) -> Dict:
        """获取交易员配置文件"""
        trader_shortcuts = self.default_shortcuts.copy()

        # 修改一些快捷键以适合交易员
        trader_shortcuts['quick_buy']['default_key'] = 'F1'
        trader_shortcuts['quick_sell']['default_key'] = 'F2'
        trader_shortcuts['execute_arbitrage']['default_key'] = 'F3'
        trader_shortcuts['cancel_all_orders']['default_key'] = 'F4'
        trader_shortcuts['emergency_stop']['default_key'] = 'Esc'

        return trader_shortcuts

    def _get_analyst_profile(self) -> Dict:
        """获取分析师配置文件"""
        analyst_shortcuts = self.default_shortcuts.copy()

        # 禁用一些交易相关的快捷键
        analyst_shortcuts['quick_buy']['enabled'] = False
        analyst_shortcuts['quick_sell']['enabled'] = False
        analyst_shortcuts['execute_arbitrage']['enabled'] = False

        # 强化图表和数据操作
        analyst_shortcuts['zoom_in']['default_key'] = '+'
        analyst_shortcuts['zoom_out']['default_key'] = '-'
        analyst_shortcuts['refresh_data']['default_key'] = 'R'

        return analyst_shortcuts

    def _get_minimal_profile(self) -> Dict:
        """获取极简配置文件"""
        minimal_shortcuts = {}

        # 只保留最基本的快捷键
        essential_shortcuts = [
            'refresh_data', 'help', 'goto_dashboard',
            'toggle_theme', 'emergency_stop'
        ]

        for shortcut_id in essential_shortcuts:
            if shortcut_id in self.default_shortcuts:
                minimal_shortcuts[shortcut_id] = self.default_shortcuts[shortcut_id].copy()

        return minimal_shortcuts

    def render_usage_statistics(self):
        """渲染使用统计"""
        st.subheader("📊 使用统计")

        if not self.shortcut_history:
            st.info("暂无快捷键使用记录")
            return

        # 统计数据
        history_df = pd.DataFrame(self.shortcut_history)

        col1, col2 = st.columns(2)

        with col1:
            st.metric("总使用次数", len(self.shortcut_history))

            # 最常用的快捷键
            most_used = history_df['shortcut_id'].value_counts().head(5)
            st.write("**最常用快捷键:**")
            for shortcut_id, count in most_used.items():
                shortcut = st.session_state['user_shortcuts'].get(shortcut_id, {})
                st.write(f"• {shortcut.get('name', shortcut_id)}: {count}次")

        with col2:
            # 今日使用情况
            today = datetime.now().date()
            today_usage = history_df[history_df['timestamp'].dt.date == today]
            st.metric("今日使用次数", len(today_usage))

            # 按类别统计
            if 'category' in history_df.columns:
                category_stats = history_df['category'].value_counts()
                st.write("**按类别统计:**")
                for category, count in category_stats.items():
                    st.write(f"• {category}: {count}次")

        # 使用趋势图
        if len(self.shortcut_history) > 1:
            st.subheader("📈 使用趋势")

            # 按小时统计
            history_df['hour'] = history_df['timestamp'].dt.hour
            hourly_usage = history_df.groupby('hour').size().reset_index(name='count')

            import plotly.express as px
            fig = px.bar(
                hourly_usage,
                x='hour',
                y='count',
                title="每小时快捷键使用次数",
                template="plotly_dark"
            )

            st.plotly_chart(fig, use_container_width=True)

    def render_help_guide(self):
        """渲染帮助指南"""
        st.subheader("❓ 快捷键帮助")

        # 按类别显示快捷键
        categories = {
            "trading": "💰 交易操作",
            "navigation": "🧭 页面导航",
            "chart": "📈 图表操作",
            "data": "📊 数据操作",
            "interface": "🖥️ 界面操作",
            "utility": "🔧 实用工具",
            "risk": "🛡️ 风险管理",
            "arbitrage": "⚡ 套利操作"
        }

        for category, category_name in categories.items():
            category_shortcuts = {
                k: v for k, v in st.session_state['user_shortcuts'].items()
                if v.get('category') == category and v.get('enabled', True)
            }

            if category_shortcuts:
                with st.expander(category_name):
                    for shortcut_id, shortcut in category_shortcuts.items():
                        col1, col2, col3 = st.columns([1, 3, 2])

                        with col1:
                            st.write(shortcut['icon'])

                        with col2:
                            st.write(f"**{shortcut['name']}**")
                            st.caption(shortcut['description'])

                        with col3:
                            st.code(shortcut.get('default_key', 'N/A'))

        # 快捷键使用技巧
        st.subheader("💡 使用技巧")

        tips = [
            "🎯 **组合键**: 使用 Ctrl、Shift、Alt 组合键可以避免与系统快捷键冲突",
            "⚡ **快速访问**: 数字键 1-9 配合 Ctrl 可以快速切换页面",
            "🔄 **刷新数据**: F5 键可以快速刷新所有数据",
            "🚨 **紧急停止**: Esc 键可以紧急停止所有交易操作",
            "📋 **复制粘贴**: 标准的 Ctrl+C/Ctrl+V 在数据表格中仍然有效",
            "🔍 **搜索功能**: Ctrl+F 可以在任何页面打开搜索功能",
            "🌓 **主题切换**: Ctrl+T 可以快速切换明暗主题",
            "❓ **获取帮助**: F1 键可以在任何时候显示帮助信息"
        ]

        for tip in tips:
            st.write(tip)

def render_keyboard_shortcuts():
    """渲染键盘快捷键主界面"""
    st.title("⌨️ 键盘快捷键系统")

    # 创建快捷键系统实例
    shortcuts = KeyboardShortcuts()

    # 创建标签页
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "⌨️ 快捷键管理",
        "🎙️ 录制快捷键",
        "👤 配置文件",
        "📊 使用统计",
        "❓ 帮助指南"
    ])

    with tab1:
        shortcuts.render_shortcut_manager()

    with tab2:
        shortcuts.render_shortcut_recorder()

    with tab3:
        shortcuts.render_shortcut_profiles()

    with tab4:
        shortcuts.render_usage_statistics()

    with tab5:
        shortcuts.render_help_guide()

    # 快捷键测试区域
    st.sidebar.subheader("🧪 快捷键测试")

    # 显示当前启用的快捷键
    enabled_shortcuts = {
        k: v for k, v in st.session_state.get('user_shortcuts', {}).items()
        if v.get('enabled', True)
    }

    if enabled_shortcuts:
        test_shortcut = st.sidebar.selectbox(
            "选择要测试的快捷键",
            list(enabled_shortcuts.keys()),
            format_func=lambda x: f"{enabled_shortcuts[x]['icon']} {enabled_shortcuts[x]['name']}"
        )

        if st.sidebar.button("🚀 执行快捷键"):
            shortcuts.execute_shortcut(test_shortcut)

    # 快捷键状态显示
    st.sidebar.subheader("📊 快捷键状态")

    total_shortcuts = len(st.session_state.get('user_shortcuts', {}))
    enabled_count = len(enabled_shortcuts)

    st.sidebar.metric("总快捷键数", total_shortcuts)
    st.sidebar.metric("已启用", enabled_count)
    st.sidebar.metric("已禁用", total_shortcuts - enabled_count)

    # 功能说明
    with st.expander("📖 功能说明"):
        st.markdown("""
        ### ⌨️ 键盘快捷键系统特性

        **⌨️ 快捷键管理**
        - 🔍 智能搜索和过滤
        - ✏️ 自定义快捷键组合
        - 🔄 启用/禁用控制
        - 🧪 实时测试功能

        **🎙️ 录制功能**
        - 🔴 实时快捷键录制
        - ⌨️ 组合键检测
        - ✅ 冲突检查
        - 💾 自动保存配置

        **👤 配置文件**
        - 🎯 预设专业配置
        - 💼 交易员/分析师专用
        - 📁 导入/导出配置
        - 🔄 一键切换配置

        **📊 使用统计**
        - 📈 使用频率分析
        - ⏰ 时间分布统计
        - 🏆 最常用快捷键
        - 📊 类别使用统计

        **❓ 帮助系统**
        - 📚 分类快捷键列表
        - 💡 使用技巧指南
        - 🔍 快速查找功能
        - 📖 详细操作说明

        **🎯 支持的操作类型**
        - 💰 交易执行 (买入/卖出/套利)
        - 🧭 页面导航 (快速跳转)
        - 📈 图表操作 (缩放/全屏)
        - 📊 数据管理 (刷新/导出)
        - 🖥️ 界面控制 (主题/侧边栏)
        - 🛡️ 风险管理 (紧急停止)
        """)

    return True

if __name__ == "__main__":
    render_keyboard_shortcuts()
