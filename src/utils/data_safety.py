"""
数据安全处理工具模块
提供安全的数据处理函数，防止NoneType错误
"""

import logging
from typing import Any, Union, Optional, Dict, List
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

def safe_format(template: str, *args, **kwargs) -> str:
    """
    安全的字符串格式化，防止NoneType错误
    
    Args:
        template: 格式化模板
        *args: 位置参数
        **kwargs: 关键字参数
    
    Returns:
        格式化后的字符串，如果出错返回默认值
    """
    try:
        # 检查并替换None值
        safe_args = []
        for arg in args:
            if arg is None:
                safe_args.append("N/A")
            else:
                safe_args.append(arg)
        
        safe_kwargs = {}
        for key, value in kwargs.items():
            if value is None:
                safe_kwargs[key] = "N/A"
            else:
                safe_kwargs[key] = value
        
        return template.format(*safe_args, **safe_kwargs)
    except Exception as e:
        logger.warning(f"字符串格式化失败: {e}")
        return template

def safe_abs(value: Any, default: float = 0.0) -> float:
    """
    安全的绝对值计算，防止NoneType错误
    
    Args:
        value: 要计算绝对值的数值
        default: 默认值
    
    Returns:
        绝对值或默认值
    """
    try:
        if value is None:
            return default
        if isinstance(value, (int, float)):
            return abs(value)
        if isinstance(value, str):
            try:
                return abs(float(value))
            except ValueError:
                return default
        return default
    except Exception as e:
        logger.warning(f"绝对值计算失败: {e}")
        return default

def safe_float(value: Any, default: float = 0.0) -> float:
    """
    安全的浮点数转换
    
    Args:
        value: 要转换的值
        default: 默认值
    
    Returns:
        转换后的浮点数或默认值
    """
    try:
        if value is None:
            return default
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                return default
        return default
    except Exception as e:
        logger.warning(f"浮点数转换失败: {e}")
        return default

def safe_int(value: Any, default: int = 0) -> int:
    """
    安全的整数转换
    
    Args:
        value: 要转换的值
        default: 默认值
    
    Returns:
        转换后的整数或默认值
    """
    try:
        if value is None:
            return default
        if isinstance(value, (int, float)):
            return int(value)
        if isinstance(value, str):
            try:
                return int(float(value))
            except ValueError:
                return default
        return default
    except Exception as e:
        logger.warning(f"整数转换失败: {e}")
        return default

def safe_get(data: Dict, key: str, default: Any = None) -> Any:
    """
    安全的字典取值
    
    Args:
        data: 字典数据
        key: 键名
        default: 默认值
    
    Returns:
        字典值或默认值
    """
    try:
        if not isinstance(data, dict):
            return default
        return data.get(key, default)
    except Exception as e:
        logger.warning(f"字典取值失败: {e}")
        return default

def safe_percentage(value: Any, default: str = "0.00%") -> str:
    """
    安全的百分比格式化
    
    Args:
        value: 数值
        default: 默认值
    
    Returns:
        格式化的百分比字符串
    """
    try:
        if value is None:
            return default
        num_value = safe_float(value, 0.0)
        return f"{num_value:.2f}%"
    except Exception as e:
        logger.warning(f"百分比格式化失败: {e}")
        return default

def safe_currency(value: Any, currency: str = "$", default: str = "$0.00") -> str:
    """
    安全的货币格式化
    
    Args:
        value: 数值
        currency: 货币符号
        default: 默认值
    
    Returns:
        格式化的货币字符串
    """
    try:
        if value is None:
            return default
        num_value = safe_float(value, 0.0)
        return f"{currency}{num_value:,.2f}"
    except Exception as e:
        logger.warning(f"货币格式化失败: {e}")
        return default

def validate_api_response(data: Any, required_fields: List[str] = None) -> bool:
    """
    验证API响应数据
    
    Args:
        data: API响应数据
        required_fields: 必需字段列表
    
    Returns:
        验证是否通过
    """
    try:
        if data is None:
            logger.warning("API响应数据为None")
            return False
        
        if not isinstance(data, (dict, list)):
            logger.warning(f"API响应数据类型错误: {type(data)}")
            return False
        
        if isinstance(data, list) and len(data) == 0:
            logger.warning("API响应数据为空列表")
            return False
        
        if isinstance(data, dict) and len(data) == 0:
            logger.warning("API响应数据为空字典")
            return False
        
        # 检查必需字段
        if required_fields and isinstance(data, dict):
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                logger.warning(f"API响应缺少必需字段: {missing_fields}")
                return False
        
        return True
    except Exception as e:
        logger.error(f"API响应验证失败: {e}")
        return False

def clean_numeric_data(df: pd.DataFrame, numeric_columns: List[str] = None) -> pd.DataFrame:
    """
    清理数据框中的数值数据，处理None和异常值
    
    Args:
        df: 数据框
        numeric_columns: 数值列名列表
    
    Returns:
        清理后的数据框
    """
    try:
        if df is None or df.empty:
            return pd.DataFrame()
        
        df_clean = df.copy()
        
        if numeric_columns is None:
            numeric_columns = df_clean.select_dtypes(include=[np.number]).columns.tolist()
        
        for col in numeric_columns:
            if col in df_clean.columns:
                # 替换None和NaN为0
                df_clean[col] = df_clean[col].fillna(0)
                # 替换无穷大值
                df_clean[col] = df_clean[col].replace([np.inf, -np.inf], 0)
                # 确保数据类型为数值
                df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce').fillna(0)
        
        return df_clean
    except Exception as e:
        logger.error(f"数据清理失败: {e}")
        return df if df is not None else pd.DataFrame()

def safe_calculate_change(current: Any, previous: Any, default: float = 0.0) -> float:
    """
    安全计算变化率
    
    Args:
        current: 当前值
        previous: 之前值
        default: 默认值
    
    Returns:
        变化率
    """
    try:
        current_val = safe_float(current, 0.0)
        previous_val = safe_float(previous, 0.0)
        
        if previous_val == 0:
            return default
        
        return ((current_val - previous_val) / previous_val) * 100
    except Exception as e:
        logger.warning(f"变化率计算失败: {e}")
        return default

def safe_metric_display(label: str, value: Any, delta: Any = None, format_type: str = "number") -> Dict[str, str]:
    """
    安全的指标显示格式化
    
    Args:
        label: 标签
        value: 值
        delta: 变化值
        format_type: 格式类型 (number, currency, percentage)
    
    Returns:
        格式化后的指标数据
    """
    try:
        if format_type == "currency":
            formatted_value = safe_currency(value)
            formatted_delta = safe_currency(delta) if delta is not None else None
        elif format_type == "percentage":
            formatted_value = safe_percentage(value)
            formatted_delta = safe_percentage(delta) if delta is not None else None
        else:
            formatted_value = str(safe_float(value, 0.0))
            formatted_delta = str(safe_float(delta, 0.0)) if delta is not None else None
        
        return {
            "label": label,
            "value": formatted_value,
            "delta": formatted_delta
        }
    except Exception as e:
        logger.error(f"指标显示格式化失败: {e}")
        return {
            "label": label,
            "value": "N/A",
            "delta": None
        }