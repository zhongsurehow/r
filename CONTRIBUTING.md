# 贡献指南 (Contributing Guide)

## 项目结构规范

### 目录结构
```
src/
├── components/          # UI组件
├── pages/              # 页面模块
├── providers/          # 数据提供者
├── ui/                 # UI相关工具
├── utils/              # 工具包
│   ├── __init__.py
│   ├── error_handler.py
│   ├── dependency_manager.py
│   └── logging_utils.py
├── utils_general.py    # 通用工具函数
├── imports.py          # 导入管理
└── app.py             # 主应用
```

### 命名规范

#### 文件和模块命名
- **模块名称**: 使用小写字母和下划线 (例如: `data_processing.py`)
- **包名称**: 使用小写字母，避免下划线 (例如: `utils`, `components`)
- **类名**: 使用驼峰命名法 (例如: `DataProcessor`, `ErrorHandler`)
- **函数名**: 使用小写字母和下划线 (例如: `process_data`, `handle_error`)
- **常量**: 使用大写字母和下划线 (例如: `MAX_RETRY_COUNT`, `DEFAULT_TIMEOUT`)

#### 变量命名
- **局部变量**: 使用小写字母和下划线 (例如: `user_data`, `api_response`)
- **私有变量**: 以单下划线开头 (例如: `_internal_state`)
- **特殊方法**: 以双下划线包围 (例如: `__init__`, `__str__`)

## 代码质量标准

### 错误处理
1. **使用具体异常类型**
   ```python
   # ❌ 错误做法
   try:
       result = risky_operation()
   except Exception as e:
       print("Something went wrong")
   
   # ✅ 正确做法
   try:
       result = risky_operation()
   except ConnectionError as e:
       logger.error(f"网络连接失败: {e}")
       st.error("网络连接失败，请检查网络设置")
   except ValueError as e:
       logger.error(f"数据格式错误: {e}")
       st.error("数据格式不正确，请检查输入")
   ```

2. **使用自定义异常类**
   ```python
   from src.utils.error_handler import DataFetchError, NetworkError
   
   try:
       data = fetch_market_data()
   except DataFetchError as e:
       handle_error(e, "获取市场数据失败")
   ```

3. **记录详细日志**
   ```python
   import logging
   logger = logging.getLogger(__name__)
   
   try:
       process_data()
   except Exception as e:
       logger.exception("处理数据时发生错误")  # 自动记录堆栈跟踪
       raise
   ```

### 代码格式化
- 使用 **Black** 进行代码格式化
- 使用 **isort** 进行导入排序
- 行长度限制为 **120** 字符
- 使用 **Flake8** 进行代码检查

### 导入规范
```python
# 标准库导入
import os
import sys
from typing import Dict, List, Optional

# 第三方库导入
import streamlit as st
import pandas as pd
import numpy as np

# 本地导入
from src.utils.error_handler import handle_error
from src.providers.base import BaseProvider
```

## 开发工作流

### 1. 设置开发环境
```bash
# 安装开发依赖
pip install black isort flake8 pre-commit mypy

# 安装pre-commit钩子
pre-commit install
```

### 2. 代码提交前检查
```bash
# 格式化代码
black src/
isort src/

# 检查代码质量
flake8 src/

# 类型检查
mypy src/
```

### 3. 提交规范
- 提交信息使用中文
- 格式: `类型: 简短描述`
- 类型包括:
  - `feat`: 新功能
  - `fix`: 修复bug
  - `docs`: 文档更新
  - `style`: 代码格式调整
  - `refactor`: 代码重构
  - `test`: 测试相关
  - `chore`: 构建过程或辅助工具的变动

### 4. 功能开发规范

#### 新增工具函数
- 所有共享工具函数应放在 `src/utils/` 包中
- 为每个工具模块添加适当的文档字符串
- 包含基本的单元测试

#### 新增页面或组件
- 页面放在 `src/pages/` 目录
- 组件放在 `src/components/` 目录
- 遵循现有的命名和结构模式

#### API集成
- 所有API相关代码放在 `src/providers/` 目录
- 实现适当的错误处理和重试机制
- 添加日志记录用于调试

## 测试规范

### 单元测试
- 测试文件命名: `test_*.py`
- 放置在对应模块的 `tests/` 目录下
- 使用 `pytest` 框架

### 集成测试
- 测试关键功能的端到端流程
- 模拟外部API调用
- 验证错误处理机制

## 性能优化

### 缓存策略
- 使用 `@st.cache_data` 缓存数据获取
- 使用 `@st.cache_resource` 缓存资源初始化
- 合理设置缓存过期时间

### 异步处理
- 对于耗时操作使用异步处理
- 使用 `safe_run_async` 函数处理异步调用
- 提供用户友好的加载提示

## 安全规范

### API密钥管理
- 使用环境变量存储敏感信息
- 不在代码中硬编码密钥
- 使用 `.env` 文件进行本地开发配置

### 数据验证
- 验证所有用户输入
- 使用类型提示增强代码安全性
- 实施适当的数据清理

## 文档规范

### 代码文档
- 为所有公共函数和类添加文档字符串
- 使用Google风格的文档字符串
- 包含参数说明、返回值和异常信息

### 示例
```python
def fetch_market_data(symbol: str, timeframe: str = "1h") -> Dict:
    """获取市场数据
    
    Args:
        symbol: 交易对符号，例如 'BTC/USDT'
        timeframe: 时间框架，默认为 '1h'
    
    Returns:
        包含市场数据的字典
    
    Raises:
        DataFetchError: 当数据获取失败时
        ValueError: 当参数格式不正确时
    """
    pass
```

## 问题报告

### Bug报告
- 提供详细的错误信息和堆栈跟踪
- 包含重现步骤
- 说明预期行为和实际行为

### 功能请求
- 清楚描述需求
- 说明使用场景
- 提供可能的实现方案

---

遵循这些规范将帮助我们维护高质量、可维护的代码库。如有疑问，请随时提出讨论。