"""
统一错误处理工具
整合重复的异常处理逻辑
"""

import functools
import logging
import traceback
from typing import Any, Callable, Optional, Union, Dict, List
import streamlit as st
from datetime import datetime

# 配置日志
logger = logging.getLogger(__name__)

class ErrorHandler:
    """统一错误处理器"""

    def __init__(self):
        self.error_counts = {}
        self.last_errors = {}

    def handle_error(self,
                    error: Exception,
                    context: str = "操作",
                    show_user: bool = True,
                    log_level: str = "error",
                    return_value: Any = None) -> Any:
        """
        统一错误处理

        Args:
            error: 异常对象
            context: 错误上下文描述
            show_user: 是否向用户显示错误
            log_level: 日志级别
            return_value: 发生错误时的返回值
        """
        error_msg = str(error)
        error_type = type(error).__name__

        # 记录错误统计
        error_key = f"{context}:{error_type}"
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        self.last_errors[error_key] = {
            'message': error_msg,
            'timestamp': datetime.now(),
            'traceback': traceback.format_exc()
        }

        # 记录日志
        log_message = f"{context}失败: {error_msg}"
        if log_level == "error":
            logger.error(log_message, exc_info=True)
        elif log_level == "warning":
            logger.warning(log_message)
        elif log_level == "info":
            logger.info(log_message)

        # 向用户显示错误
        if show_user:
            self._show_user_error(context, error_msg, error_type)

        return return_value

    def _show_user_error(self, context: str, error_msg: str, error_type: str):
        """向用户显示错误信息"""
        if "网络" in error_msg.lower() or "timeout" in error_msg.lower():
            st.error(f"🌐 网络连接问题: {context}失败，请检查网络连接后重试")
        elif "api" in error_msg.lower() or "key" in error_msg.lower():
            st.error(f"🔑 API问题: {context}失败，请检查API配置")
        elif "permission" in error_msg.lower() or "unauthorized" in error_msg.lower():
            st.error(f"🚫 权限问题: {context}失败，请检查访问权限")
        elif "rate limit" in error_msg.lower():
            st.error(f"⏱️ 请求频率限制: {context}失败，请稍后重试")
        else:
            st.error(f"❌ {context}失败: {error_msg}")

    def get_error_stats(self) -> Dict[str, Any]:
        """获取错误统计信息"""
        return {
            'error_counts': self.error_counts,
            'last_errors': self.last_errors,
            'total_errors': sum(self.error_counts.values())
        }

    def clear_stats(self):
        """清除错误统计"""
        self.error_counts.clear()
        self.last_errors.clear()

# 全局错误处理器实例
error_handler = ErrorHandler()

def safe_execute(context: str = "操作",
                show_user: bool = True,
                log_level: str = "error",
                return_value: Any = None,
                suppress_errors: List[type] = None):
    """
    安全执行装饰器

    Args:
        context: 操作上下文描述
        show_user: 是否向用户显示错误
        log_level: 日志级别
        return_value: 发生错误时的返回值
        suppress_errors: 要抑制的异常类型列表
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # 检查是否需要抑制特定异常
                if suppress_errors and type(e) in suppress_errors:
                    return return_value

                return error_handler.handle_error(
                    error=e,
                    context=context,
                    show_user=show_user,
                    log_level=log_level,
                    return_value=return_value
                )
        return wrapper
    return decorator

def safe_api_call(func: Callable,
                 context: str = "API调用",
                 max_retries: int = 3,
                 retry_delay: float = 1.0,
                 *args, **kwargs) -> Any:
    """
    安全的API调用，带重试机制

    Args:
        func: 要调用的函数
        context: 操作上下文
        max_retries: 最大重试次数
        retry_delay: 重试延迟
    """
         import time

    last_error = None
    for attempt in range(max_retries + 1):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            last_error = e
            if attempt < max_retries:
                logger.warning(f"{context}第{attempt + 1}次尝试失败，{retry_delay}秒后重试: {str(e)}")
                time.sleep(retry_delay)
                retry_delay *= 2  # 指数退避
            else:
                return error_handler.handle_error(
                    error=e,
                    context=f"{context}(重试{max_retries}次后)",
                    show_user=True,
                    log_level="error"
                )

def validate_input(value: Any,
                  value_type: type = None,
                  min_value: Union[int, float] = None,
                  max_value: Union[int, float] = None,
                  allowed_values: List[Any] = None,
                  not_empty: bool = False) -> bool:
    """
    输入验证

    Args:
        value: 要验证的值
        value_type: 期望的类型
        min_value: 最小值
        max_value: 最大值
        allowed_values: 允许的值列表
        not_empty: 是否不能为空
    """
    try:
        # 类型检查
        if value_type and not isinstance(value, value_type):
            raise ValueError(f"期望类型 {value_type.__name__}，实际类型 {type(value).__name__}")

        # 空值检查
        if not_empty and (value is None or value == "" or (hasattr(value, '__len__') and len(value) == 0)):
            raise ValueError("值不能为空")

        # 数值范围检查
        if isinstance(value, (int, float)):
            if min_value is not None and value < min_value:
                raise ValueError(f"值 {value} 小于最小值 {min_value}")
            if max_value is not None and value > max_value:
                raise ValueError(f"值 {value} 大于最大值 {max_value}")

        # 允许值检查
        if allowed_values and value not in allowed_values:
            raise ValueError(f"值 {value} 不在允许的值列表中: {allowed_values}")

        return True

    except ValueError as e:
        error_handler.handle_error(e, "输入验证", show_user=True, log_level="warning")
        return False

class ErrorContext:
    """错误上下文管理器"""

    def __init__(self, context: str, show_user: bool = True, return_value: Any = None):
        self.context = context
        self.show_user = show_user
        self.return_value = return_value

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            error_handler.handle_error(
                error=exc_val,
                context=self.context,
                show_user=self.show_user,
                return_value=self.return_value
            )
            return True  # 抑制异常
        return False

# 常用的安全执行装饰器
safe_data_operation = safe_execute("数据操作", return_value=None)
safe_api_operation = safe_execute("API操作", return_value={})
safe_ui_operation = safe_execute("界面操作", return_value=None, log_level="warning")
safe_calculation = safe_execute("计算操作", return_value=0)

# 便利函数
def handle_streamlit_error(func: Callable) -> Callable:
    """Streamlit专用错误处理装饰器"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            st.error(f"操作失败: {str(e)}")
            logger.error(f"Streamlit操作失败: {str(e)}", exc_info=True)
            return None
    return wrapper

def log_performance(func: Callable) -> Callable:
    """性能日志装饰器"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
         import time
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            if execution_time > 1.0:  # 超过1秒记录警告
                logger.warning(f"函数 {func.__name__} 执行时间较长: {execution_time:.2f}秒")
            else:
                logger.debug(f"函数 {func.__name__} 执行时间: {execution_time:.2f}秒")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"函数 {func.__name__} 执行失败 (耗时 {execution_time:.2f}秒): {str(e)}")
            raise
    return wrapper

def retry_on_failure(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """重试装饰器"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(f"函数 {func.__name__} 第{attempt + 1}次尝试失败，{current_delay}秒后重试")
         import time
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(f"函数 {func.__name__} 重试{max_retries}次后仍然失败")
                        raise last_exception
        return wrapper
    return decorator

# 错误报告功能
class ErrorReporter:
    """错误报告器"""

    @staticmethod
    def generate_error_report() -> Dict[str, Any]:
        """生成错误报告"""
        stats = error_handler.get_error_stats()

        # 按错误类型分组
        error_by_type = {}
        for error_key, count in stats['error_counts'].items():
            context, error_type = error_key.split(':', 1)
            if error_type not in error_by_type:
                error_by_type[error_type] = []
            error_by_type[error_type].append({
                'context': context,
                'count': count,
                'last_error': stats['last_errors'].get(error_key, {})
            })

        return {
            'total_errors': stats['total_errors'],
            'error_types': len(error_by_type),
            'errors_by_type': error_by_type,
            'most_common_errors': sorted(
                stats['error_counts'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
        }

    @staticmethod
    def display_error_dashboard():
        """显示错误仪表盘"""
        report = ErrorReporter.generate_error_report()

        st.subheader("🚨 错误统计")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("总错误数", report['total_errors'])
        with col2:
            st.metric("错误类型数", report['error_types'])
        with col3:
            if report['most_common_errors']:
                most_common = report['most_common_errors'][0]
                st.metric("最常见错误", most_common[1], f"{most_common[0].split(':', 1)[1]}")

        if report['most_common_errors']:
            st.subheader("最常见错误")
            for error_key, count in report['most_common_errors']:
                context, error_type = error_key.split(':', 1)
                st.write(f"- **{error_type}** 在 {context}: {count} 次")

# 导出主要功能
__all__ = [
    'ErrorHandler', 'error_handler', 'safe_execute', 'safe_api_call',
    'validate_input', 'ErrorContext', 'handle_streamlit_error',
    'log_performance', 'retry_on_failure', 'ErrorReporter',
    'safe_data_operation', 'safe_api_operation', 'safe_ui_operation', 'safe_calculation'
]
