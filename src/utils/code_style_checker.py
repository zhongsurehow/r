"""
代码风格检查和统一工具
确保代码遵循一致的风格规范
"""

import ast
import re
import os
from typing import List, Dict, Any, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class CodeStyleChecker:
    """代码风格检查器"""

    def __init__(self):
        self.issues = []
        self.stats = {
            'files_checked': 0,
            'issues_found': 0,
            'lines_checked': 0
        }

    def check_file(self, file_path: str) -> List[Dict[str, Any]]:
        """检查单个文件的代码风格"""
        issues = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')

            self.stats['files_checked'] += 1
            self.stats['lines_checked'] += len(lines)

            # 检查各种风格问题
            issues.extend(self._check_line_length(lines, file_path))
            issues.extend(self._check_imports(content, file_path))
            issues.extend(self._check_naming_conventions(content, file_path))
            issues.extend(self._check_spacing(lines, file_path))
            issues.extend(self._check_docstrings(content, file_path))
            issues.extend(self._check_comments(lines, file_path))

            self.stats['issues_found'] += len(issues)

        except Exception as e:
            logger.error(f"检查文件 {file_path} 时出错: {str(e)}")
            issues.append({
                'file': file_path,
                'line': 0,
                'type': 'error',
                'message': f"无法读取文件: {str(e)}"
            })

        return issues

    def _check_line_length(self, lines: List[str], file_path: str) -> List[Dict[str, Any]]:
        """检查行长度"""
        issues = []
        max_length = 120  # PEP 8 建议79，但现代开发通常使用120

        for i, line in enumerate(lines, 1):
            if len(line) > max_length:
                issues.append({
                    'file': file_path,
                    'line': i,
                    'type': 'line_length',
                    'message': f"行长度 {len(line)} 超过建议的 {max_length} 字符",
                    'severity': 'warning'
                })

        return issues

    def _check_imports(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """检查导入语句"""
        issues = []
        lines = content.split('\n')

        # 检查导入顺序和分组
        import_sections = {
            'stdlib': [],
            'third_party': [],
            'local': []
        }

        stdlib_modules = {
            'os', 'sys', 'time', 'datetime', 'json', 'logging', 'typing',
            'asyncio', 'functools', 'itertools', 'collections', 're',
            'pathlib', 'urllib', 'http', 'email', 'xml', 'html'
        }

        for i, line in enumerate(lines, 1):
            line = line.strip()
            if line.startswith('import ') or line.startswith('from '):
                # 检查是否有多个导入在一行
                if ',' in line and 'from' in line and 'import' in line:
                    if line.count(',') > 2:  # 允许少量的多导入
                        issues.append({
                            'file': file_path,
                            'line': i,
                            'type': 'import_style',
                            'message': "建议将多个导入分行写",
                            'severity': 'info'
                        })

                # 检查导入分组
                if line.startswith('from '):
                    module = line.split()[1].split('.')[0]
                elif line.startswith('import '):
                    module = line.split()[1].split('.')[0]
                else:
                    continue

                if module in stdlib_modules:
                    import_sections['stdlib'].append((i, line))
                elif module.startswith('src.') or module.startswith('.'):
                    import_sections['local'].append((i, line))
                else:
                    import_sections['third_party'].append((i, line))

        return issues

    def _check_naming_conventions(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """检查命名规范"""
        issues = []

        try:
            tree = ast.parse(content)

            for node in ast.walk(tree):
                # 检查函数名
                if isinstance(node, ast.FunctionDef):
                    if not self._is_snake_case(node.name) and not node.name.startswith('__'):
                        issues.append({
                            'file': file_path,
                            'line': node.lineno,
                            'type': 'naming',
                            'message': f"函数名 '{node.name}' 应使用snake_case",
                            'severity': 'warning'
                        })

                # 检查类名
                elif isinstance(node, ast.ClassDef):
                    if not self._is_pascal_case(node.name):
                        issues.append({
                            'file': file_path,
                            'line': node.lineno,
                            'type': 'naming',
                            'message': f"类名 '{node.name}' 应使用PascalCase",
                            'severity': 'warning'
                        })

                # 检查变量名
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            if target.id.isupper() and len(target.id) > 1:
                                # 常量，应该全大写
                                if '_' not in target.id and len(target.id) > 3:
                                    issues.append({
                                        'file': file_path,
                                        'line': node.lineno,
                                        'type': 'naming',
                                        'message': f"常量 '{target.id}' 建议使用UPPER_CASE_WITH_UNDERSCORES",
                                        'severity': 'info'
                                    })

        except SyntaxError:
            # 如果文件有语法错误，跳过AST检查
            pass

        return issues

    def _check_spacing(self, lines: List[str], file_path: str) -> List[Dict[str, Any]]:
        """检查空格和缩进"""
        issues = []

        for i, line in enumerate(lines, 1):
            # 检查行尾空格
            if line.endswith(' ') or line.endswith('\t'):
                issues.append({
                    'file': file_path,
                    'line': i,
                    'type': 'spacing',
                    'message': "行尾有多余的空格",
                    'severity': 'info'
                })

            # 检查制表符
            if '\t' in line:
                issues.append({
                    'file': file_path,
                    'line': i,
                    'type': 'spacing',
                    'message': "使用制表符缩进，建议使用4个空格",
                    'severity': 'warning'
                })

            # 检查操作符周围的空格
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                # 检查 = 周围的空格
                if '=' in stripped and not any(op in stripped for op in ['==', '!=', '<=', '>=']):
                    parts = stripped.split('=')
                    if len(parts) == 2:
                        if not parts[0].endswith(' ') or not parts[1].startswith(' '):
                            issues.append({
                                'file': file_path,
                                'line': i,
                                'type': 'spacing',
                                'message': "赋值操作符 '=' 周围应该有空格",
                                'severity': 'info'
                            })

        return issues

    def _check_docstrings(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """检查文档字符串"""
        issues = []

        try:
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    # 检查是否有文档字符串
                    has_docstring = (
                        node.body and
                        isinstance(node.body[0], ast.Expr) and
                        isinstance(node.body[0].value, ast.Constant) and
                        isinstance(node.body[0].value.value, str)
                    )

                    # 公共方法和类应该有文档字符串
                    if not node.name.startswith('_') and not has_docstring:
                        node_type = "类" if isinstance(node, ast.ClassDef) else "函数"
                        issues.append({
                            'file': file_path,
                            'line': node.lineno,
                            'type': 'docstring',
                            'message': f"公共{node_type} '{node.name}' 缺少文档字符串",
                            'severity': 'info'
                        })

        except SyntaxError:
            pass

        return issues

    def _check_comments(self, lines: List[str], file_path: str) -> List[Dict[str, Any]]:
        """检查注释风格"""
        issues = []

        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('#'):
                # 检查注释格式
                if len(stripped) > 1 and stripped[1] != ' ':
                    issues.append({
                        'file': file_path,
                        'line': i,
                        'type': 'comment',
                        'message': "注释符号 '#' 后应该有一个空格",
                        'severity': 'info'
                    })

                # 检查TODO注释
                if 'TODO' in stripped.upper() or 'FIXME' in stripped.upper():
                    issues.append({
                        'file': file_path,
                        'line': i,
                        'type': 'todo',
                        'message': "发现TODO或FIXME注释，建议及时处理",
                        'severity': 'info'
                    })

        return issues

    def _is_snake_case(self, name: str) -> bool:
        """检查是否为snake_case"""
        return re.match(r'^[a-z_][a-z0-9_]*$', name) is not None

    def _is_pascal_case(self, name: str) -> bool:
        """检查是否为PascalCase"""
        return re.match(r'^[A-Z][a-zA-Z0-9]*$', name) is not None

    def check_directory(self, directory: str, extensions: List[str] = None) -> Dict[str, Any]:
        """检查目录下的所有Python文件"""
        if extensions is None:
            extensions = ['.py']

        all_issues = []

        for root, dirs, files in os.walk(directory):
            # 跳过一些目录
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']

            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    file_path = os.path.join(root, file)
                    issues = self.check_file(file_path)
                    all_issues.extend(issues)

        return {
            'issues': all_issues,
            'stats': self.stats,
            'summary': self._generate_summary(all_issues)
        }

    def _generate_summary(self, issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成检查摘要"""
        summary = {
            'total_issues': len(issues),
            'by_type': {},
            'by_severity': {},
            'by_file': {}
        }

        for issue in issues:
            # 按类型统计
            issue_type = issue.get('type', 'unknown')
            summary['by_type'][issue_type] = summary['by_type'].get(issue_type, 0) + 1

            # 按严重程度统计
            severity = issue.get('severity', 'info')
            summary['by_severity'][severity] = summary['by_severity'].get(severity, 0) + 1

            # 按文件统计
            file_path = issue.get('file', 'unknown')
            summary['by_file'][file_path] = summary['by_file'].get(file_path, 0) + 1

        return summary

class CodeStyleFixer:
    """代码风格修复器"""

    @staticmethod
    def fix_line_endings(file_path: str) -> bool:
        """修复行尾空格"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 移除行尾空格
            lines = content.split('\n')
            fixed_lines = [line.rstrip() for line in lines]

            # 确保文件以换行符结尾
            if fixed_lines and fixed_lines[-1]:
                fixed_lines.append('')

            fixed_content = '\n'.join(fixed_lines)

            if fixed_content != content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                return True

        except Exception as e:
            logger.error(f"修复文件 {file_path} 时出错: {str(e)}")

        return False

    @staticmethod
    def fix_imports(file_path: str) -> bool:
        """修复导入语句格式"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            lines = content.split('\n')
            fixed_lines = []

            for line in lines:
                # 修复导入语句中的空格
                if line.strip().startswith(('import ', 'from ')):
                    # 确保 import 和 from 后有空格
                    line = re.sub(r'import\s+', 'import ', line)
                    line = re.sub(r'from\s+', 'from ', line)
                    line = re.sub(r'\s+import\s+', ' import ', line)

                fixed_lines.append(line)

            fixed_content = '\n'.join(fixed_lines)

            if fixed_content != content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                return True

        except Exception as e:
            logger.error(f"修复导入语句 {file_path} 时出错: {str(e)}")

        return False

def check_code_style(directory: str = "src") -> Dict[str, Any]:
    """检查代码风格的便利函数"""
    checker = CodeStyleChecker()
    return checker.check_directory(directory)

def fix_basic_style_issues(directory: str = "src") -> Dict[str, int]:
    """修复基础的代码风格问题"""
    fixed_files = 0
    total_files = 0

    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']

        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                total_files += 1

                # 修复行尾空格
                if CodeStyleFixer.fix_line_endings(file_path):
                    fixed_files += 1

                # 修复导入格式
                CodeStyleFixer.fix_imports(file_path)

    return {
        'total_files': total_files,
        'fixed_files': fixed_files
    }

# 导出主要功能
__all__ = [
    'CodeStyleChecker', 'CodeStyleFixer',
    'check_code_style', 'fix_basic_style_issues'
]
