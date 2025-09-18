"""
Enhanced error handling utilities for better debugging and user experience.
"""
import logging
import traceback
import functools
from typing import Any, Callable, Optional, Type, Union
import streamlit as st

# Configure logger
logger = logging.getLogger(__name__)

class AppError(Exception):
    """Base exception class for application-specific errors."""
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "UNKNOWN_ERROR"
        self.details = details or {}

class DataFetchError(AppError):
    """Raised when data fetching operations fail."""
    pass

class ConfigurationError(AppError):
    """Raised when configuration is invalid or missing."""
    pass

class NetworkError(AppError):
    """Raised when network operations fail."""
    pass

class ValidationError(AppError):
    """Raised when data validation fails."""
    pass

def handle_error(
    error: Exception,
    user_message: str = "操作失败",
    log_level: int = logging.ERROR,
    show_details: bool = False
) -> None:
    """
    Enhanced error handler that logs detailed information and shows user-friendly messages.

    Args:
        error: The exception that occurred
        user_message: User-friendly message to display
        log_level: Logging level for the error
        show_details: Whether to show technical details to user
    """
    # Log detailed error information
    error_details = {
        'error_type': type(error).__name__,
        'error_message': str(error),
        'traceback': traceback.format_exc()
    }

    logger.log(log_level, f"Error occurred: {user_message}", extra=error_details)

    # Show user-friendly message
    if isinstance(error, AppError):
        st.error(f"❌ {error.message}")
        if show_details and error.details:
            with st.expander("技术详情"):
                st.json(error.details)
    else:
        st.error(f"❌ {user_message}")
        if show_details:
            with st.expander("错误详情"):
                st.code(str(error))

def safe_execute(
    func: Callable,
    fallback_value: Any = None,
    error_message: str = "操作执行失败",
    show_error: bool = True
) -> Any:
    """
    Safely execute a function with proper error handling.

    Args:
        func: Function to execute
        fallback_value: Value to return if function fails
        error_message: Message to show on error
        show_error: Whether to display error to user

    Returns:
        Function result or fallback value
    """
    try:
        return func()
    except (ConnectionError, TimeoutError) as e:
        if show_error:
            handle_error(NetworkError(f"网络连接失败: {str(e)}"), error_message)
        return fallback_value
    except (KeyError, ValueError, TypeError) as e:
        if show_error:
            handle_error(ValidationError(f"数据验证失败: {str(e)}"), error_message)
        return fallback_value
    except FileNotFoundError as e:
        if show_error:
            handle_error(ConfigurationError(f"文件未找到: {str(e)}"), error_message)
        return fallback_value
    except ImportError as e:
        if show_error:
            handle_error(ConfigurationError(f"模块导入失败: {str(e)}"), error_message)
        return fallback_value
    except Exception as e:
        if show_error:
            handle_error(e, error_message, show_details=True)
        return fallback_value

def error_boundary(
    fallback_value: Any = None,
    error_message: str = "组件加载失败",
    show_error: bool = True
):
    """
    Decorator for creating error boundaries around functions.

    Args:
        fallback_value: Value to return on error
        error_message: Message to show on error
        show_error: Whether to display error to user
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return safe_execute(
                lambda: func(*args, **kwargs),
                fallback_value=fallback_value,
                error_message=error_message,
                show_error=show_error
            )
        return wrapper
    return decorator

def validate_required_config(config: dict, required_keys: list) -> None:
    """
    Validate that required configuration keys are present.

    Args:
        config: Configuration dictionary
        required_keys: List of required keys

    Raises:
        ConfigurationError: If required keys are missing
    """
    missing_keys = [key for key in required_keys if key not in config]
    if missing_keys:
        raise ConfigurationError(
            f"缺少必需的配置项: {', '.join(missing_keys)}",
            error_code="MISSING_CONFIG",
            details={"missing_keys": missing_keys}
        )

def retry_on_failure(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    Decorator to retry function execution on failure.

    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries (seconds)
        backoff_factor: Factor to multiply delay by after each retry
        exceptions: Tuple of exceptions to catch and retry on
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(f"Attempt {attempt + 1} failed, retrying in {current_delay}s: {str(e)}")
                        import time
                        time.sleep(current_delay)
                        current_delay *= backoff_factor
                    else:
                        logger.error(f"All {max_retries + 1} attempts failed")

            raise last_exception
        return wrapper
    return decorator

# Convenience functions for common error scenarios
def handle_api_error(error: Exception, api_name: str = "API") -> None:
    """Handle API-related errors with appropriate user messages."""
    if "timeout" in str(error).lower():
        handle_error(NetworkError(f"{api_name} 请求超时"), f"{api_name} 连接超时，请稍后重试")
    elif "connection" in str(error).lower():
        handle_error(NetworkError(f"{api_name} 连接失败"), f"无法连接到 {api_name}，请检查网络连接")
    elif "unauthorized" in str(error).lower() or "401" in str(error):
        handle_error(ConfigurationError(f"{api_name} 认证失败"), f"{api_name} 认证失败，请检查API密钥")
    elif "rate limit" in str(error).lower() or "429" in str(error):
        handle_error(NetworkError(f"{api_name} 请求频率限制"), f"{api_name} 请求过于频繁，请稍后重试")
    else:
        handle_error(error, f"{api_name} 请求失败")

def handle_data_error(error: Exception, operation: str = "数据处理") -> None:
    """Handle data-related errors with appropriate user messages."""
    if isinstance(error, (KeyError, AttributeError)):
        handle_error(ValidationError(f"数据格式错误: {str(error)}"), f"{operation} 失败：数据格式不正确")
    elif isinstance(error, (ValueError, TypeError)):
        handle_error(ValidationError(f"数据类型错误: {str(error)}"), f"{operation} 失败：数据类型不匹配")
    else:
        handle_error(error, f"{operation} 失败")
