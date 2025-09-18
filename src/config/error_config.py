"""
统一错误处理配置
整合所有错误处理相关的配置和策略
"""

from enum import Enum
from typing import Dict, List, Any
from dataclasses import dataclass


class ErrorLevel(Enum):
    """错误级别"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """错误分类"""
    NETWORK = "network"
    API = "api"
    DATABASE = "database"
    VALIDATION = "validation"
    AUTHENTICATION = "authentication"
    PERMISSION = "permission"
    BUSINESS_LOGIC = "business_logic"
    SYSTEM = "system"
    UI = "ui"
    UNKNOWN = "unknown"


@dataclass
class ErrorHandlingConfig:
    """错误处理配置"""
    # 显示设置
    show_user_friendly_messages: bool = True
    show_technical_details: bool = False
    show_recovery_suggestions: bool = True
    show_error_id: bool = True
    
    # 日志设置
    log_to_file: bool = True
    log_to_console: bool = True
    max_log_file_size: int = 10 * 1024 * 1024  # 10MB
    max_log_files: int = 5
    
    # 错误统计设置
    enable_error_tracking: bool = True
    max_error_history: int = 1000
    error_report_interval: int = 3600  # 1小时
    
    # 重试设置
    enable_auto_retry: bool = True
    max_retry_attempts: int = 3
    retry_delay: float = 1.0
    exponential_backoff: bool = True
    
    # 熔断器设置
    enable_circuit_breaker: bool = True
    failure_threshold: int = 5
    recovery_timeout: int = 60
    
    # 用户通知设置
    enable_toast_notifications: bool = True
    enable_sidebar_notifications: bool = True
    notification_timeout: int = 5


# 默认配置
DEFAULT_ERROR_CONFIG = ErrorHandlingConfig()

# 错误消息模板
ERROR_MESSAGES = {
    ErrorCategory.NETWORK: {
        "user_message": "🌐 网络连接问题，请检查网络连接后重试",
        "suggestions": [
            "检查网络连接是否正常",
            "尝试刷新页面",
            "稍后重试",
            "检查防火墙设置"
        ]
    },
    ErrorCategory.API: {
        "user_message": "🔑 API服务问题，请检查API配置",
        "suggestions": [
            "检查API密钥是否正确",
            "验证API权限设置",
            "检查API服务状态",
            "查看API使用限制"
        ]
    },
    ErrorCategory.DATABASE: {
        "user_message": "💾 数据库连接问题，请稍后重试",
        "suggestions": [
            "检查数据库连接",
            "验证数据库权限",
            "检查数据库服务状态",
            "清理数据库缓存"
        ]
    },
    ErrorCategory.VALIDATION: {
        "user_message": "📝 数据验证失败，请检查输入数据",
        "suggestions": [
            "检查输入数据格式",
            "验证必填字段",
            "确认数据类型正确",
            "查看数据范围限制"
        ]
    },
    ErrorCategory.AUTHENTICATION: {
        "user_message": "🔐 身份验证失败，请重新登录",
        "suggestions": [
            "检查用户名和密码",
            "重新登录系统",
            "清除浏览器缓存",
            "联系管理员"
        ]
    },
    ErrorCategory.PERMISSION: {
        "user_message": "🚫 权限不足，无法执行此操作",
        "suggestions": [
            "检查用户权限",
            "联系管理员获取权限",
            "确认操作范围",
            "查看权限文档"
        ]
    },
    ErrorCategory.BUSINESS_LOGIC: {
        "user_message": "⚠️ 业务逻辑错误，请检查操作流程",
        "suggestions": [
            "检查操作步骤",
            "验证业务规则",
            "确认数据状态",
            "查看操作手册"
        ]
    },
    ErrorCategory.SYSTEM: {
        "user_message": "🔧 系统错误，请联系技术支持",
        "suggestions": [
            "重启应用程序",
            "检查系统资源",
            "查看系统日志",
            "联系技术支持"
        ]
    },
    ErrorCategory.UI: {
        "user_message": "🖥️ 界面显示问题，请刷新页面",
        "suggestions": [
            "刷新浏览器页面",
            "清除浏览器缓存",
            "尝试其他浏览器",
            "检查浏览器兼容性"
        ]
    },
    ErrorCategory.UNKNOWN: {
        "user_message": "❓ 未知错误，请稍后重试",
        "suggestions": [
            "刷新页面重试",
            "检查网络连接",
            "清除缓存",
            "联系技术支持"
        ]
    }
}

# 错误级别映射
ERROR_LEVEL_MAPPING = {
    # 网络错误
    "ConnectionError": ErrorLevel.ERROR,
    "TimeoutError": ErrorLevel.WARNING,
    "HTTPError": ErrorLevel.ERROR,
    
    # API错误
    "APIError": ErrorLevel.ERROR,
    "AuthenticationError": ErrorLevel.ERROR,
    "RateLimitError": ErrorLevel.WARNING,
    
    # 数据错误
    "ValidationError": ErrorLevel.WARNING,
    "ValueError": ErrorLevel.WARNING,
    "TypeError": ErrorLevel.ERROR,
    "KeyError": ErrorLevel.WARNING,
    
    # 系统错误
    "MemoryError": ErrorLevel.CRITICAL,
    "SystemError": ErrorLevel.CRITICAL,
    "OSError": ErrorLevel.ERROR,
    
    # 默认错误
    "Exception": ErrorLevel.ERROR
}

# 错误分类映射
ERROR_CATEGORY_MAPPING = {
    # 网络相关
    "ConnectionError": ErrorCategory.NETWORK,
    "TimeoutError": ErrorCategory.NETWORK,
    "HTTPError": ErrorCategory.NETWORK,
    "URLError": ErrorCategory.NETWORK,
    
    # API相关
    "APIError": ErrorCategory.API,
    "AuthenticationError": ErrorCategory.AUTHENTICATION,
    "PermissionError": ErrorCategory.PERMISSION,
    "RateLimitError": ErrorCategory.API,
    
    # 数据相关
    "ValidationError": ErrorCategory.VALIDATION,
    "ValueError": ErrorCategory.VALIDATION,
    "TypeError": ErrorCategory.VALIDATION,
    "KeyError": ErrorCategory.VALIDATION,
    "AttributeError": ErrorCategory.VALIDATION,
    
    # 数据库相关
    "DatabaseError": ErrorCategory.DATABASE,
    "IntegrityError": ErrorCategory.DATABASE,
    "OperationalError": ErrorCategory.DATABASE,
    
    # 系统相关
    "MemoryError": ErrorCategory.SYSTEM,
    "SystemError": ErrorCategory.SYSTEM,
    "OSError": ErrorCategory.SYSTEM,
    "FileNotFoundError": ErrorCategory.SYSTEM,
    
    # UI相关
    "StreamlitAPIException": ErrorCategory.UI,
    "DuplicateWidgetID": ErrorCategory.UI,
    
    # 默认分类
    "Exception": ErrorCategory.UNKNOWN
}

# 重试策略配置
RETRY_STRATEGIES = {
    ErrorCategory.NETWORK: {
        "max_attempts": 3,
        "delay": 1.0,
        "exponential_backoff": True,
        "jitter": True
    },
    ErrorCategory.API: {
        "max_attempts": 2,
        "delay": 2.0,
        "exponential_backoff": True,
        "jitter": False
    },
    ErrorCategory.DATABASE: {
        "max_attempts": 3,
        "delay": 0.5,
        "exponential_backoff": False,
        "jitter": True
    },
    ErrorCategory.VALIDATION: {
        "max_attempts": 1,
        "delay": 0,
        "exponential_backoff": False,
        "jitter": False
    }
}

# 熔断器配置
CIRCUIT_BREAKER_CONFIG = {
    ErrorCategory.NETWORK: {
        "failure_threshold": 5,
        "recovery_timeout": 60,
        "expected_exception": ["ConnectionError", "TimeoutError"]
    },
    ErrorCategory.API: {
        "failure_threshold": 3,
        "recovery_timeout": 120,
        "expected_exception": ["HTTPError", "RateLimitError"]
    },
    ErrorCategory.DATABASE: {
        "failure_threshold": 3,
        "recovery_timeout": 30,
        "expected_exception": ["DatabaseError", "OperationalError"]
    }
}

# 监控和报警配置
MONITORING_CONFIG = {
    "error_rate_threshold": 0.1,  # 10%错误率阈值
    "response_time_threshold": 5.0,  # 5秒响应时间阈值
    "memory_usage_threshold": 0.8,  # 80%内存使用率阈值
    "disk_usage_threshold": 0.9,  # 90%磁盘使用率阈值
    "alert_cooldown": 300,  # 5分钟报警冷却时间
}

def get_error_config() -> ErrorHandlingConfig:
    """获取错误处理配置"""
    return DEFAULT_ERROR_CONFIG

def get_error_message(category: ErrorCategory) -> Dict[str, Any]:
    """获取错误消息模板"""
    return ERROR_MESSAGES.get(category, ERROR_MESSAGES[ErrorCategory.UNKNOWN])

def get_error_level(exception_type: str) -> ErrorLevel:
    """根据异常类型获取错误级别"""
    return ERROR_LEVEL_MAPPING.get(exception_type, ErrorLevel.ERROR)

def get_error_category(exception_type: str) -> ErrorCategory:
    """根据异常类型获取错误分类"""
    return ERROR_CATEGORY_MAPPING.get(exception_type, ErrorCategory.UNKNOWN)

def get_retry_strategy(category: ErrorCategory) -> Dict[str, Any]:
    """获取重试策略"""
    return RETRY_STRATEGIES.get(category, RETRY_STRATEGIES[ErrorCategory.NETWORK])

def get_circuit_breaker_config(category: ErrorCategory) -> Dict[str, Any]:
    """获取熔断器配置"""
    return CIRCUIT_BREAKER_CONFIG.get(category, CIRCUIT_BREAKER_CONFIG[ErrorCategory.NETWORK])