"""
用户偏好设置和配置管理系统
提供个性化设置、配置导入导出、用户配置文件管理等功能
"""

import streamlit as st
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

class UserPreferences:
    """用户偏好设置管理类"""

    def __init__(self):
        self.preferences_file = "user_preferences.json"
        self.default_preferences = self.load_default_preferences()
        self.current_preferences = self.load_user_preferences()

    def load_default_preferences(self):
        """加载默认偏好设置"""
        return {
            "general": {
                "language": "zh-CN",
                "timezone": "Asia/Shanghai",
                "currency_display": "USDT",
                "decimal_places": 4,
                "auto_refresh": True,
                "refresh_interval": 10,
                "sound_alerts": True,
                "desktop_notifications": True
            },
            "trading": {
                "default_amount": 1000,
                "risk_level": "medium",
                "max_slippage": 0.5,
                "auto_execute": False,
                "confirm_trades": True,
                "stop_loss_enabled": True,
                "take_profit_enabled": True,
                "position_size_limit": 10000
            },
            "display": {
                "theme": "dark",
                "chart_style": "candlestick",
                "grid_lines": True,
                "volume_display": True,
                "technical_indicators": ["MA", "RSI", "MACD"],
                "price_alerts_color": "#FF6B6B",
                "profit_color": "#4ECDC4",
                "loss_color": "#FF6B6B"
            },
            "notifications": {
                "email_enabled": False,
                "email_address": "",
                "telegram_enabled": False,
                "telegram_chat_id": "",
                "push_enabled": True,
                "price_change_threshold": 5.0,
                "volume_spike_threshold": 200.0,
                "arbitrage_opportunity_threshold": 0.5
            },
            "shortcuts": {
                "quick_buy": "Ctrl+B",
                "quick_sell": "Ctrl+S",
                "refresh_data": "F5",
                "toggle_chart": "Ctrl+C",
                "open_calculator": "Ctrl+Shift+C",
                "export_data": "Ctrl+E",
                "open_settings": "Ctrl+,",
                "toggle_fullscreen": "F11"
            },
            "dashboard": {
                "layout": "default",
                "widgets": [
                    {"type": "price_ticker", "position": {"x": 0, "y": 0, "w": 6, "h": 2}},
                    {"type": "chart", "position": {"x": 6, "y": 0, "w": 6, "h": 4}},
                    {"type": "orderbook", "position": {"x": 0, "y": 2, "w": 3, "h": 4}},
                    {"type": "trades", "position": {"x": 3, "y": 2, "w": 3, "h": 4}},
                    {"type": "portfolio", "position": {"x": 0, "y": 6, "w": 12, "h": 2}}
                ],
                "auto_arrange": True,
                "compact_mode": False
            }
        }

    def load_user_preferences(self):
        """加载用户偏好设置"""
        try:
            if os.path.exists(self.preferences_file):
                with open(self.preferences_file, 'r', encoding='utf-8') as f:
                    user_prefs = json.load(f)
                # 合并默认设置和用户设置
                return self.merge_preferences(self.default_preferences, user_prefs)
            else:
                return self.default_preferences.copy()
        except Exception as e:
            st.error(f"加载用户偏好设置失败: {str(e)}")
            return self.default_preferences.copy()

    def merge_preferences(self, default: Dict, user: Dict) -> Dict:
        """合并默认设置和用户设置"""
        result = default.copy()
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self.merge_preferences(result[key], value)
            else:
                result[key] = value
        return result

    def save_preferences(self, preferences: Dict):
        """保存用户偏好设置"""
        try:
            with open(self.preferences_file, 'w', encoding='utf-8') as f:
                json.dump(preferences, f, indent=2, ensure_ascii=False)
            self.current_preferences = preferences
            return True
        except Exception as e:
            st.error(f"保存用户偏好设置失败: {str(e)}")
            return False

    def export_preferences(self) -> str:
        """导出偏好设置为JSON字符串"""
        return json.dumps(self.current_preferences, indent=2, ensure_ascii=False)

    def import_preferences(self, json_str: str) -> bool:
        """从JSON字符串导入偏好设置"""
        try:
            imported_prefs = json.loads(json_str)
            merged_prefs = self.merge_preferences(self.default_preferences, imported_prefs)
            return self.save_preferences(merged_prefs)
        except Exception as e:
            st.error(f"导入偏好设置失败: {str(e)}")
            return False

    def reset_to_default(self):
        """重置为默认设置"""
        return self.save_preferences(self.default_preferences.copy())

    def render_general_settings(self):
        """渲染通用设置"""
        st.subheader("🌐 通用设置")

        col1, col2 = st.columns(2)

        with col1:
            # 语言设置
            language = st.selectbox(
                "界面语言",
                ["zh-CN", "en-US", "ja-JP", "ko-KR"],
                index=["zh-CN", "en-US", "ja-JP", "ko-KR"].index(
                    self.current_preferences["general"]["language"]
                ),
                help="选择界面显示语言"
            )

            # 时区设置
            timezone = st.selectbox(
                "时区",
                ["Asia/Shanghai", "UTC", "America/New_York", "Europe/London", "Asia/Tokyo"],
                index=["Asia/Shanghai", "UTC", "America/New_York", "Europe/London", "Asia/Tokyo"].index(
                    self.current_preferences["general"]["timezone"]
                ),
                help="选择显示时区"
            )

            # 货币显示
            currency_display = st.selectbox(
                "默认货币单位",
                ["USDT", "USD", "BTC", "ETH"],
                index=["USDT", "USD", "BTC", "ETH"].index(
                    self.current_preferences["general"]["currency_display"]
                ),
                help="选择价格显示的默认货币单位"
            )

            # 小数位数
            decimal_places = st.slider(
                "价格小数位数",
                min_value=2,
                max_value=8,
                value=self.current_preferences["general"]["decimal_places"],
                help="设置价格显示的小数位数"
            )

        with col2:
            # 自动刷新
            auto_refresh = st.checkbox(
                "启用自动刷新",
                value=self.current_preferences["general"]["auto_refresh"],
                help="自动刷新页面数据"
            )

            # 刷新间隔
            refresh_interval = st.slider(
                "刷新间隔 (秒)",
                min_value=5,
                max_value=60,
                value=self.current_preferences["general"]["refresh_interval"],
                disabled=not auto_refresh,
                help="自动刷新的时间间隔"
            )

            # 声音提醒
            sound_alerts = st.checkbox(
                "启用声音提醒",
                value=self.current_preferences["general"]["sound_alerts"],
                help="重要事件时播放提示音"
            )

            # 桌面通知
            desktop_notifications = st.checkbox(
                "启用桌面通知",
                value=self.current_preferences["general"]["desktop_notifications"],
                help="发送桌面通知消息"
            )

        return {
            "language": language,
            "timezone": timezone,
            "currency_display": currency_display,
            "decimal_places": decimal_places,
            "auto_refresh": auto_refresh,
            "refresh_interval": refresh_interval,
            "sound_alerts": sound_alerts,
            "desktop_notifications": desktop_notifications
        }

    def render_trading_settings(self):
        """渲染交易设置"""
        st.subheader("💼 交易设置")

        col1, col2 = st.columns(2)

        with col1:
            # 默认交易金额
            default_amount = st.number_input(
                "默认交易金额 (USDT)",
                min_value=10,
                max_value=100000,
                value=self.current_preferences["trading"]["default_amount"],
                step=100,
                help="新建交易时的默认金额"
            )

            # 风险等级
            risk_level = st.selectbox(
                "风险等级",
                ["low", "medium", "high"],
                index=["low", "medium", "high"].index(
                    self.current_preferences["trading"]["risk_level"]
                ),
                format_func=lambda x: {"low": "低风险", "medium": "中等风险", "high": "高风险"}[x],
                help="选择交易风险等级"
            )

            # 最大滑点
            max_slippage = st.slider(
                "最大滑点 (%)",
                min_value=0.1,
                max_value=2.0,
                value=self.current_preferences["trading"]["max_slippage"],
                step=0.1,
                help="可接受的最大价格滑点"
            )

            # 仓位限制
            position_size_limit = st.number_input(
                "单笔交易限额 (USDT)",
                min_value=100,
                max_value=100000,
                value=self.current_preferences["trading"]["position_size_limit"],
                step=1000,
                help="单笔交易的最大金额限制"
            )

        with col2:
            # 自动执行
            auto_execute = st.checkbox(
                "启用自动执行",
                value=self.current_preferences["trading"]["auto_execute"],
                help="符合条件时自动执行交易"
            )

            # 交易确认
            confirm_trades = st.checkbox(
                "交易前确认",
                value=self.current_preferences["trading"]["confirm_trades"],
                help="执行交易前显示确认对话框"
            )

            # 止损设置
            stop_loss_enabled = st.checkbox(
                "启用止损",
                value=self.current_preferences["trading"]["stop_loss_enabled"],
                help="自动设置止损订单"
            )

            # 止盈设置
            take_profit_enabled = st.checkbox(
                "启用止盈",
                value=self.current_preferences["trading"]["take_profit_enabled"],
                help="自动设置止盈订单"
            )

        return {
            "default_amount": default_amount,
            "risk_level": risk_level,
            "max_slippage": max_slippage,
            "auto_execute": auto_execute,
            "confirm_trades": confirm_trades,
            "stop_loss_enabled": stop_loss_enabled,
            "take_profit_enabled": take_profit_enabled,
            "position_size_limit": position_size_limit
        }

    def render_display_settings(self):
        """渲染显示设置"""
        st.subheader("🎨 显示设置")

        col1, col2 = st.columns(2)

        with col1:
            # 主题选择
            theme = st.selectbox(
                "界面主题",
                ["dark", "light", "auto"],
                index=["dark", "light", "auto"].index(
                    self.current_preferences["display"]["theme"]
                ),
                format_func=lambda x: {"dark": "深色主题", "light": "浅色主题", "auto": "自动切换"}[x],
                help="选择界面主题"
            )

            # 图表样式
            chart_style = st.selectbox(
                "图表样式",
                ["candlestick", "line", "area"],
                index=["candlestick", "line", "area"].index(
                    self.current_preferences["display"]["chart_style"]
                ),
                format_func=lambda x: {"candlestick": "蜡烛图", "line": "线图", "area": "面积图"}[x],
                help="选择默认图表样式"
            )

            # 网格线
            grid_lines = st.checkbox(
                "显示网格线",
                value=self.current_preferences["display"]["grid_lines"],
                help="在图表中显示网格线"
            )

            # 成交量显示
            volume_display = st.checkbox(
                "显示成交量",
                value=self.current_preferences["display"]["volume_display"],
                help="在图表中显示成交量"
            )

        with col2:
            # 技术指标
            available_indicators = ["MA", "EMA", "RSI", "MACD", "BOLL", "KDJ", "CCI", "WR"]
            technical_indicators = st.multiselect(
                "默认技术指标",
                available_indicators,
                default=self.current_preferences["display"]["technical_indicators"],
                help="选择默认显示的技术指标"
            )

            # 颜色设置
            st.write("**颜色设置**")

            price_alerts_color = st.color_picker(
                "价格提醒颜色",
                value=self.current_preferences["display"]["price_alerts_color"],
                help="价格提醒的显示颜色"
            )

            profit_color = st.color_picker(
                "盈利颜色",
                value=self.current_preferences["display"]["profit_color"],
                help="盈利数据的显示颜色"
            )

            loss_color = st.color_picker(
                "亏损颜色",
                value=self.current_preferences["display"]["loss_color"],
                help="亏损数据的显示颜色"
            )

        return {
            "theme": theme,
            "chart_style": chart_style,
            "grid_lines": grid_lines,
            "volume_display": volume_display,
            "technical_indicators": technical_indicators,
            "price_alerts_color": price_alerts_color,
            "profit_color": profit_color,
            "loss_color": loss_color
        }

    def render_import_export(self):
        """渲染导入导出功能"""
        st.subheader("📁 配置管理")

        col1, col2 = st.columns(2)

        with col1:
            st.write("**导出配置**")

            if st.button("📤 导出当前配置", use_container_width=True):
                config_json = self.export_preferences()
                st.download_button(
                    label="💾 下载配置文件",
                    data=config_json,
                    file_name=f"user_preferences_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )
                st.success("配置已准备下载!")

            if st.button("🔄 重置为默认设置", use_container_width=True):
                if st.session_state.get('confirm_reset', False):
                    if self.reset_to_default():
                        st.success("已重置为默认设置!")
                        st.rerun()
                    else:
                        st.error("重置失败!")
                else:
                    st.session_state.confirm_reset = True
                    st.warning("再次点击确认重置")

        with col2:
            st.write("**导入配置**")

            uploaded_file = st.file_uploader(
                "选择配置文件",
                type=['json'],
                help="上传之前导出的配置文件"
            )

            if uploaded_file is not None:
                try:
                    config_content = uploaded_file.read().decode('utf-8')
                    if st.button("📥 导入配置", use_container_width=True):
                        if self.import_preferences(config_content):
                            st.success("配置导入成功!")
                            st.rerun()
                        else:
                            st.error("配置导入失败!")
                except Exception as e:
                    st.error(f"文件读取失败: {str(e)}")

            # 手动输入配置
            with st.expander("✏️ 手动输入配置"):
                manual_config = st.text_area(
                    "粘贴配置JSON",
                    height=200,
                    placeholder="在此粘贴配置JSON内容..."
                )

                if st.button("导入手动配置") and manual_config:
                    if self.import_preferences(manual_config):
                        st.success("手动配置导入成功!")
                        st.rerun()
                    else:
                        st.error("手动配置导入失败!")

    def render_usage_statistics(self):
        """渲染使用统计"""
        st.subheader("📊 使用统计")

        # 模拟使用数据
        usage_data = {
            "login_times": np.random.randint(50, 200),
            "total_trades": np.random.randint(100, 1000),
            "profit_trades": np.random.randint(60, 700),
            "total_profit": np.random.uniform(1000, 10000),
            "avg_session_time": np.random.uniform(30, 120),
            "favorite_features": ["价格监控", "套利分析", "风险管理", "数据导出"],
            "last_login": datetime.now() - timedelta(hours=np.random.randint(1, 24))
        }

        # 基础统计
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("登录次数", usage_data["login_times"])

        with col2:
            st.metric("总交易次数", usage_data["total_trades"])

        with col3:
            st.metric("盈利交易", usage_data["profit_trades"])

        with col4:
            st.metric("总盈利 (USDT)", f"{usage_data['total_profit']:.2f}")

        # 使用趋势图
        st.subheader("📈 使用趋势")

        # 生成模拟数据
        dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
        daily_usage = np.random.poisson(5, len(dates))
        daily_profit = np.random.normal(50, 20, len(dates))

        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('每日使用时长 (分钟)', '每日盈亏 (USDT)'),
            vertical_spacing=0.1
        )

        # 使用时长
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=daily_usage * 30,  # 转换为分钟
                mode='lines+markers',
                name='使用时长',
                line=dict(color='#4ECDC4', width=2)
            ),
            row=1, col=1
        )

        # 每日盈亏
        colors = ['#4ECDC4' if x >= 0 else '#FF6B6B' for x in daily_profit]
        fig.add_trace(
            go.Bar(
                x=dates,
                y=daily_profit,
                name='每日盈亏',
                marker_color=colors
            ),
            row=2, col=1
        )

        fig.update_layout(
            height=500,
            template="plotly_dark",
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True)

        # 功能使用统计
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🎯 常用功能")
            for i, feature in enumerate(usage_data["favorite_features"]):
                usage_count = np.random.randint(10, 100)
                st.write(f"{i+1}. {feature} - 使用 {usage_count} 次")

        with col2:
            st.subheader("⏰ 会话信息")
            st.write(f"平均会话时长: {usage_data['avg_session_time']:.1f} 分钟")
            st.write(f"上次登录: {usage_data['last_login'].strftime('%Y-%m-%d %H:%M:%S')}")
            st.write(f"胜率: {(usage_data['profit_trades'] / usage_data['total_trades'] * 100):.1f}%")


def render_user_preferences():
    """渲染用户偏好设置主界面"""
    st.title("⚙️ 用户偏好设置")
    st.markdown("个性化定制您的交易体验，优化工作流程")

    # 初始化偏好设置管理器
    if 'preferences_manager' not in st.session_state:
        st.session_state.preferences_manager = UserPreferences()

    prefs_manager = st.session_state.preferences_manager

    # 创建设置标签页
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🌐 通用设置",
        "💼 交易设置",
        "🎨 显示设置",
        "📁 配置管理",
        "📊 使用统计"
    ])

    # 存储更新的设置
    updated_preferences = prefs_manager.current_preferences.copy()

    with tab1:
        general_settings = prefs_manager.render_general_settings()
        updated_preferences["general"] = general_settings

    with tab2:
        trading_settings = prefs_manager.render_trading_settings()
        updated_preferences["trading"] = trading_settings

    with tab3:
        display_settings = prefs_manager.render_display_settings()
        updated_preferences["display"] = display_settings

    with tab4:
        prefs_manager.render_import_export()

    with tab5:
        prefs_manager.render_usage_statistics()

    # 保存设置按钮
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])

    with col2:
        if st.button("💾 保存所有设置", type="primary", use_container_width=True):
            if prefs_manager.save_preferences(updated_preferences):
                st.success("✅ 设置已保存!")
                st.balloons()
                # 更新session state
                st.session_state.preferences_manager = UserPreferences()
            else:
                st.error("❌ 设置保存失败!")

    # 显示当前配置预览
    with st.expander("🔍 当前配置预览"):
        st.json(prefs_manager.current_preferences)
