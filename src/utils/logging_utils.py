"""
日志工具模块
提供统一的日志记录和错误处理功能
"""

import logging
import traceback
import streamlit as st
from typing import Optional, Any, Callable
from functools import wraps
import os
from datetime import datetime

# 配置日志
def setup_logging():
    """设置应用日志配置"""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file = os.path.join(log_dir, f"app_{datetime.now().strftime('%Y%m%d')}.log")

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

    return logging.getLogger(__name__)

logger = setup_logging()

class ComponentError(Exception):
    """组件相关错误基类"""
    pass

class ImportComponentError(ComponentError):
    """组件导入错误"""
    pass

class RenderComponentError(ComponentError):
    """组件渲染错误"""
    pass

class DataServiceError(Exception):
    """数据服务错误"""
    pass

class APIConnectionError(DataServiceError):
    """API连接错误"""
    pass

class ConfigurationError(Exception):
    """配置错误"""
    pass

def log_error(error: Exception, context: str = "", component: str = ""):
    """记录详细错误信息"""
    error_info = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "context": context,
        "component": component,
        "traceback": traceback.format_exc()
    }

    logger.error(f"Error in {component}: {context}", extra=error_info)
    return error_info

def safe_component_loader(component_name: str, import_path: str, render_function: str):
    """安全的组件加载器"""
    try:
        # 尝试导入模块
        module = __import__(import_path, fromlist=[render_function])
        render_func = getattr(module, render_function)

        # 尝试渲染组件
        render_func()

    except ImportError as e:
        error_info = log_error(e, f"导入{component_name}组件失败", component_name)
        st.error(f"❌ {component_name}组件导入失败")
        st.error(f"错误详情: {str(e)}")
        st.info("💡 请检查组件文件是否存在，或联系开发人员")

    except AttributeError as e:
        error_info = log_error(e, f"{component_name}组件中缺少渲染函数", component_name)
        st.error(f"❌ {component_name}组件配置错误")
        st.error(f"错误详情: 找不到渲染函数 '{render_function}'")
        st.info("💡 请联系开发人员检查组件配置")

    except APIConnectionError as e:
        error_info = log_error(e, f"{component_name}组件API连接失败", component_name)
        st.error(f"🌐 {component_name}组件网络连接失败")
        st.error(f"错误详情: {str(e)}")
        st.info("💡 请检查网络连接和API密钥配置")

    except DataServiceError as e:
        error_info = log_error(e, f"{component_name}组件数据服务错误", component_name)
        st.error(f"📊 {component_name}组件数据获取失败")
        st.error(f"错误详情: {str(e)}")
        st.info("💡 请稍后重试，或检查数据服务状态")

    except ConfigurationError as e:
        error_info = log_error(e, f"{component_name}组件配置错误", component_name)
        st.error(f"⚙️ {component_name}组件配置错误")
        st.error(f"错误详情: {str(e)}")
        st.info("💡 请检查配置文件或联系管理员")

    except Exception as e:
        error_info = log_error(e, f"{component_name}组件未知错误", component_name)
        st.error(f"❌ {component_name}组件发生未知错误")
        st.error(f"错误类型: {type(e).__name__}")
        st.error(f"错误详情: {str(e)}")

        # 显示详细错误信息（仅在开发模式下）
        if st.session_state.get('debug_mode', False):
            st.code(traceback.format_exc())

        st.info("💡 错误已记录，请联系开发人员或稍后重试")

def error_handler(component_name: str):
    """装饰器：为函数添加错误处理"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                log_error(e, f"执行{func.__name__}时发生错误", component_name)
                raise
        return wrapper
    return decorator

def display_error_summary():
    """显示错误摘要（用于调试）"""
    if st.session_state.get('debug_mode', False):
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🐛 调试信息")

        log_file = f"logs/app_{datetime.now().strftime('%Y%m%d')}.log"
        if os.path.exists(log_file):
            if st.sidebar.button("查看今日错误日志"):
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        logs = f.read()
                    st.sidebar.text_area("错误日志", logs, height=200)
                except Exception as e:
                    st.sidebar.error(f"无法读取日志文件: {e}")
