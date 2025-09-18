"""
依赖管理工具
检查关键依赖的可用性并提供优雅降级
"""

import importlib
import logging
import streamlit as st
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class DependencyInfo:
    """依赖信息"""
    name: str
    import_name: str
    required: bool
    description: str
    install_command: str
    fallback_message: str

class DependencyManager:
    """依赖管理器"""

    # 关键依赖配置
    DEPENDENCIES = {
        'ccxt': DependencyInfo(
            name='ccxt',
            import_name='ccxt',
            required=False,
            description='CCXT - 加密货币交易库，提供多交易所统一API',
            install_command='pip install ccxt',
            fallback_message='CCXT功能已禁用，使用模拟数据模式'
        ),
        'ccxt_pro': DependencyInfo(
            name='ccxt-pro',
            import_name='ccxtpro',
            required=False,
            description='CCXT Pro - 专业版加密货币交易库，提供实时数据流',
            install_command='pip install ccxt-pro',
            fallback_message='实时数据流功能已禁用，使用模拟数据模式'
        ),
        'ta_lib': DependencyInfo(
            name='TA-Lib',
            import_name='talib',
            required=False,
            description='技术分析库，提供高级技术指标计算',
            install_command='pip install TA-Lib',
            fallback_message='高级技术指标功能已禁用，使用基础指标'
        ),
        'redis': DependencyInfo(
            name='Redis',
            import_name='redis',
            required=False,
            description='Redis缓存数据库，提供高性能缓存',
            install_command='pip install redis',
            fallback_message='Redis缓存已禁用，使用内存缓存'
        )
    }

    def __init__(self):
        self._availability_cache = {}
        self._check_all_dependencies()

    def _check_all_dependencies(self):
        """检查所有依赖的可用性"""
        for dep_key, dep_info in self.DEPENDENCIES.items():
            self._availability_cache[dep_key] = self._check_dependency(dep_info)

    def _check_dependency(self, dep_info: DependencyInfo) -> bool:
        """检查单个依赖的可用性"""
        try:
            importlib.import_module(dep_info.import_name)
            logger.info(f"依赖 {dep_info.name} 可用")
            return True
        except ImportError:
            logger.warning(f"依赖 {dep_info.name} 不可用: {dep_info.fallback_message}")
            return False
        except Exception as e:
            logger.error(f"检查依赖 {dep_info.name} 时出错: {e}")
            return False

    def is_available(self, dependency_key: str) -> bool:
        """检查指定依赖是否可用"""
        return self._availability_cache.get(dependency_key, False)

    def get_missing_dependencies(self) -> List[DependencyInfo]:
        """获取缺失的依赖列表"""
        missing = []
        for dep_key, dep_info in self.DEPENDENCIES.items():
            if not self._availability_cache.get(dep_key, False):
                missing.append(dep_info)
        return missing

    def get_dependency_status(self) -> Dict[str, bool]:
        """获取所有依赖的状态"""
        return self._availability_cache.copy()

    def display_dependency_warnings(self):
        """在Streamlit中显示依赖警告"""
        missing_deps = self.get_missing_dependencies()

        if missing_deps:
            with st.expander("⚠️ 可选依赖缺失", expanded=False):
                st.warning("以下可选依赖未安装，某些功能可能受限：")

                for dep in missing_deps:
                    st.markdown(f"""
                    **{dep.name}**
                    - 描述：{dep.description}
                    - 安装命令：`{dep.install_command}`
                    - 影响：{dep.fallback_message}
                    """)

                st.info("这些依赖是可选的，应用仍可正常运行，但某些高级功能将被禁用。")

    def require_dependency(self, dependency_key: str, error_message: str = None) -> bool:
        """要求特定依赖，如果不可用则显示错误"""
        if not self.is_available(dependency_key):
            dep_info = self.DEPENDENCIES.get(dependency_key)
            if dep_info:
                error_msg = error_message or f"此功能需要 {dep_info.name}，请先安装：{dep_info.install_command}"
                st.error(error_msg)
                return False
        return True

    def get_feature_availability(self) -> Dict[str, bool]:
        """获取功能可用性状态"""
        return {
            'real_time_streaming': self.is_available('ccxt_pro'),
            'advanced_ta_indicators': self.is_available('ta_lib'),
            'redis_caching': self.is_available('redis'),
            'basic_trading': True,  # 基础功能始终可用
            'demo_mode': True,      # 演示模式始终可用
        }

    def display_feature_status(self):
        """显示功能状态面板"""
        features = self.get_feature_availability()

        st.subheader("🔧 功能状态")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**可用功能：**")
            for feature, available in features.items():
                if available:
                    feature_name = feature.replace('_', ' ').title()
                    st.success(f"✅ {feature_name}")

        with col2:
            st.markdown("**受限功能：**")
            for feature, available in features.items():
                if not available:
                    feature_name = feature.replace('_', ' ').title()
                    st.warning(f"⚠️ {feature_name}")

        # 显示改进建议
        missing_deps = self.get_missing_dependencies()
        if missing_deps:
            st.markdown("**改进建议：**")
            for dep in missing_deps:
                st.info(f"安装 {dep.name} 以启用更多功能：`{dep.install_command}`")

# 全局依赖管理器实例
dependency_manager = DependencyManager()

def check_ccxt() -> bool:
    """检查ccxt是否可用"""
    return dependency_manager.is_available('ccxt')

def check_ccxt_pro() -> bool:
    """检查ccxt-pro是否可用"""
    return dependency_manager.is_available('ccxt_pro')

def check_ta_lib() -> bool:
    """检查TA-Lib是否可用"""
    return dependency_manager.is_available('ta_lib')

def check_redis() -> bool:
    """检查Redis是否可用"""
    return dependency_manager.is_available('redis')

def display_dependency_status():
    """显示依赖状态（便捷函数）"""
    dependency_manager.display_dependency_warnings()
    dependency_manager.display_feature_status()
