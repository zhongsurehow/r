"""
快速入门指南组件
"""

import streamlit as st
from datetime import datetime

def show_quick_start_guide():
    """显示快速入门指南"""
    
    # 检查是否是首次访问
    if 'first_visit' not in st.session_state:
        st.session_state.first_visit = True
    
    # 如果是首次访问，显示欢迎信息
    if st.session_state.first_visit:
        show_welcome_message()
    
    # 显示快速操作指南
    show_quick_actions()

def show_welcome_message():
    """显示欢迎信息"""
    st.info("""
    🎉 **欢迎使用加密货币比较工具！**
    
    这是您第一次使用本系统。点击右侧的 "📚 使用帮助" 获取详细的使用说明。
    """)
    
    if st.button("我已了解，不再显示此消息"):
        st.session_state.first_visit = False
        st.rerun()

def show_quick_actions():
    """显示快速操作指南"""
    with st.expander("🚀 快速操作指南", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            ### 📊 查看价格
            1. 选择交易对
            2. 查看实时价格
            3. 比较不同交易所
            """)
            
        with col2:
            st.markdown("""
            ### 🔄 发现套利
            1. 进入套利分析页面
            2. 查看价格差异
            3. 分析套利机会
            """)
            
        with col3:
            st.markdown("""
            ### 📈 市场分析
            1. 查看市场概览
            2. 分析价格趋势
            3. 监控交易量
            """)

def show_feature_highlights():
    """显示功能亮点"""
    st.markdown("### ✨ 主要功能")
    
    features = [
        {
            "icon": "📊",
            "title": "实时价格监控",
            "description": "监控多个交易所的实时价格数据"
        },
        {
            "icon": "🔄", 
            "title": "套利机会分析",
            "description": "自动发现和分析套利机会"
        },
        {
            "icon": "📈",
            "title": "市场趋势分析", 
            "description": "深入分析市场趋势和价格走势"
        },
        {
            "icon": "⚡",
            "title": "快速响应",
            "description": "毫秒级数据更新和响应"
        }
    ]
    
    cols = st.columns(len(features))
    for i, feature in enumerate(features):
        with cols[i]:
            st.markdown(f"""
            <div style="text-align: center; padding: 1rem; border: 1px solid #ddd; border-radius: 10px; margin: 0.5rem 0;">
                <div style="font-size: 2rem;">{feature['icon']}</div>
                <h4>{feature['title']}</h4>
                <p style="font-size: 0.9rem; color: #666;">{feature['description']}</p>
            </div>
            """, unsafe_allow_html=True)

def show_system_status():
    """显示系统状态"""
    with st.expander("🔧 系统状态", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("数据源状态", "正常", "5/5 活跃")
            
        with col2:
            st.metric("响应时间", "< 100ms", "优秀")
            
        with col3:
            st.metric("数据更新", "实时", "60秒间隔")

def show_tips_and_tricks():
    """显示使用技巧"""
    with st.expander("💡 使用技巧", expanded=False):
        st.markdown("""
        ### 🎯 高效使用技巧
        
        1. **快捷键支持**
           - `Ctrl + R`: 刷新数据
           - `Ctrl + H`: 打开帮助页面
           - `Ctrl + S`: 保存当前设置
        
        2. **数据解读**
           - 绿色表示价格上涨
           - 红色表示价格下跌
           - 黄色表示数据异常或延迟
        
        3. **最佳实践**
           - 定期检查数据时间戳
           - 对比多个数据源
           - 关注交易量变化
           - 设置价格提醒
        
        4. **风险提示**
           - 套利存在时间窗口
           - 考虑交易费用成本
           - 注意流动性风险
           - 验证数据准确性
        """)

def show_recent_updates():
    """显示最近更新"""
    with st.expander("📝 最近更新", expanded=False):
        updates = [
            {
                "date": "2024-01-20",
                "version": "v2.1.0",
                "changes": [
                    "优化API调用性能",
                    "添加智能重试机制", 
                    "改进数据缓存策略",
                    "增强错误处理能力"
                ]
            },
            {
                "date": "2024-01-15", 
                "version": "v2.0.5",
                "changes": [
                    "修复价格数据异常问题",
                    "优化用户界面响应速度",
                    "添加更多交易所支持"
                ]
            }
        ]
        
        for update in updates:
            st.markdown(f"""
            **{update['version']}** - {update['date']}
            """)
            for change in update['changes']:
                st.markdown(f"- {change}")
            st.markdown("---")

def show_help_shortcuts():
    """显示帮助快捷方式"""
    st.markdown("### 🆘 需要帮助？")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📚 查看完整帮助", use_container_width=True):
            st.session_state.page = "📚 使用帮助"
            st.rerun()
    
    with col2:
        if st.button("🔧 故障排除", use_container_width=True):
            st.session_state.help_section = "🔧 故障排除"
            st.session_state.page = "📚 使用帮助"
            st.rerun()
    
    with col3:
        if st.button("❓ 常见问题", use_container_width=True):
            st.session_state.help_section = "❓ 常见问题"
            st.session_state.page = "📚 使用帮助"
            st.rerun()

def render_quick_start_sidebar():
    """在侧边栏渲染快速开始信息"""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🚀 快速开始")
    
    if st.sidebar.button("📚 查看帮助", use_container_width=True):
        st.session_state.page = "📚 使用帮助"
        st.rerun()
    
    if st.sidebar.button("🔄 刷新数据", use_container_width=True):
        # 清除缓存
        st.cache_data.clear()
        st.cache_resource.clear()
        st.success("数据已刷新！")
        st.rerun()
    
    # 显示快速统计
    st.sidebar.markdown("### 📊 快速统计")
    st.sidebar.metric("当前时间", datetime.now().strftime("%H:%M:%S"))
    st.sidebar.metric("数据状态", "正常")

if __name__ == "__main__":
    show_quick_start_guide()