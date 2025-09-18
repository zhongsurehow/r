"""
统一数据处理工具
整合重复的数据处理逻辑
"""

import pandas as pd
import numpy as np
from typing import Any, Dict, List, Optional, Union, Callable
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class DataProcessor:
    """统一数据处理器"""

    @staticmethod
    def clean_dataframe(df: pd.DataFrame,
                       fill_method: str = 'forward',
                       drop_na_cols: List[str] = None,
                       round_decimals: Dict[str, int] = None) -> pd.DataFrame:
        """
        清理DataFrame

        Args:
            df: 输入DataFrame
            fill_method: 填充方法 ('forward', 'backward', 'zero', 'mean', 'median')
            drop_na_cols: 需要删除NA值的列
            round_decimals: 需要四舍五入的列及小数位数
        """
        df_clean = df.copy()

        # 删除指定列的NA值
        if drop_na_cols:
            for col in drop_na_cols:
                if col in df_clean.columns:
                    df_clean = df_clean.dropna(subset=[col])

        # 填充NA值
        if fill_method == 'forward':
            df_clean = df_clean.fillna(method='ffill')
        elif fill_method == 'backward':
            df_clean = df_clean.fillna(method='bfill')
        elif fill_method == 'zero':
            df_clean = df_clean.fillna(0)
        elif fill_method == 'mean':
            numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
            df_clean[numeric_cols] = df_clean[numeric_cols].fillna(df_clean[numeric_cols].mean())
        elif fill_method == 'median':
            numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
            df_clean[numeric_cols] = df_clean[numeric_cols].fillna(df_clean[numeric_cols].median())

        # 四舍五入
        if round_decimals:
            for col, decimals in round_decimals.items():
                if col in df_clean.columns:
                    df_clean[col] = df_clean[col].round(decimals)

        return df_clean

    @staticmethod
    def calculate_returns(price_data: pd.DataFrame,
                         method: str = 'simple',
                         periods: int = 1) -> pd.DataFrame:
        """
        计算收益率

        Args:
            price_data: 价格数据
            method: 计算方法 ('simple', 'log')
            periods: 计算周期
        """
        if method == 'simple':
            returns = price_data.pct_change(periods=periods)
        elif method == 'log':
            returns = np.log(price_data / price_data.shift(periods))
        else:
            raise ValueError(f"不支持的计算方法: {method}")

        return returns.dropna()

    @staticmethod
    def normalize_data(data: pd.DataFrame,
                      method: str = 'minmax',
                      columns: List[str] = None) -> pd.DataFrame:
        """
        数据标准化

        Args:
            data: 输入数据
            method: 标准化方法 ('minmax', 'zscore', 'robust')
            columns: 需要标准化的列
        """
        df_norm = data.copy()

        if columns is None:
            columns = df_norm.select_dtypes(include=[np.number]).columns

        for col in columns:
            if col not in df_norm.columns:
                continue

            if method == 'minmax':
                min_val = df_norm[col].min()
                max_val = df_norm[col].max()
                if max_val != min_val:
                    df_norm[col] = (df_norm[col] - min_val) / (max_val - min_val)
            elif method == 'zscore':
                mean_val = df_norm[col].mean()
                std_val = df_norm[col].std()
                if std_val != 0:
                    df_norm[col] = (df_norm[col] - mean_val) / std_val
            elif method == 'robust':
                median_val = df_norm[col].median()
                mad_val = (df_norm[col] - median_val).abs().median()
                if mad_val != 0:
                    df_norm[col] = (df_norm[col] - median_val) / mad_val

        return df_norm

    @staticmethod
    def resample_data(data: pd.DataFrame,
                     freq: str = '1H',
                     agg_methods: Dict[str, str] = None) -> pd.DataFrame:
        """
        重采样数据

        Args:
            data: 输入数据（需要时间索引）
            freq: 重采样频率
            agg_methods: 聚合方法字典
        """
        if not isinstance(data.index, pd.DatetimeIndex):
            raise ValueError("数据索引必须是DatetimeIndex")

        if agg_methods is None:
            # 默认聚合方法
            agg_methods = {}
            for col in data.columns:
                if 'price' in col.lower() or 'close' in col.lower():
                    agg_methods[col] = 'last'
                elif 'volume' in col.lower():
                    agg_methods[col] = 'sum'
                elif 'high' in col.lower():
                    agg_methods[col] = 'max'
                elif 'low' in col.lower():
                    agg_methods[col] = 'min'
                elif 'open' in col.lower():
                    agg_methods[col] = 'first'
                else:
                    agg_methods[col] = 'mean'

        return data.resample(freq).agg(agg_methods)

    @staticmethod
    def detect_outliers(data: pd.DataFrame,
                       method: str = 'iqr',
                       columns: List[str] = None,
                       threshold: float = 1.5) -> pd.DataFrame:
        """
        检测异常值

        Args:
            data: 输入数据
            method: 检测方法 ('iqr', 'zscore', 'isolation')
            columns: 检测的列
            threshold: 阈值
        """
        if columns is None:
            columns = data.select_dtypes(include=[np.number]).columns

        outliers = pd.DataFrame(index=data.index)

        for col in columns:
            if col not in data.columns:
                continue

            if method == 'iqr':
                Q1 = data[col].quantile(0.25)
                Q3 = data[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - threshold * IQR
                upper_bound = Q3 + threshold * IQR
                outliers[col] = (data[col] < lower_bound) | (data[col] > upper_bound)

            elif method == 'zscore':
                z_scores = np.abs((data[col] - data[col].mean()) / data[col].std())
                outliers[col] = z_scores > threshold

            elif method == 'isolation':
                from sklearn.ensemble import IsolationForest
                iso_forest = IsolationForest(contamination=0.1, random_state=42)
                outliers[col] = iso_forest.fit_predict(data[[col]].fillna(0)) == -1

        return outliers

    @staticmethod
    def rolling_statistics(data: pd.DataFrame,
                          window: int = 20,
                          statistics: List[str] = None) -> pd.DataFrame:
        """
        计算滚动统计

        Args:
            data: 输入数据
            window: 滚动窗口大小
            statistics: 统计指标列表
        """
        if statistics is None:
            statistics = ['mean', 'std', 'min', 'max']

        result = pd.DataFrame(index=data.index)

        for col in data.select_dtypes(include=[np.number]).columns:
            for stat in statistics:
                if stat == 'mean':
                    result[f"{col}_ma_{window}"] = data[col].rolling(window).mean()
                elif stat == 'std':
                    result[f"{col}_std_{window}"] = data[col].rolling(window).std()
                elif stat == 'min':
                    result[f"{col}_min_{window}"] = data[col].rolling(window).min()
                elif stat == 'max':
                    result[f"{col}_max_{window}"] = data[col].rolling(window).max()
                elif stat == 'median':
                    result[f"{col}_median_{window}"] = data[col].rolling(window).median()
                elif stat == 'sum':
                    result[f"{col}_sum_{window}"] = data[col].rolling(window).sum()

        return result

    @staticmethod
    def merge_dataframes(dataframes: List[pd.DataFrame],
                        how: str = 'outer',
                        suffixes: List[str] = None) -> pd.DataFrame:
        """
        合并多个DataFrame

        Args:
            dataframes: DataFrame列表
            how: 合并方式
            suffixes: 后缀列表
        """
        if not dataframes:
            return pd.DataFrame()

        if len(dataframes) == 1:
            return dataframes[0]

        result = dataframes[0]

        for i, df in enumerate(dataframes[1:], 1):
            suffix = f"_{i}" if suffixes is None or i >= len(suffixes) else f"_{suffixes[i]}"
            result = result.join(df, how=how, rsuffix=suffix)

        return result

    @staticmethod
    def pivot_data(data: pd.DataFrame,
                  index_col: str,
                  columns_col: str,
                  values_col: str,
                  agg_func: str = 'mean') -> pd.DataFrame:
        """
        数据透视

        Args:
            data: 输入数据
            index_col: 索引列
            columns_col: 列名列
            values_col: 值列
            agg_func: 聚合函数
        """
        return data.pivot_table(
            index=index_col,
            columns=columns_col,
            values=values_col,
            aggfunc=agg_func,
            fill_value=0
        )

class TimeSeriesProcessor:
    """时间序列数据处理器"""

    @staticmethod
    def create_time_features(data: pd.DataFrame,
                           datetime_col: str = None) -> pd.DataFrame:
        """
        创建时间特征

        Args:
            data: 输入数据
            datetime_col: 时间列名（如果为None则使用索引）
        """
        df = data.copy()

        if datetime_col:
            dt_series = pd.to_datetime(df[datetime_col])
        else:
            if not isinstance(df.index, pd.DatetimeIndex):
                raise ValueError("索引必须是DatetimeIndex或指定datetime_col")
            dt_series = df.index

        # 基础时间特征
        df['year'] = dt_series.year
        df['month'] = dt_series.month
        df['day'] = dt_series.day
        df['hour'] = dt_series.hour
        df['minute'] = dt_series.minute
        df['weekday'] = dt_series.weekday
        df['quarter'] = dt_series.quarter

        # 周期性特征
        df['is_weekend'] = dt_series.weekday >= 5
        df['is_month_start'] = dt_series.is_month_start
        df['is_month_end'] = dt_series.is_month_end
        df['is_quarter_start'] = dt_series.is_quarter_start
        df['is_quarter_end'] = dt_series.is_quarter_end

        # 三角函数编码（捕获周期性）
        df['hour_sin'] = np.sin(2 * np.pi * dt_series.hour / 24)
        df['hour_cos'] = np.cos(2 * np.pi * dt_series.hour / 24)
        df['day_sin'] = np.sin(2 * np.pi * dt_series.dayofyear / 365)
        df['day_cos'] = np.cos(2 * np.pi * dt_series.dayofyear / 365)

        return df

    @staticmethod
    def lag_features(data: pd.DataFrame,
                    columns: List[str],
                    lags: List[int]) -> pd.DataFrame:
        """
        创建滞后特征

        Args:
            data: 输入数据
            columns: 需要创建滞后特征的列
            lags: 滞后期数列表
        """
        df = data.copy()

        for col in columns:
            if col not in df.columns:
                continue
            for lag in lags:
                df[f"{col}_lag_{lag}"] = df[col].shift(lag)

        return df

    @staticmethod
    def difference_features(data: pd.DataFrame,
                          columns: List[str],
                          periods: List[int] = None) -> pd.DataFrame:
        """
        创建差分特征

        Args:
            data: 输入数据
            columns: 需要差分的列
            periods: 差分周期列表
        """
        if periods is None:
            periods = [1]

        df = data.copy()

        for col in columns:
            if col not in df.columns:
                continue
            for period in periods:
                df[f"{col}_diff_{period}"] = df[col].diff(period)
                df[f"{col}_pct_change_{period}"] = df[col].pct_change(period)

        return df

class DataValidator:
    """数据验证器"""

    @staticmethod
    def validate_dataframe(df: pd.DataFrame,
                          required_columns: List[str] = None,
                          min_rows: int = 1,
                          max_missing_ratio: float = 0.5) -> Dict[str, Any]:
        """
        验证DataFrame

        Args:
            df: 输入DataFrame
            required_columns: 必需的列
            min_rows: 最小行数
            max_missing_ratio: 最大缺失比例
        """
        validation_result = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'info': {}
        }

        # 基础检查
        if df.empty:
            validation_result['is_valid'] = False
            validation_result['errors'].append("DataFrame为空")
            return validation_result

        if len(df) < min_rows:
            validation_result['is_valid'] = False
            validation_result['errors'].append(f"行数不足，需要至少{min_rows}行，实际{len(df)}行")

        # 必需列检查
        if required_columns:
            missing_cols = set(required_columns) - set(df.columns)
            if missing_cols:
                validation_result['is_valid'] = False
                validation_result['errors'].append(f"缺少必需的列: {missing_cols}")

        # 缺失值检查
        missing_ratios = df.isnull().sum() / len(df)
        high_missing_cols = missing_ratios[missing_ratios > max_missing_ratio].index.tolist()
        if high_missing_cols:
            validation_result['warnings'].append(f"以下列缺失值比例过高: {high_missing_cols}")

        # 数据类型检查
        validation_result['info']['dtypes'] = df.dtypes.to_dict()
        validation_result['info']['shape'] = df.shape
        validation_result['info']['missing_counts'] = df.isnull().sum().to_dict()
        validation_result['info']['memory_usage'] = df.memory_usage(deep=True).sum()

        return validation_result

    @staticmethod
    def check_data_quality(df: pd.DataFrame) -> Dict[str, Any]:
        """
        检查数据质量

        Args:
            df: 输入DataFrame
        """
        quality_report = {
            'completeness': {},
            'consistency': {},
            'accuracy': {},
            'timeliness': {}
        }

        # 完整性检查
        total_cells = df.size
        missing_cells = df.isnull().sum().sum()
        quality_report['completeness']['missing_ratio'] = missing_cells / total_cells
        quality_report['completeness']['complete_rows'] = len(df.dropna())
        quality_report['completeness']['complete_ratio'] = len(df.dropna()) / len(df)

        # 一致性检查
        for col in df.select_dtypes(include=[np.number]).columns:
            # 检查异常值
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            outliers = df[(df[col] < Q1 - 1.5 * IQR) | (df[col] > Q3 + 1.5 * IQR)]
            quality_report['consistency'][f'{col}_outliers'] = len(outliers)

        # 准确性检查（基础统计）
        quality_report['accuracy']['numeric_stats'] = df.describe().to_dict()

        # 时效性检查（如果有时间列）
        datetime_cols = df.select_dtypes(include=['datetime64']).columns
        if len(datetime_cols) > 0:
            for col in datetime_cols:
                quality_report['timeliness'][f'{col}_range'] = {
                    'min': df[col].min(),
                    'max': df[col].max(),
                    'span_days': (df[col].max() - df[col].min()).days
                }

        return quality_report

# 便利函数
def quick_clean(df: pd.DataFrame, **kwargs) -> pd.DataFrame:
    """快速清理DataFrame"""
    return DataProcessor.clean_dataframe(df, **kwargs)

def quick_returns(price_data: pd.DataFrame, **kwargs) -> pd.DataFrame:
    """快速计算收益率"""
    return DataProcessor.calculate_returns(price_data, **kwargs)

def quick_normalize(data: pd.DataFrame, **kwargs) -> pd.DataFrame:
    """快速标准化数据"""
    return DataProcessor.normalize_data(data, **kwargs)

def quick_validate(df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
    """快速验证DataFrame"""
    return DataValidator.validate_dataframe(df, **kwargs)

# 导出主要功能
__all__ = [
    'DataProcessor', 'TimeSeriesProcessor', 'DataValidator',
    'quick_clean', 'quick_returns', 'quick_normalize', 'quick_validate'
]
