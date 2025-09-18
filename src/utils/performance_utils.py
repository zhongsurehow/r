"""
性能优化工具
提供常用的性能优化函数和装饰器
"""

import time
import functools
import logging
import pandas as pd
import numpy as np
from typing import Callable, Any, Dict, List
import streamlit as st

logger = logging.getLogger(__name__)

def performance_timer(func: Callable) -> Callable:
    """
    性能计时装饰器
    记录函数执行时间
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time

        if execution_time > 1.0:  # 只记录超过1秒的操作
            logger.warning(f"函数 {func.__name__} 执行时间: {execution_time:.2f}秒")

        return result
    return wrapper

def optimize_dataframe_display(df: pd.DataFrame, format_rules: Dict[str, str] = None) -> pd.DataFrame:
    """
    优化DataFrame显示格式化
    使用向量化操作替代apply()

    Args:
        df: 要格式化的DataFrame
        format_rules: 格式化规则字典，例如 {'price': '${:.2f}', 'percentage': '{:.1f}%'}

    Returns:
        格式化后的DataFrame
    """
    if df.empty or format_rules is None:
        return df

    df_formatted = df.copy()

    for column, format_str in format_rules.items():
        if column not in df_formatted.columns:
            continue

        try:
            if '{:.2f}' in format_str or '{:.1f}' in format_str or '{:.0f}' in format_str:
                # 数值格式化
                if '$' in format_str:
                    precision = int(format_str.split(':.')[1].split('f')[0])
                    df_formatted[column] = "$" + df_formatted[column].round(precision).astype(str)
                elif '%' in format_str:
                    precision = int(format_str.split(':.')[1].split('f')[0])
                    df_formatted[column] = df_formatted[column].round(precision).astype(str) + "%"
                else:
                    precision = int(format_str.split(':.')[1].split('f')[0])
                    df_formatted[column] = df_formatted[column].round(precision).astype(str)
            elif '{:,}' in format_str:
                # 千分位分隔符
                df_formatted[column] = df_formatted[column].round(0).astype(int).apply(lambda x: f"{x:,}")
        except Exception as e:
            logger.warning(f"格式化列 {column} 失败: {str(e)}")
            continue

    return df_formatted

def batch_process_dataframe(df: pd.DataFrame, process_func: Callable, batch_size: int = 1000) -> pd.DataFrame:
    """
    批量处理大型DataFrame
    避免内存溢出

    Args:
        df: 要处理的DataFrame
        process_func: 处理函数
        batch_size: 批次大小

    Returns:
        处理后的DataFrame
    """
    if len(df) <= batch_size:
        return process_func(df)

    results = []
    for i in range(0, len(df), batch_size):
        batch = df.iloc[i:i + batch_size]
        processed_batch = process_func(batch)
        results.append(processed_batch)

    return pd.concat(results, ignore_index=True)

def efficient_iterrows_replacement(df: pd.DataFrame, process_func: Callable) -> List[Any]:
    """
    高效的iterrows替代方案
    使用向量化操作或numpy数组

    Args:
        df: 要遍历的DataFrame
        process_func: 处理每行的函数

    Returns:
        处理结果列表
    """
    # 转换为numpy数组以提高性能
    values = df.values
    columns = df.columns.tolist()

    results = []
    for row_values in values:
        row_dict = dict(zip(columns, row_values))
        result = process_func(row_dict)
        results.append(result)

    return results

@st.cache_data(ttl=300)  # 缓存5分钟
def cached_expensive_computation(data: Any, computation_type: str) -> Any:
    """
    缓存昂贵的计算操作

    Args:
        data: 输入数据
        computation_type: 计算类型

    Returns:
        计算结果
    """
    # 这里可以添加各种昂贵的计算
    if computation_type == "correlation_matrix":
        if isinstance(data, pd.DataFrame):
            return data.corr()
    elif computation_type == "statistical_summary":
        if isinstance(data, pd.DataFrame):
            return data.describe()

    return data

def optimize_loops(data: List[Any], operation: Callable, use_numpy: bool = True) -> List[Any]:
    """
    优化循环操作

    Args:
        data: 输入数据列表
        operation: 要执行的操作
        use_numpy: 是否使用numpy优化

    Returns:
        操作结果列表
    """
    if use_numpy and len(data) > 100:
        # 对于大数据集使用numpy向量化
        try:
            np_data = np.array(data)
            return operation(np_data).tolist()
        except Exception:
            # 如果numpy操作失败，回退到普通循环
            pass

    # 普通循环
    return [operation(item) for item in data]

class PerformanceMonitor:
    """性能监控器"""

    def __init__(self):
        self.metrics = {}
        self.start_times = {}

    def start_timer(self, operation_name: str):
        """开始计时"""
        self.start_times[operation_name] = time.time()

    def end_timer(self, operation_name: str):
        """结束计时并记录"""
        if operation_name in self.start_times:
            duration = time.time() - self.start_times[operation_name]
            self.metrics[operation_name] = duration
            del self.start_times[operation_name]
            return duration
        return None

    def get_metrics(self) -> Dict[str, float]:
        """获取性能指标"""
        return self.metrics.copy()

    def display_metrics(self):
        """在Streamlit中显示性能指标"""
        if self.metrics:
            st.subheader("🚀 性能指标")
            for operation, duration in self.metrics.items():
                if duration > 1.0:
                    st.warning(f"⚠️ {operation}: {duration:.2f}秒 (较慢)")
                else:
                    st.success(f"✅ {operation}: {duration:.3f}秒")

# 全局性能监控器实例
performance_monitor = PerformanceMonitor()

def memory_efficient_dataframe_operations(df: pd.DataFrame) -> pd.DataFrame:
    """
    内存高效的DataFrame操作
    """
    # 优化数据类型以减少内存使用
    for col in df.select_dtypes(include=['int64']).columns:
        if df[col].min() >= 0:
            if df[col].max() < 255:
                df[col] = df[col].astype('uint8')
            elif df[col].max() < 65535:
                df[col] = df[col].astype('uint16')
            elif df[col].max() < 4294967295:
                df[col] = df[col].astype('uint32')
        else:
            if df[col].min() > -128 and df[col].max() < 127:
                df[col] = df[col].astype('int8')
            elif df[col].min() > -32768 and df[col].max() < 32767:
                df[col] = df[col].astype('int16')
            elif df[col].min() > -2147483648 and df[col].max() < 2147483647:
                df[col] = df[col].astype('int32')

    # 优化浮点数类型
    for col in df.select_dtypes(include=['float64']).columns:
        df[col] = pd.to_numeric(df[col], downcast='float')

    return df
