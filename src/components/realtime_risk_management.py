"""
实时风险管理模块
提供全面的风险监控、控制和预警功能
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import random
import time


class RealtimeRiskManagement:
    """实时风险管理系统"""

    def __init__(self):
        self.exchanges = ["Binance", "OKX", "Huobi", "KuCoin", "Gate.io", "Bybit"]
        self.currencies = ["BTC", "ETH", "BNB", "ADA", "DOT", "LINK", "UNI", "MATIC", "USDT", "USDC"]

        # 初始化session state
        if "risk_mgmt_portfolio_data" not in st.session_state:
            st.session_state.risk_mgmt_portfolio_data = self.generate_portfolio_data()
        if "risk_alerts" not in st.session_state:
            st.session_state.risk_alerts = []
        if "emergency_mode" not in st.session_state:
            st.session_state.emergency_mode = False
        if "risk_limits" not in st.session_state:
            st.session_state.risk_limits = {
                "max_exchange_exposure": 30,  # 单个交易所最大敞口百分比
                "max_currency_exposure": 25,  # 单个货币最大敞口百分比
                "max_daily_loss": 5,  # 最大日损失百分比
                "min_margin_ratio": 150,  # 最小保证金比例
                "max_volatility_threshold": 20  # 最大波动率阈值
            }

    def generate_portfolio_data(self):
        """生成投资组合数据"""
        portfolio = []
        total_value = 100000  # 总价值100k USD

        for exchange in self.exchanges:
            exchange_allocation = random.uniform(0.1, 0.3)
            exchange_value = total_value * exchange_allocation

            # 为每个交易所分配不同货币
            num_currencies = random.randint(3, 6)
            selected_currencies = random.sample(self.currencies, num_currencies)

            for currency in selected_currencies:
                if currency in ["USDT", "USDC"]:
                    price = 1.0
                    allocation = random.uniform(0.1, 0.4)
                elif currency == "BTC":
                    price = random.uniform(40000, 50000)
                    allocation = random.uniform(0.2, 0.5)
                elif currency == "ETH":
                    price = random.uniform(2500, 3500)
                    allocation = random.uniform(0.15, 0.4)
                else:
                    price = random.uniform(0.5, 100)
                    allocation = random.uniform(0.05, 0.3)

                position_value = exchange_value * allocation
                quantity = position_value / price

                # 计算风险指标
                volatility = random.uniform(5, 30)  # 年化波动率
                var_1d = position_value * 0.01 * volatility / np.sqrt(252)  # 1日VaR

                portfolio.append({
                    "exchange": exchange,
                    "currency": currency,
                    "quantity": quantity,
                    "price": price,
                    "value": position_value,
                    "allocation": allocation,
                    "volatility": volatility,
                    "var_1d": var_1d,
                    "margin_ratio": random.uniform(120, 300) if currency not in ["USDT", "USDC"] else None,
                    "last_update": datetime.now()
                })

        return pd.DataFrame(portfolio)

    def calculate_risk_metrics(self, portfolio_df):
        """计算风险指标"""
        total_value = portfolio_df["value"].sum()

        # 交易所敞口
        exchange_exposure = portfolio_df.groupby("exchange")["value"].sum() / total_value * 100

        # 货币敞口
        currency_exposure = portfolio_df.groupby("currency")["value"].sum() / total_value * 100

        # 总VaR
        total_var = portfolio_df["var_1d"].sum()

        # 最大回撤（模拟）
        max_drawdown = random.uniform(2, 8)

        # 夏普比率（模拟）
        sharpe_ratio = random.uniform(0.8, 2.5)

        # 保证金使用率
        margin_positions = portfolio_df[portfolio_df["margin_ratio"].notna()]
        if not margin_positions.empty:
            avg_margin_ratio = margin_positions["margin_ratio"].mean()
            margin_utilization = 100 / avg_margin_ratio * 100
        else:
            margin_utilization = 0

        return {
            "total_value": total_value,
            "exchange_exposure": exchange_exposure,
            "currency_exposure": currency_exposure,
            "total_var": total_var,
            "var_percentage": total_var / total_value * 100,
            "max_drawdown": max_drawdown,
            "sharpe_ratio": sharpe_ratio,
            "margin_utilization": margin_utilization
        }

    def check_risk_violations(self, metrics):
        """检查风险违规"""
        violations = []
        limits = st.session_state.risk_limits

        # 检查交易所敞口
        for exchange, exposure in metrics["exchange_exposure"].items():
            if exposure > limits["max_exchange_exposure"]:
                violations.append({
                    "type": "exchange_exposure",
                    "severity": "high" if exposure > limits["max_exchange_exposure"] * 1.2 else "medium",
                    "message": f"{exchange} 敞口过高: {exposure:.1f}% (限制: {limits['max_exchange_exposure']}%)",
                    "value": exposure,
                    "limit": limits["max_exchange_exposure"]
                })

        # 检查货币敞口
        for currency, exposure in metrics["currency_exposure"].items():
            if exposure > limits["max_currency_exposure"]:
                violations.append({
                    "type": "currency_exposure",
                    "severity": "high" if exposure > limits["max_currency_exposure"] * 1.2 else "medium",
                    "message": f"{currency} 敞口过高: {exposure:.1f}% (限制: {limits['max_currency_exposure']}%)",
                    "value": exposure,
                    "limit": limits["max_currency_exposure"]
                })

        # 检查VaR
        if metrics["var_percentage"] > limits["max_daily_loss"]:
            violations.append({
                "type": "var_limit",
                "severity": "high",
                "message": f"日VaR过高: {metrics['var_percentage']:.2f}% (限制: {limits['max_daily_loss']}%)",
                "value": metrics["var_percentage"],
                "limit": limits["max_daily_loss"]
            })

        # 检查保证金比例
        if metrics["margin_utilization"] > 100 - limits["min_margin_ratio"]:
            violations.append({
                "type": "margin_risk",
                "severity": "critical",
                "message": f"保证金使用率过高: {metrics['margin_utilization']:.1f}%",
                "value": metrics["margin_utilization"],
                "limit": 100 - limits["min_margin_ratio"]
            })

        return violations

    def render_risk_dashboard_overview(self, metrics):
        """渲染风险仪表板概览"""
        st.subheader("🛡️ 风险概览")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "投资组合价值",
                f"${metrics['total_value']:,.0f}",
                delta=f"{random.uniform(-2, 5):.1f}%"
            )

        with col2:
            var_color = "normal"
            if metrics["var_percentage"] > st.session_state.risk_limits["max_daily_loss"]:
                var_color = "inverse"

            st.metric(
                "日风险价值 (VaR)",
                f"${metrics['total_var']:,.0f}",
                delta=f"{metrics['var_percentage']:.2f}%",
                delta_color=var_color
            )

        with col3:
            st.metric(
                "最大回撤",
                f"{metrics['max_drawdown']:.1f}%",
                delta=f"{random.uniform(-0.5, 0.3):.1f}%"
            )

        with col4:
            st.metric(
                "夏普比率",
                f"{metrics['sharpe_ratio']:.2f}",
                delta=f"{random.uniform(-0.1, 0.2):.2f}"
            )

    def render_exposure_analysis(self, metrics):
        """渲染敞口分析"""
        st.subheader("📊 敞口分析")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**交易所敞口分布**")

            # 交易所敞口饼图
            fig = px.pie(
                values=metrics["exchange_exposure"].values,
                names=metrics["exchange_exposure"].index,
                title="交易所敞口分布"
            )

            # 添加风险限制线
            for exchange, exposure in metrics["exchange_exposure"].items():
                if exposure > st.session_state.risk_limits["max_exchange_exposure"]:
                    fig.add_annotation(
                        text=f"⚠️ {exchange} 超限",
                        x=0.5, y=0.1,
                        showarrow=False,
                        font=dict(color="red", size=12)
                    )

            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("**货币敞口分布**")

            # 货币敞口柱状图
            fig = px.bar(
                x=metrics["currency_exposure"].index,
                y=metrics["currency_exposure"].values,
                title="货币敞口分布",
                labels={"x": "货币", "y": "敞口 (%)"}
            )

            # 添加风险限制线
            fig.add_hline(
                y=st.session_state.risk_limits["max_currency_exposure"],
                line_dash="dash",
                line_color="red",
                annotation_text="风险限制"
            )

            st.plotly_chart(fig, use_container_width=True)

    def render_risk_alerts(self, violations):
        """渲染风险警报"""
        st.subheader("🚨 风险警报")

        if not violations:
            st.success("✅ 当前无风险警报")
            return

        # 按严重程度分组
        critical_alerts = [v for v in violations if v["severity"] == "critical"]
        high_alerts = [v for v in violations if v["severity"] == "high"]
        medium_alerts = [v for v in violations if v["severity"] == "medium"]

        if critical_alerts:
            st.error("🔴 **严重警报**")
            for alert in critical_alerts:
                st.error(f"• {alert['message']}")

        if high_alerts:
            st.warning("🟡 **高风险警报**")
            for alert in high_alerts:
                st.warning(f"• {alert['message']}")

        if medium_alerts:
            st.info("🟠 **中风险警报**")
            for alert in medium_alerts:
                st.info(f"• {alert['message']}")

        # 添加到历史警报
        for violation in violations:
            violation["timestamp"] = datetime.now()
            st.session_state.risk_alerts.append(violation)

        # 保持最近100条警报
        st.session_state.risk_alerts = st.session_state.risk_alerts[-100:]

    def render_emergency_controls(self):
        """渲染紧急控制"""
        st.subheader("🚨 紧急控制")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button(
                "🛑 全局止损",
                type="primary",
                help="立即平仓所有风险头寸"
            ):
                st.session_state.emergency_mode = True
                st.error("🚨 全局止损已激活！")
                st.info("正在平仓所有风险头寸...")
                # 这里会调用实际的平仓逻辑

        with col2:
            if st.button(
                "⏸️ 暂停交易",
                help="暂停所有自动交易"
            ):
                st.warning("⏸️ 自动交易已暂停")
                # 这里会暂停所有自动交易

        with col3:
            if st.button(
                "💰 转换稳定币",
                help="将所有头寸转换为USDT"
            ):
                st.info("🔄 正在转换为稳定币...")
                # 这里会执行稳定币转换

        if st.session_state.emergency_mode:
            st.error("🚨 **紧急模式已激活**")
            if st.button("🔄 重置紧急模式"):
                st.session_state.emergency_mode = False
                st.success("✅ 紧急模式已重置")
                st.rerun()

    def render_position_monitoring(self, portfolio_df):
        """渲染头寸监控"""
        st.subheader("📈 实时头寸监控")

        # 头寸表格
        display_df = portfolio_df.copy()
        display_df["价值"] = display_df["value"].apply(lambda x: f"${x:,.0f}")
        display_df["数量"] = display_df["quantity"].apply(lambda x: f"{x:,.4f}")
        display_df["价格"] = display_df["price"].apply(lambda x: f"${x:,.2f}")
        display_df["波动率"] = display_df["volatility"].apply(lambda x: f"{x:.1f}%")
        display_df["VaR"] = display_df["var_1d"].apply(lambda x: f"${x:,.0f}")

        # 保证金比例
        display_df["保证金比例"] = display_df["margin_ratio"].apply(
            lambda x: f"{x:.0f}%" if pd.notna(x) else "现货"
        )

        # 风险等级
        def get_risk_level(row):
            if row["volatility"] > 25:
                return "🔴 高"
            elif row["volatility"] > 15:
                return "🟡 中"
            else:
                return "🟢 低"

        display_df["风险等级"] = portfolio_df.apply(get_risk_level, axis=1)

        st.dataframe(
            display_df[["exchange", "currency", "数量", "价格", "价值", "波动率", "VaR", "保证金比例", "风险等级"]],
            column_config={
                "exchange": "交易所",
                "currency": "货币"
            },
            use_container_width=True,
            height=400
        )

    def render_volatility_monitoring(self, portfolio_df):
        """渲染波动率监控"""
        st.subheader("📊 波动率监控")

        # 生成历史波动率数据
        dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
        volatility_data = []

        for currency in portfolio_df["currency"].unique():
            if currency not in ["USDT", "USDC"]:
                base_vol = portfolio_df[portfolio_df["currency"] == currency]["volatility"].iloc[0]
                for date in dates:
                    vol = base_vol + random.uniform(-5, 5)
                    volatility_data.append({
                        "date": date,
                        "currency": currency,
                        "volatility": max(0, vol)
                    })

        vol_df = pd.DataFrame(volatility_data)

        # 波动率趋势图
        fig = px.line(
            vol_df,
            x="date",
            y="volatility",
            color="currency",
            title="30日波动率趋势",
            labels={"volatility": "波动率 (%)", "date": "日期"}
        )

        # 添加风险阈值线
        fig.add_hline(
            y=st.session_state.risk_limits["max_volatility_threshold"],
            line_dash="dash",
            line_color="red",
            annotation_text="风险阈值"
        )

        st.plotly_chart(fig, use_container_width=True)

        # 当前高波动率资产
        high_vol_assets = portfolio_df[
            portfolio_df["volatility"] > st.session_state.risk_limits["max_volatility_threshold"]
        ]

        if not high_vol_assets.empty:
            st.warning("⚠️ **高波动率资产警告**")
            for _, asset in high_vol_assets.iterrows():
                st.write(f"• {asset['currency']} ({asset['exchange']}): {asset['volatility']:.1f}%")

    def render_margin_monitoring(self, portfolio_df):
        """渲染保证金监控"""
        st.subheader("💰 保证金监控")

        margin_positions = portfolio_df[portfolio_df["margin_ratio"].notna()]

        if margin_positions.empty:
            st.info("当前无保证金头寸")
            return

        # 保证金比例分布
        fig = px.bar(
            margin_positions,
            x="currency",
            y="margin_ratio",
            color="exchange",
            title="保证金比例分布",
            labels={"margin_ratio": "保证金比例 (%)", "currency": "货币"}
        )

        # 添加最小保证金要求线
        fig.add_hline(
            y=st.session_state.risk_limits["min_margin_ratio"],
            line_dash="dash",
            line_color="red",
            annotation_text="最小要求"
        )

        st.plotly_chart(fig, use_container_width=True)

        # 保证金风险警告
        risky_positions = margin_positions[
            margin_positions["margin_ratio"] < st.session_state.risk_limits["min_margin_ratio"] * 1.2
        ]

        if not risky_positions.empty:
            st.error("🚨 **保证金风险警告**")
            for _, pos in risky_positions.iterrows():
                st.error(f"• {pos['currency']} ({pos['exchange']}): {pos['margin_ratio']:.0f}%")

    def render_risk_settings(self):
        """渲染风险设置"""
        st.subheader("⚙️ 风险参数设置")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**敞口限制**")

            max_exchange_exposure = st.slider(
                "单交易所最大敞口 (%)",
                10, 50,
                st.session_state.risk_limits["max_exchange_exposure"],
                5
            )

            max_currency_exposure = st.slider(
                "单货币最大敞口 (%)",
                10, 40,
                st.session_state.risk_limits["max_currency_exposure"],
                5
            )

        with col2:
            st.markdown("**风险限制**")

            max_daily_loss = st.slider(
                "最大日损失 (%)",
                1, 10,
                st.session_state.risk_limits["max_daily_loss"],
                1
            )

            min_margin_ratio = st.slider(
                "最小保证金比例 (%)",
                100, 200,
                st.session_state.risk_limits["min_margin_ratio"],
                10
            )

        # 更新设置
        if st.button("💾 保存设置"):
            st.session_state.risk_limits.update({
                "max_exchange_exposure": max_exchange_exposure,
                "max_currency_exposure": max_currency_exposure,
                "max_daily_loss": max_daily_loss,
                "min_margin_ratio": min_margin_ratio
            })
            st.success("✅ 风险参数已更新")


def render_realtime_risk_management():
    """渲染实时风险管理主界面"""
    st.title("🛡️ 实时风险管理系统")
    st.markdown("---")

    risk_mgmt = RealtimeRiskManagement()

    # 初始化或获取投资组合数据
    if 'risk_mgmt_portfolio_data' not in st.session_state or st.session_state.risk_mgmt_portfolio_data is None:
        st.session_state.risk_mgmt_portfolio_data = risk_mgmt.generate_portfolio_data()
    
    portfolio_df = st.session_state.risk_mgmt_portfolio_data
    
    # 验证数据框结构
    required_columns = ['exchange', 'currency', 'quantity', 'price', 'value', 'allocation', 'volatility', 'var_1d']
    if not isinstance(portfolio_df, pd.DataFrame):
        st.warning(f"投资组合数据不是DataFrame格式，当前类型: {type(portfolio_df)}，正在重新生成...")
        st.session_state.risk_mgmt_portfolio_data = risk_mgmt.generate_portfolio_data()
        portfolio_df = st.session_state.risk_mgmt_portfolio_data
    elif not all(col in portfolio_df.columns for col in required_columns):
        missing_cols = [col for col in required_columns if col not in portfolio_df.columns]
        st.warning(f"投资组合数据缺少必要列: {missing_cols}，当前列: {list(portfolio_df.columns)}，正在重新生成...")
        st.session_state.risk_mgmt_portfolio_data = risk_mgmt.generate_portfolio_data()
        portfolio_df = st.session_state.risk_mgmt_portfolio_data

    # 计算风险指标
    with st.spinner("计算风险指标..."):
        try:
            metrics = risk_mgmt.calculate_risk_metrics(portfolio_df)
            violations = risk_mgmt.check_risk_violations(metrics)
        except Exception as e:
            st.error(f"计算风险指标时出错: {str(e)}")
            st.info("正在重新生成投资组合数据...")
            st.session_state.risk_mgmt_portfolio_data = risk_mgmt.generate_portfolio_data()
            portfolio_df = st.session_state.risk_mgmt_portfolio_data
            metrics = risk_mgmt.calculate_risk_metrics(portfolio_df)
            violations = risk_mgmt.check_risk_violations(metrics)

    # 渲染各个组件
    risk_mgmt.render_risk_dashboard_overview(metrics)
    st.markdown("---")

    risk_mgmt.render_risk_alerts(violations)
    st.markdown("---")

    risk_mgmt.render_emergency_controls()
    st.markdown("---")

    risk_mgmt.render_exposure_analysis(metrics)
    st.markdown("---")

    risk_mgmt.render_position_monitoring(portfolio_df)
    st.markdown("---")

    risk_mgmt.render_volatility_monitoring(portfolio_df)
    st.markdown("---")

    risk_mgmt.render_margin_monitoring(portfolio_df)
    st.markdown("---")

    risk_mgmt.render_risk_settings()

    # 刷新按钮
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🔄 刷新数据", key="risk_mgmt_refresh"):
            st.session_state.portfolio_data = risk_mgmt.generate_portfolio_data()
            st.rerun()

    with col2:
        st.markdown(f"*最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
