"""
统一错误处理器
整合所有错误处理功能，提供一致的错误处理体验
"""

import uuid
import time
import traceback
import functools
import asyncio
from typing import Dict, List, Any, Optional, Callable, Union, Type
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import streamlit as st
import logging

from config.error_config import (
    ErrorLevel, ErrorCategory, ErrorHandlingConfig,
    get_error_config, get_error_message, get_error_level,
    get_error_category, get_retry_strategy, get_circuit_breaker_config
)

# 配置日志
logger = logging.getLogger(__name__)


@dataclass
class ErrorRecord:
    """错误记录"""
    id: str
    timestamp: datetime
    error_type: str
    error_message: str
    error_details: str
    category: ErrorCategory
    level: ErrorLevel
    function_name: str
    file_name: str
    line_number: int
    user_message: str
    suggestions: List[str]
    context: Dict[str, Any] = field(default_factory=dict)
    resolved: bool = False
    resolution_time: Optional[datetime] = None


class CircuitBreaker:
    """熔断器"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func: Callable, *args, **kwargs):
        """执行函数调用，带熔断保护"""
        if self.state == "OPEN":
            if self._should_attempt_reset():
                self.state = "HALF_OPEN"
            else:
                raise Exception("熔断器开启，服务暂时不可用")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """检查是否应该尝试重置熔断器"""
        if self.last_failure_time is None:
            return True
        return time.time() - self.last_failure_time >= self.recovery_timeout
    
    def _on_success(self):
        """成功时的处理"""
        self.failure_count = 0
        self.state = "CLOSED"
    
    def _on_failure(self):
        """失败时的处理"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"


class RetryManager:
    """重试管理器"""
    
    @staticmethod
    def retry_with_backoff(
        func: Callable,
        max_attempts: int = 3,
        delay: float = 1.0,
        exponential_backoff: bool = True,
        jitter: bool = True,
        exceptions: tuple = (Exception,)
    ):
        """带退避策略的重试装饰器"""
        def decorator(original_func):
            @functools.wraps(original_func)
            def wrapper(*args, **kwargs):
                last_exception = None
                
                for attempt in range(max_attempts):
                    try:
                        return original_func(*args, **kwargs)
                    except exceptions as e:
                        last_exception = e
                        
                        if attempt == max_attempts - 1:
                            break
                        
                        # 计算延迟时间
                        current_delay = delay
                        if exponential_backoff:
                            current_delay *= (2 ** attempt)
                        
                        if jitter:
                            import random
                            current_delay *= (0.5 + random.random() * 0.5)
                        
                        time.sleep(current_delay)
                
                raise last_exception
            return wrapper
        
        if func is None:
            return decorator
        else:
            return decorator(func)


class UnifiedErrorHandler:
    """统一错误处理器"""
    
    def __init__(self, config: Optional[ErrorHandlingConfig] = None):
        self.config = config or get_error_config()
        self.error_history: List[ErrorRecord] = []
        self.error_counts: Dict[str, int] = {}
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.retry_manager = RetryManager()
        
        # 性能监控
        self.performance_metrics = {
            "total_errors": 0,
            "errors_by_category": {},
            "errors_by_level": {},
            "average_resolution_time": 0,
            "last_error_time": None
        }
    
    def handle_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        function_name: str = "",
        show_user: bool = True,
        custom_message: str = ""
    ) -> ErrorRecord:
        """处理错误的主要方法"""
        
        # 生成错误ID
        error_id = str(uuid.uuid4())[:8]
        
        # 获取错误信息
        error_type = type(error).__name__
        error_message = str(error)
        error_details = traceback.format_exc()
        
        # 分类错误
        category = get_error_category(error_type)
        level = get_error_level(error_type)
        
        # 获取调用栈信息
        tb = traceback.extract_tb(error.__traceback__)
        if tb:
            last_frame = tb[-1]
            file_name = last_frame.filename
            line_number = last_frame.lineno
        else:
            file_name = ""
            line_number = 0
        
        # 获取用户友好的消息和建议
        error_template = get_error_message(category)
        user_message = custom_message or error_template["user_message"]
        suggestions = error_template["suggestions"]
        
        # 创建错误记录
        error_record = ErrorRecord(
            id=error_id,
            timestamp=datetime.now(),
            error_type=error_type,
            error_message=error_message,
            error_details=error_details,
            category=category,
            level=level,
            function_name=function_name,
            file_name=file_name,
            line_number=line_number,
            user_message=user_message,
            suggestions=suggestions,
            context=context or {}
        )
        
        # 记录错误
        self._record_error(error_record)
        
        # 记录日志
        self._log_error(error_record)
        
        # 显示用户消息
        if show_user and self.config.show_user_friendly_messages:
            self._display_error_message(error_record)
        
        # 更新性能指标
        self._update_performance_metrics(error_record)
        
        return error_record
    
    def _record_error(self, error_record: ErrorRecord):
        """记录错误到历史记录"""
        self.error_history.append(error_record)
        
        # 限制历史记录数量
        if len(self.error_history) > self.config.max_error_history:
            self.error_history.pop(0)
        
        # 更新错误计数
        error_key = f"{error_record.category.value}:{error_record.error_type}"
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
    
    def _log_error(self, error_record: ErrorRecord):
        """记录错误日志"""
        log_level_mapping = {
            ErrorLevel.DEBUG: logging.DEBUG,
            ErrorLevel.INFO: logging.INFO,
            ErrorLevel.WARNING: logging.WARNING,
            ErrorLevel.ERROR: logging.ERROR,
            ErrorLevel.CRITICAL: logging.CRITICAL
        }
        
        log_level = log_level_mapping.get(error_record.level, logging.ERROR)
        
        logger.log(
            log_level,
            f"[{error_record.id}] {error_record.error_type}: {error_record.error_message}",
            extra={
                "error_id": error_record.id,
                "category": error_record.category.value,
                "level": error_record.level.value,
                "function": error_record.function_name,
                "context": error_record.context
            }
        )
    
    def _display_error_message(self, error_record: ErrorRecord):
        """显示用户友好的错误消息"""
        level_icons = {
            ErrorLevel.DEBUG: "🔍",
            ErrorLevel.INFO: "ℹ️",
            ErrorLevel.WARNING: "⚠️",
            ErrorLevel.ERROR: "❌",
            ErrorLevel.CRITICAL: "💥"
        }
        
        icon = level_icons.get(error_record.level, "❌")
        
        # 根据错误级别选择显示方式
        if error_record.level == ErrorLevel.CRITICAL:
            st.error(f"{icon} {error_record.user_message}")
        elif error_record.level == ErrorLevel.ERROR:
            st.error(f"{icon} {error_record.user_message}")
        elif error_record.level == ErrorLevel.WARNING:
            st.warning(f"{icon} {error_record.user_message}")
        else:
            st.info(f"{icon} {error_record.user_message}")
        
        # 显示恢复建议
        if self.config.show_recovery_suggestions and error_record.suggestions:
            with st.expander("💡 解决建议"):
                for suggestion in error_record.suggestions:
                    st.write(f"• {suggestion}")
        
        # 显示错误ID
        if self.config.show_error_id:
            st.caption(f"错误ID: {error_record.id}")
        
        # 在调试模式下显示技术详情
        if self.config.show_technical_details or st.session_state.get('debug_mode', False):
            with st.expander("🔍 技术详情"):
                st.code(error_record.error_details, language='python')
                if error_record.context:
                    st.json(error_record.context)
    
    def _update_performance_metrics(self, error_record: ErrorRecord):
        """更新性能指标"""
        self.performance_metrics["total_errors"] += 1
        self.performance_metrics["last_error_time"] = error_record.timestamp
        
        # 按分类统计
        category_key = error_record.category.value
        self.performance_metrics["errors_by_category"][category_key] = \
            self.performance_metrics["errors_by_category"].get(category_key, 0) + 1
        
        # 按级别统计
        level_key = error_record.level.value
        self.performance_metrics["errors_by_level"][level_key] = \
            self.performance_metrics["errors_by_level"].get(level_key, 0) + 1
    
    def get_circuit_breaker(self, name: str, category: ErrorCategory) -> CircuitBreaker:
        """获取或创建熔断器"""
        if name not in self.circuit_breakers:
            config = get_circuit_breaker_config(category)
            self.circuit_breakers[name] = CircuitBreaker(
                failure_threshold=config["failure_threshold"],
                recovery_timeout=config["recovery_timeout"]
            )
        return self.circuit_breakers[name]
    
    def with_retry(self, category: ErrorCategory):
        """重试装饰器"""
        strategy = get_retry_strategy(category)
        return self.retry_manager.retry_with_backoff(
            func=None,
            max_attempts=strategy["max_attempts"],
            delay=strategy["delay"],
            exponential_backoff=strategy["exponential_backoff"],
            jitter=strategy["jitter"]
        )
    
    def with_circuit_breaker(self, name: str, category: ErrorCategory):
        """熔断器装饰器"""
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                circuit_breaker = self.get_circuit_breaker(name, category)
                return circuit_breaker.call(func, *args, **kwargs)
            return wrapper
        return decorator
    
    def safe_execute(
        self,
        func: Callable,
        *args,
        context: Optional[Dict[str, Any]] = None,
        default_return: Any = None,
        show_error: bool = True,
        **kwargs
    ) -> Any:
        """安全执行函数"""
        try:
            return func(*args, **kwargs)
        except Exception as e:
            self.handle_error(
                error=e,
                context=context,
                function_name=func.__name__,
                show_user=show_error
            )
            return default_return
    
    async def safe_execute_async(
        self,
        coro: Callable,
        *args,
        context: Optional[Dict[str, Any]] = None,
        default_return: Any = None,
        show_error: bool = True,
        **kwargs
    ) -> Any:
        """安全执行异步函数"""
        try:
            return await coro(*args, **kwargs)
        except Exception as e:
            self.handle_error(
                error=e,
                context=context,
                function_name=coro.__name__,
                show_user=show_error
            )
            return default_return
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """获取错误统计信息"""
        recent_errors = []
        resolved_errors = 0
        
        for error in self.error_history[-50:]:  # 最近50个错误
            if error.resolved:
                resolved_errors += 1
            
            if len(recent_errors) < 10:
                recent_errors.append({
                    'id': error.id,
                    'timestamp': error.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'type': error.error_type,
                    'message': error.error_message[:100] + '...' if len(error.error_message) > 100 else error.error_message,
                    'category': error.category.value,
                    'level': error.level.value,
                    'resolved': error.resolved
                })
        
        return {
            'total_errors': len(self.error_history),
            'resolved_errors': resolved_errors,
            'resolution_rate': resolved_errors / len(self.error_history) if self.error_history else 0,
            'errors_by_category': self.performance_metrics["errors_by_category"],
            'errors_by_level': self.performance_metrics["errors_by_level"],
            'recent_errors': recent_errors,
            'circuit_breaker_states': {
                name: cb.state for name, cb in self.circuit_breakers.items()
            }
        }
    
    def display_error_dashboard(self):
        """显示错误仪表盘"""
        st.subheader("🚨 错误统计仪表盘")
        
        stats = self.get_error_statistics()
        
        # 基本指标
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("总错误数", stats['total_errors'])
        with col2:
            st.metric("已解决", stats['resolved_errors'])
        with col3:
            st.metric("解决率", f"{stats['resolution_rate']:.1%}")
        with col4:
            st.metric("活跃熔断器", len([cb for cb in stats['circuit_breaker_states'].values() if cb != "CLOSED"]))
        
        # 错误分类图表
        if stats['errors_by_category']:
            st.subheader("错误分类分布")
            import plotly.express as px
            import pandas as pd
            
            df = pd.DataFrame(list(stats['errors_by_category'].items()), columns=['分类', '数量'])
            fig = px.pie(df, values='数量', names='分类', title="错误分类分布")
            st.plotly_chart(fig, use_container_width=True)
        
        # 最近错误
        if stats['recent_errors']:
            st.subheader("最近错误")
            for error in stats['recent_errors']:
                status_icon = "✅" if error['resolved'] else "❌"
                level_icon = {"debug": "🔍", "info": "ℹ️", "warning": "⚠️", "error": "❌", "critical": "💥"}.get(error['level'], "❌")
                
                st.write(f"{status_icon} {level_icon} **{error['type']}** ({error['timestamp']})")
                st.write(f"   {error['message']}")
                st.write(f"   分类: {error['category']} | ID: {error['id']}")
                st.write("---")
        
        # 熔断器状态
        if stats['circuit_breaker_states']:
            st.subheader("熔断器状态")
            for name, state in stats['circuit_breaker_states'].items():
                state_color = {"CLOSED": "🟢", "OPEN": "🔴", "HALF_OPEN": "🟡"}.get(state, "⚪")
                st.write(f"{state_color} **{name}**: {state}")
    
    def clear_error_history(self):
        """清除错误历史"""
        self.error_history.clear()
        self.error_counts.clear()
        self.performance_metrics = {
            "total_errors": 0,
            "errors_by_category": {},
            "errors_by_level": {},
            "average_resolution_time": 0,
            "last_error_time": None
        }


# 全局错误处理器实例
global_error_handler = UnifiedErrorHandler()

# 便捷装饰器
def error_handler(
    category: ErrorCategory = ErrorCategory.UNKNOWN,
    show_user: bool = True,
    default_return: Any = None,
    custom_message: str = ""
):
    """错误处理装饰器"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                global_error_handler.handle_error(
                    error=e,
                    function_name=func.__name__,
                    show_user=show_user,
                    custom_message=custom_message
                )
                return default_return
        return wrapper
    return decorator

def async_error_handler(
    category: ErrorCategory = ErrorCategory.UNKNOWN,
    show_user: bool = True,
    default_return: Any = None,
    custom_message: str = ""
):
    """异步错误处理装饰器"""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                global_error_handler.handle_error(
                    error=e,
                    function_name=func.__name__,
                    show_user=show_user,
                    custom_message=custom_message
                )
                return default_return
        return wrapper
    return decorator

# 便捷函数
def safe_execute(func: Callable, *args, **kwargs) -> Any:
    """安全执行函数"""
    return global_error_handler.safe_execute(func, *args, **kwargs)

async def safe_execute_async(coro: Callable, *args, **kwargs) -> Any:
    """安全执行异步函数"""
    return await global_error_handler.safe_execute_async(coro, *args, **kwargs)

def display_error_dashboard():
    """显示错误仪表盘"""
    global_error_handler.display_error_dashboard()

def get_error_statistics() -> Dict[str, Any]:
    """获取错误统计"""
    return global_error_handler.get_error_statistics()