"""
统一异常处理系统
提供全局异常处理、错误分类、错误恢复和用户友好的错误显示功能
"""

import traceback
import functools
import asyncio
from typing import Dict, Any, Optional, Callable, Type, Union, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import streamlit as st
from src.utils.logging_utils import logger


class ErrorSeverity(Enum):
    """错误严重程度"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """错误分类"""
    NETWORK = "network"
    DATABASE = "database"
    API = "api"
    VALIDATION = "validation"
    AUTHENTICATION = "authentication"
    PERMISSION = "permission"
    BUSINESS_LOGIC = "business_logic"
    SYSTEM = "system"
    UNKNOWN = "unknown"


@dataclass
class ErrorInfo:
    """错误信息数据类"""
    error_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    error_type: str = ""
    error_message: str = ""
    error_details: str = ""
    category: ErrorCategory = ErrorCategory.UNKNOWN
    severity: ErrorSeverity = ErrorSeverity.MEDIUM
    function_name: str = ""
    file_name: str = ""
    line_number: int = 0
    user_message: str = ""
    recovery_suggestions: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)


class TradingIntelligenceException(Exception):
    """交易智能平台基础异常类"""
    
    def __init__(
        self,
        message: str,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        user_message: str = "",
        recovery_suggestions: List[str] = None,
        context: Dict[str, Any] = None
    ):
        super().__init__(message)
        self.message = message
        self.category = category
        self.severity = severity
        self.user_message = user_message or self._get_default_user_message()
        self.recovery_suggestions = recovery_suggestions or []
        self.context = context or {}
    
    def _get_default_user_message(self) -> str:
        """获取默认用户友好消息"""
        category_messages = {
            ErrorCategory.NETWORK: "网络连接出现问题，请检查网络连接后重试",
            ErrorCategory.DATABASE: "数据库操作失败，请稍后重试",
            ErrorCategory.API: "API调用失败，请稍后重试",
            ErrorCategory.VALIDATION: "输入数据验证失败，请检查输入内容",
            ErrorCategory.AUTHENTICATION: "身份验证失败，请重新登录",
            ErrorCategory.PERMISSION: "权限不足，请联系管理员",
            ErrorCategory.BUSINESS_LOGIC: "业务逻辑错误，请检查操作流程",
            ErrorCategory.SYSTEM: "系统错误，请联系技术支持",
            ErrorCategory.UNKNOWN: "发生未知错误，请稍后重试"
        }
        return category_messages.get(self.category, "发生错误，请稍后重试")


class NetworkException(TradingIntelligenceException):
    """网络相关异常"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.MEDIUM,
            **kwargs
        )


class DatabaseException(TradingIntelligenceException):
    """数据库相关异常"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.DATABASE,
            severity=ErrorSeverity.HIGH,
            **kwargs
        )


class APIException(TradingIntelligenceException):
    """API相关异常"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.API,
            severity=ErrorSeverity.MEDIUM,
            **kwargs
        )


class ValidationException(TradingIntelligenceException):
    """数据验证异常"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.LOW,
            **kwargs
        )


class BusinessLogicException(TradingIntelligenceException):
    """业务逻辑异常"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.BUSINESS_LOGIC,
            severity=ErrorSeverity.MEDIUM,
            **kwargs
        )


class ExceptionHandler:
    """异常处理器"""
    
    def __init__(self):
        self.error_history: List[ErrorInfo] = []
        self.max_history = 1000
        self.error_counts: Dict[str, int] = {}
    
    def handle_exception(
        self,
        exception: Exception,
        function_name: str = "",
        context: Dict[str, Any] = None
    ) -> ErrorInfo:
        """处理异常并返回错误信息"""
        import uuid
        
        error_id = str(uuid.uuid4())[:8]
        
        # 获取异常信息
        tb = traceback.extract_tb(exception.__traceback__)
        if tb:
            last_frame = tb[-1]
            file_name = last_frame.filename
            line_number = last_frame.lineno
        else:
            file_name = ""
            line_number = 0
        
        # 创建错误信息
        if isinstance(exception, TradingIntelligenceException):
            error_info = ErrorInfo(
                error_id=error_id,
                error_type=type(exception).__name__,
                error_message=str(exception),
                error_details=traceback.format_exc(),
                category=exception.category,
                severity=exception.severity,
                function_name=function_name,
                file_name=file_name,
                line_number=line_number,
                user_message=exception.user_message,
                recovery_suggestions=exception.recovery_suggestions,
                context=context or exception.context
            )
        else:
            # 处理标准异常
            category, severity = self._classify_exception(exception)
            error_info = ErrorInfo(
                error_id=error_id,
                error_type=type(exception).__name__,
                error_message=str(exception),
                error_details=traceback.format_exc(),
                category=category,
                severity=severity,
                function_name=function_name,
                file_name=file_name,
                line_number=line_number,
                user_message=self._get_user_friendly_message(exception, category),
                recovery_suggestions=self._get_recovery_suggestions(exception, category),
                context=context or {}
            )
        
        # 记录错误
        self._record_error(error_info)
        
        # 记录日志
        log_level = self._get_log_level(error_info.severity)
        logger.log(
            log_level,
            f"[{error_id}] {error_info.error_type}: {error_info.error_message}",
            extra={
                "error_id": error_id,
                "category": error_info.category.value,
                "severity": error_info.severity.value,
                "function": function_name,
                "context": context
            }
        )
        
        return error_info
    
    def _classify_exception(self, exception: Exception) -> tuple[ErrorCategory, ErrorSeverity]:
        """分类标准异常"""
        exception_type = type(exception).__name__
        
        # 网络相关异常
        if any(keyword in exception_type.lower() for keyword in 
               ['connection', 'timeout', 'network', 'http', 'url']):
            return ErrorCategory.NETWORK, ErrorSeverity.MEDIUM
        
        # 数据库相关异常
        if any(keyword in exception_type.lower() for keyword in 
               ['database', 'sql', 'connection', 'integrity']):
            return ErrorCategory.DATABASE, ErrorSeverity.HIGH
        
        # 验证相关异常
        if any(keyword in exception_type.lower() for keyword in 
               ['value', 'type', 'attribute', 'key', 'index']):
            return ErrorCategory.VALIDATION, ErrorSeverity.LOW
        
        # 权限相关异常
        if any(keyword in exception_type.lower() for keyword in 
               ['permission', 'access', 'forbidden', 'unauthorized']):
            return ErrorCategory.PERMISSION, ErrorSeverity.MEDIUM
        
        return ErrorCategory.UNKNOWN, ErrorSeverity.MEDIUM
    
    def _get_user_friendly_message(self, exception: Exception, category: ErrorCategory) -> str:
        """获取用户友好的错误消息"""
        category_messages = {
            ErrorCategory.NETWORK: "网络连接出现问题，请检查网络连接后重试",
            ErrorCategory.DATABASE: "数据库操作失败，请稍后重试",
            ErrorCategory.API: "API调用失败，请稍后重试",
            ErrorCategory.VALIDATION: "输入数据有误，请检查后重新输入",
            ErrorCategory.PERMISSION: "权限不足，请联系管理员",
            ErrorCategory.UNKNOWN: "系统出现异常，请稍后重试"
        }
        return category_messages.get(category, "发生未知错误，请稍后重试")
    
    def _get_recovery_suggestions(self, exception: Exception, category: ErrorCategory) -> List[str]:
        """获取恢复建议"""
        suggestions = {
            ErrorCategory.NETWORK: [
                "检查网络连接是否正常",
                "稍后重试操作",
                "联系网络管理员"
            ],
            ErrorCategory.DATABASE: [
                "稍后重试操作",
                "检查数据库连接",
                "联系技术支持"
            ],
            ErrorCategory.API: [
                "检查API服务状态",
                "稍后重试操作",
                "联系API提供商"
            ],
            ErrorCategory.VALIDATION: [
                "检查输入数据格式",
                "确认必填字段已填写",
                "参考输入示例"
            ],
            ErrorCategory.PERMISSION: [
                "联系管理员获取权限",
                "确认账户状态正常",
                "重新登录系统"
            ]
        }
        return suggestions.get(category, ["稍后重试操作", "联系技术支持"])
    
    def _get_log_level(self, severity: ErrorSeverity) -> int:
        """获取日志级别"""
        import logging
        
        level_mapping = {
            ErrorSeverity.LOW: logging.WARNING,
            ErrorSeverity.MEDIUM: logging.ERROR,
            ErrorSeverity.HIGH: logging.ERROR,
            ErrorSeverity.CRITICAL: logging.CRITICAL
        }
        return level_mapping.get(severity, logging.ERROR)
    
    def _record_error(self, error_info: ErrorInfo):
        """记录错误信息"""
        self.error_history.append(error_info)
        
        # 限制历史记录数量
        if len(self.error_history) > self.max_history:
            self.error_history.pop(0)
        
        # 更新错误计数
        error_key = f"{error_info.category.value}:{error_info.error_type}"
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """获取错误统计信息"""
        if not self.error_history:
            return {}
        
        # 按类别统计
        category_counts = {}
        severity_counts = {}
        recent_errors = []
        
        for error in self.error_history[-100:]:  # 最近100个错误
            # 按类别统计
            category = error.category.value
            category_counts[category] = category_counts.get(category, 0) + 1
            
            # 按严重程度统计
            severity = error.severity.value
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            # 最近错误
            if len(recent_errors) < 10:
                recent_errors.append({
                    'id': error.error_id,
                    'timestamp': error.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'type': error.error_type,
                    'message': error.error_message[:100] + '...' if len(error.error_message) > 100 else error.error_message,
                    'category': error.category.value,
                    'severity': error.severity.value
                })
        
        return {
            'total_errors': len(self.error_history),
            'category_counts': category_counts,
            'severity_counts': severity_counts,
            'recent_errors': recent_errors,
            'error_counts': dict(list(self.error_counts.items())[-20:])  # 最近20种错误类型
        }


# 全局异常处理器实例
global_exception_handler = ExceptionHandler()


def exception_handler(
    show_user_message: bool = True,
    reraise: bool = False,
    default_return: Any = None
):
    """异常处理装饰器"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            try:
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)
            except Exception as e:
                error_info = global_exception_handler.handle_exception(
                    e, func.__name__, {"args": str(args)[:200], "kwargs": str(kwargs)[:200]}
                )
                
                if show_user_message:
                    display_error_message(error_info)
                
                if reraise:
                    raise
                
                return default_return
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_info = global_exception_handler.handle_exception(
                    e, func.__name__, {"args": str(args)[:200], "kwargs": str(kwargs)[:200]}
                )
                
                if show_user_message:
                    display_error_message(error_info)
                
                if reraise:
                    raise
                
                return default_return
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator


def display_error_message(error_info: ErrorInfo):
    """显示用户友好的错误消息"""
    severity_icons = {
        ErrorSeverity.LOW: "⚠️",
        ErrorSeverity.MEDIUM: "❌",
        ErrorSeverity.HIGH: "🚨",
        ErrorSeverity.CRITICAL: "💥"
    }
    
    icon = severity_icons.get(error_info.severity, "❌")
    
    # 显示主要错误消息
    if error_info.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
        st.error(f"{icon} {error_info.user_message}")
    elif error_info.severity == ErrorSeverity.MEDIUM:
        st.warning(f"{icon} {error_info.user_message}")
    else:
        st.info(f"{icon} {error_info.user_message}")
    
    # 显示恢复建议
    if error_info.recovery_suggestions:
        with st.expander("💡 解决建议"):
            for suggestion in error_info.recovery_suggestions:
                st.write(f"• {suggestion}")
    
    # 在调试模式下显示详细信息
    if st.session_state.get('debug_mode', False):
        with st.expander(f"🔍 详细信息 (错误ID: {error_info.error_id})"):
            st.code(error_info.error_details, language='python')


def display_error_dashboard():
    """显示错误统计仪表板"""
    st.subheader("🚨 错误统计仪表板")
    
    stats = global_exception_handler.get_error_statistics()
    
    if not stats:
        st.info("暂无错误记录")
        return
    
    # 总体统计
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("总错误数", stats['total_errors'])
    
    with col2:
        if stats['category_counts']:
            most_common_category = max(stats['category_counts'], key=stats['category_counts'].get)
            st.metric("最常见类别", most_common_category)
    
    with col3:
        if stats['severity_counts']:
            high_severity_count = stats['severity_counts'].get('high', 0) + stats['severity_counts'].get('critical', 0)
            st.metric("高严重度错误", high_severity_count)
    
    with col4:
        recent_count = len(stats['recent_errors'])
        st.metric("最近错误", recent_count)
    
    # 错误分类图表
    if stats['category_counts']:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("错误类别分布")
            import plotly.express as px
            import pandas as pd
            
            df = pd.DataFrame(list(stats['category_counts'].items()), columns=['类别', '数量'])
            fig = px.pie(df, values='数量', names='类别', title='错误类别分布')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("严重程度分布")
            df = pd.DataFrame(list(stats['severity_counts'].items()), columns=['严重程度', '数量'])
            fig = px.bar(df, x='严重程度', y='数量', title='错误严重程度分布')
            st.plotly_chart(fig, use_container_width=True)
    
    # 最近错误列表
    if stats['recent_errors']:
        st.subheader("最近错误记录")
        import pandas as pd
        
        df = pd.DataFrame(stats['recent_errors'])
        st.dataframe(df, use_container_width=True)