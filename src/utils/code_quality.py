"""
代码质量检查和改进工具
提供类型注解、文档字符串、代码规范检查和自动修复功能
"""

import ast
import inspect
import re
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union, Set
from dataclasses import dataclass
from pathlib import Path
import importlib.util
from datetime import datetime


@dataclass
class QualityIssue:
    """代码质量问题数据类"""
    file_path: str
    line_number: int
    issue_type: str
    severity: str  # 'error', 'warning', 'info'
    message: str
    suggestion: Optional[str] = None


@dataclass
class QualityMetrics:
    """代码质量指标数据类"""
    total_lines: int
    documented_functions: int
    total_functions: int
    type_annotated_functions: int
    complexity_score: float
    maintainability_index: float
    test_coverage: float
    issues_count: Dict[str, int]


class TypeAnnotationChecker:
    """类型注解检查器"""
    
    def __init__(self):
        self.issues: List[QualityIssue] = []
    
    def check_file(self, file_path: str) -> List[QualityIssue]:
        """检查文件的类型注解"""
        self.issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            self._check_ast_node(tree, file_path)
            
        except Exception as e:
            self.issues.append(QualityIssue(
                file_path=file_path,
                line_number=1,
                issue_type="parse_error",
                severity="error",
                message=f"无法解析文件: {str(e)}"
            ))
        
        return self.issues
    
    def _check_ast_node(self, node: ast.AST, file_path: str):
        """递归检查AST节点"""
        for child in ast.walk(node):
            if isinstance(child, ast.FunctionDef):
                self._check_function_annotations(child, file_path)
            elif isinstance(child, ast.ClassDef):
                self._check_class_annotations(child, file_path)
    
    def _check_function_annotations(self, node: ast.FunctionDef, file_path: str):
        """检查函数类型注解"""
        # 检查参数注解
        for arg in node.args.args:
            if not arg.annotation and arg.arg != 'self':
                self.issues.append(QualityIssue(
                    file_path=file_path,
                    line_number=node.lineno,
                    issue_type="missing_type_annotation",
                    severity="warning",
                    message=f"函数 '{node.name}' 的参数 '{arg.arg}' 缺少类型注解",
                    suggestion=f"为参数 '{arg.arg}' 添加类型注解，例如: {arg.arg}: str"
                ))
        
        # 检查返回值注解
        if not node.returns and not node.name.startswith('_'):
            self.issues.append(QualityIssue(
                file_path=file_path,
                line_number=node.lineno,
                issue_type="missing_return_annotation",
                severity="warning",
                message=f"函数 '{node.name}' 缺少返回值类型注解",
                suggestion=f"为函数 '{node.name}' 添加返回值注解，例如: -> None 或 -> str"
            ))
    
    def _check_class_annotations(self, node: ast.ClassDef, file_path: str):
        """检查类属性注解"""
        for child in node.body:
            if isinstance(child, ast.AnnAssign) and not child.annotation:
                self.issues.append(QualityIssue(
                    file_path=file_path,
                    line_number=child.lineno,
                    issue_type="missing_attribute_annotation",
                    severity="info",
                    message=f"类 '{node.name}' 的属性缺少类型注解"
                ))


class DocstringChecker:
    """文档字符串检查器"""
    
    def __init__(self):
        self.issues: List[QualityIssue] = []
    
    def check_file(self, file_path: str) -> List[QualityIssue]:
        """检查文件的文档字符串"""
        self.issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            self._check_ast_node(tree, file_path)
            
        except Exception as e:
            self.issues.append(QualityIssue(
                file_path=file_path,
                line_number=1,
                issue_type="parse_error",
                severity="error",
                message=f"无法解析文件: {str(e)}"
            ))
        
        return self.issues
    
    def _check_ast_node(self, node: ast.AST, file_path: str):
        """递归检查AST节点"""
        for child in ast.walk(node):
            if isinstance(child, ast.FunctionDef):
                self._check_function_docstring(child, file_path)
            elif isinstance(child, ast.ClassDef):
                self._check_class_docstring(child, file_path)
    
    def _check_function_docstring(self, node: ast.FunctionDef, file_path: str):
        """检查函数文档字符串"""
        docstring = ast.get_docstring(node)
        
        if not docstring and not node.name.startswith('_'):
            self.issues.append(QualityIssue(
                file_path=file_path,
                line_number=node.lineno,
                issue_type="missing_docstring",
                severity="warning",
                message=f"函数 '{node.name}' 缺少文档字符串",
                suggestion=f"为函数 '{node.name}' 添加文档字符串，描述其功能、参数和返回值"
            ))
        elif docstring:
            self._validate_docstring_format(docstring, node.name, file_path, node.lineno)
    
    def _check_class_docstring(self, node: ast.ClassDef, file_path: str):
        """检查类文档字符串"""
        docstring = ast.get_docstring(node)
        
        if not docstring:
            self.issues.append(QualityIssue(
                file_path=file_path,
                line_number=node.lineno,
                issue_type="missing_class_docstring",
                severity="warning",
                message=f"类 '{node.name}' 缺少文档字符串",
                suggestion=f"为类 '{node.name}' 添加文档字符串，描述其用途和主要功能"
            ))
        elif docstring:
            self._validate_docstring_format(docstring, node.name, file_path, node.lineno)
    
    def _validate_docstring_format(self, docstring: str, name: str, file_path: str, line_number: int):
        """验证文档字符串格式"""
        lines = docstring.strip().split('\n')
        
        # 检查是否有简短描述
        if not lines[0].strip():
            self.issues.append(QualityIssue(
                file_path=file_path,
                line_number=line_number,
                issue_type="docstring_format",
                severity="info",
                message=f"{name} 的文档字符串应以简短描述开始"
            ))
        
        # 检查是否过短
        if len(docstring.strip()) < 10:
            self.issues.append(QualityIssue(
                file_path=file_path,
                line_number=line_number,
                issue_type="docstring_too_short",
                severity="info",
                message=f"{name} 的文档字符串过于简短，应提供更详细的描述"
            ))


class CodeStyleChecker:
    """代码风格检查器"""
    
    def __init__(self):
        self.issues: List[QualityIssue] = []
    
    def check_file(self, file_path: str) -> List[QualityIssue]:
        """检查文件的代码风格"""
        self.issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            self._check_line_length(lines, file_path)
            self._check_naming_conventions(file_path)
            self._check_imports(lines, file_path)
            self._check_whitespace(lines, file_path)
            
        except Exception as e:
            self.issues.append(QualityIssue(
                file_path=file_path,
                line_number=1,
                issue_type="read_error",
                severity="error",
                message=f"无法读取文件: {str(e)}"
            ))
        
        return self.issues
    
    def _check_line_length(self, lines: List[str], file_path: str):
        """检查行长度"""
        max_length = 88  # PEP 8 推荐的最大行长度
        
        for i, line in enumerate(lines, 1):
            if len(line.rstrip()) > max_length:
                self.issues.append(QualityIssue(
                    file_path=file_path,
                    line_number=i,
                    issue_type="line_too_long",
                    severity="warning",
                    message=f"第 {i} 行过长 ({len(line.rstrip())} > {max_length} 字符)",
                    suggestion="考虑将长行拆分为多行"
                ))
    
    def _check_naming_conventions(self, file_path: str):
        """检查命名约定"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    self._check_function_naming(node, file_path)
                elif isinstance(node, ast.ClassDef):
                    self._check_class_naming(node, file_path)
                elif isinstance(node, ast.Name):
                    self._check_variable_naming(node, file_path)
                    
        except Exception:
            pass  # 已在其他地方处理解析错误
    
    def _check_function_naming(self, node: ast.FunctionDef, file_path: str):
        """检查函数命名"""
        if not re.match(r'^[a-z_][a-z0-9_]*$', node.name) and not node.name.startswith('__'):
            self.issues.append(QualityIssue(
                file_path=file_path,
                line_number=node.lineno,
                issue_type="naming_convention",
                severity="info",
                message=f"函数名 '{node.name}' 不符合 snake_case 命名约定",
                suggestion="使用 snake_case 命名约定，例如: my_function"
            ))
    
    def _check_class_naming(self, node: ast.ClassDef, file_path: str):
        """检查类命名"""
        if not re.match(r'^[A-Z][a-zA-Z0-9]*$', node.name):
            self.issues.append(QualityIssue(
                file_path=file_path,
                line_number=node.lineno,
                issue_type="naming_convention",
                severity="info",
                message=f"类名 '{node.name}' 不符合 PascalCase 命名约定",
                suggestion="使用 PascalCase 命名约定，例如: MyClass"
            ))
    
    def _check_variable_naming(self, node: ast.Name, file_path: str):
        """检查变量命名"""
        if isinstance(node.ctx, ast.Store):
            if node.id.isupper() and len(node.id) > 1:
                # 常量应该全大写
                if '_' not in node.id:
                    self.issues.append(QualityIssue(
                        file_path=file_path,
                        line_number=node.lineno,
                        issue_type="naming_convention",
                        severity="info",
                        message=f"常量 '{node.id}' 建议使用下划线分隔",
                        suggestion="使用 UPPER_CASE 命名约定，例如: MY_CONSTANT"
                    ))
    
    def _check_imports(self, lines: List[str], file_path: str):
        """检查导入语句"""
        import_lines = []
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('import ') or stripped.startswith('from '):
                import_lines.append((i, stripped))
        
        # 检查导入顺序
        if len(import_lines) > 1:
            prev_type = self._get_import_type(import_lines[0][1])
            for i, (line_num, import_line) in enumerate(import_lines[1:], 1):
                current_type = self._get_import_type(import_line)
                if current_type < prev_type:
                    self.issues.append(QualityIssue(
                        file_path=file_path,
                        line_number=line_num,
                        issue_type="import_order",
                        severity="info",
                        message="导入语句顺序不正确",
                        suggestion="按照标准库、第三方库、本地模块的顺序排列导入"
                    ))
                prev_type = current_type
    
    def _get_import_type(self, import_line: str) -> int:
        """获取导入类型（用于排序）"""
        if import_line.startswith('from __future__'):
            return 0
        elif any(lib in import_line for lib in ['os', 'sys', 'json', 'datetime', 'typing']):
            return 1  # 标准库
        elif any(lib in import_line for lib in ['streamlit', 'pandas', 'numpy', 'plotly']):
            return 2  # 第三方库
        else:
            return 3  # 本地模块
    
    def _check_whitespace(self, lines: List[str], file_path: str):
        """检查空白字符"""
        for i, line in enumerate(lines, 1):
            # 检查行尾空白
            if line.rstrip() != line.rstrip('\n'):
                self.issues.append(QualityIssue(
                    file_path=file_path,
                    line_number=i,
                    issue_type="trailing_whitespace",
                    severity="info",
                    message=f"第 {i} 行有行尾空白字符"
                ))
            
            # 检查制表符
            if '\t' in line:
                self.issues.append(QualityIssue(
                    file_path=file_path,
                    line_number=i,
                    issue_type="tab_character",
                    severity="warning",
                    message=f"第 {i} 行使用了制表符，建议使用空格"
                ))


class ComplexityAnalyzer:
    """复杂度分析器"""
    
    def __init__(self):
        self.complexity_scores: Dict[str, int] = {}
    
    def analyze_file(self, file_path: str) -> Dict[str, int]:
        """分析文件复杂度"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    complexity = self._calculate_cyclomatic_complexity(node)
                    self.complexity_scores[f"{file_path}::{node.name}"] = complexity
            
        except Exception:
            pass
        
        return self.complexity_scores
    
    def _calculate_cyclomatic_complexity(self, node: ast.FunctionDef) -> int:
        """计算圈复杂度"""
        complexity = 1  # 基础复杂度
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, (ast.And, ast.Or)):
                complexity += 1
            elif isinstance(child, ast.comprehension):
                complexity += 1
        
        return complexity


class QualityReporter:
    """代码质量报告生成器"""
    
    def __init__(self):
        self.type_checker = TypeAnnotationChecker()
        self.doc_checker = DocstringChecker()
        self.style_checker = CodeStyleChecker()
        self.complexity_analyzer = ComplexityAnalyzer()
    
    def analyze_project(self, project_path: str) -> QualityMetrics:
        """分析整个项目的代码质量"""
        all_issues = []
        total_lines = 0
        total_functions = 0
        documented_functions = 0
        type_annotated_functions = 0
        complexity_scores = []
        
        # 获取所有Python文件
        python_files = list(Path(project_path).rglob("*.py"))
        
        for file_path in python_files:
            file_path_str = str(file_path)
            
            # 检查类型注解
            type_issues = self.type_checker.check_file(file_path_str)
            all_issues.extend(type_issues)
            
            # 检查文档字符串
            doc_issues = self.doc_checker.check_file(file_path_str)
            all_issues.extend(doc_issues)
            
            # 检查代码风格
            style_issues = self.style_checker.check_file(file_path_str)
            all_issues.extend(style_issues)
            
            # 分析复杂度
            complexity_scores_file = self.complexity_analyzer.analyze_file(file_path_str)
            complexity_scores.extend(complexity_scores_file.values())
            
            # 统计指标
            try:
                with open(file_path_str, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    total_lines += len(lines)
                
                tree = ast.parse(open(file_path_str, 'r', encoding='utf-8').read())
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        total_functions += 1
                        if ast.get_docstring(node):
                            documented_functions += 1
                        if node.returns or any(arg.annotation for arg in node.args.args):
                            type_annotated_functions += 1
                            
            except Exception:
                continue
        
        # 计算指标
        issues_count = {}
        for issue in all_issues:
            issues_count[issue.issue_type] = issues_count.get(issue.issue_type, 0) + 1
        
        avg_complexity = sum(complexity_scores) / len(complexity_scores) if complexity_scores else 0
        maintainability_index = max(0, 171 - 5.2 * np.log(total_lines) - 0.23 * avg_complexity - 16.2 * np.log(total_lines / total_functions if total_functions > 0 else 1))
        
        return QualityMetrics(
            total_lines=total_lines,
            documented_functions=documented_functions,
            total_functions=total_functions,
            type_annotated_functions=type_annotated_functions,
            complexity_score=avg_complexity,
            maintainability_index=maintainability_index,
            test_coverage=0.0,  # 需要额外工具计算
            issues_count=issues_count
        )
    
    def generate_report(self, project_path: str) -> str:
        """生成代码质量报告"""
        metrics = self.analyze_project(project_path)
        
        report = f"""
# 代码质量报告

## 📊 总体指标

- **总行数**: {metrics.total_lines:,}
- **函数总数**: {metrics.total_functions}
- **文档覆盖率**: {(metrics.documented_functions / metrics.total_functions * 100) if metrics.total_functions > 0 else 0:.1f}%
- **类型注解覆盖率**: {(metrics.type_annotated_functions / metrics.total_functions * 100) if metrics.total_functions > 0 else 0:.1f}%
- **平均复杂度**: {metrics.complexity_score:.1f}
- **可维护性指数**: {metrics.maintainability_index:.1f}

## 🔍 问题统计

"""
        
        for issue_type, count in metrics.issues_count.items():
            report += f"- **{issue_type}**: {count} 个问题\n"
        
        report += f"""

## 📈 质量评级

"""
        
        # 计算总体评级
        doc_score = (metrics.documented_functions / metrics.total_functions * 100) if metrics.total_functions > 0 else 0
        type_score = (metrics.type_annotated_functions / metrics.total_functions * 100) if metrics.total_functions > 0 else 0
        complexity_score = max(0, 100 - metrics.complexity_score * 10)
        maintainability_score = min(100, metrics.maintainability_index)
        
        overall_score = (doc_score + type_score + complexity_score + maintainability_score) / 4
        
        if overall_score >= 90:
            grade = "A+ (优秀)"
        elif overall_score >= 80:
            grade = "A (良好)"
        elif overall_score >= 70:
            grade = "B (一般)"
        elif overall_score >= 60:
            grade = "C (需要改进)"
        else:
            grade = "D (急需改进)"
        
        report += f"**总体评级**: {grade} ({overall_score:.1f}/100)\n\n"
        
        return report


# 全局质量检查器实例
quality_reporter = QualityReporter()


def check_code_quality(project_path: str = ".") -> str:
    """检查代码质量并生成报告"""
    return quality_reporter.generate_report(project_path)


def get_quality_metrics(project_path: str = ".") -> QualityMetrics:
    """获取代码质量指标"""
    return quality_reporter.analyze_project(project_path)