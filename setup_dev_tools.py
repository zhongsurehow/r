#!/usr/bin/env python3
"""
开发工具安装和配置脚本
用于快速设置代码质量工具
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """运行命令并处理错误"""
    print(f"正在{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description}成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description}失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False

def install_dev_dependencies():
    """安装开发依赖"""
    dependencies = [
        "black",
        "isort", 
        "flake8",
        "flake8-docstrings",
        "mypy",
        "pre-commit",
        "pytest",
        "types-requests",
        "types-PyYAML"
    ]
    
    for dep in dependencies:
        if not run_command(f"pip install {dep}", f"安装 {dep}"):
            return False
    return True

def setup_pre_commit():
    """设置pre-commit钩子"""
    return run_command("pre-commit install", "设置pre-commit钩子")

def format_code():
    """格式化现有代码"""
    commands = [
        ("black src/", "使用Black格式化代码"),
        ("isort src/", "使用isort排序导入"),
    ]
    
    for command, description in commands:
        run_command(command, description)

def check_code_quality():
    """检查代码质量"""
    commands = [
        ("flake8 src/", "运行Flake8代码检查"),
        ("mypy src/ --ignore-missing-imports", "运行MyPy类型检查"),
    ]
    
    for command, description in commands:
        run_command(command, description)

def main():
    """主函数"""
    print("🚀 开始设置开发环境...")
    
    # 检查是否在项目根目录
    if not Path("src").exists():
        print("❌ 请在项目根目录运行此脚本")
        sys.exit(1)
    
    # 安装依赖
    if not install_dev_dependencies():
        print("❌ 安装开发依赖失败")
        sys.exit(1)
    
    # 设置pre-commit
    if not setup_pre_commit():
        print("⚠️ 设置pre-commit失败，但可以继续")
    
    # 格式化代码
    print("\n📝 格式化现有代码...")
    format_code()
    
    # 检查代码质量
    print("\n🔍 检查代码质量...")
    check_code_quality()
    
    print("\n✅ 开发环境设置完成！")
    print("\n📋 可用命令:")
    print("  black src/          - 格式化代码")
    print("  isort src/          - 排序导入")
    print("  flake8 src/         - 代码质量检查")
    print("  mypy src/           - 类型检查")
    print("  pre-commit run --all-files  - 运行所有检查")

if __name__ == "__main__":
    main()