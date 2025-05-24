"""
Advanced code analyzer for Python files
Detects issues, complexity, and refactoring opportunities
"""

import ast
import re
from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class CodeIssue:
    """Represents a code issue found during analysis."""
    type: str
    severity: str  # 'error', 'warning', 'suggestion'
    line: int
    column: int
    message: str
    suggestion: Optional[str] = None
    auto_fixable: bool = False


@dataclass
class FunctionInfo:
    """Information about a function."""
    name: str
    start_line: int
    end_line: int
    line_count: int
    complexity: int
    args: List[str]
    docstring: Optional[str]
    calls: List[str]
    is_method: bool = False


class ComplexityAnalyzer(ast.NodeVisitor):
    """Analyzes code complexity using cyclomatic complexity."""

    def __init__(self):
        self.complexity = 1  # Base complexity

    def visit_If(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_While(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_For(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_ExceptHandler(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_With(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_BoolOp(self, node):
        self.complexity += len(node.values) - 1
        self.generic_visit(node)


class CodeAnalyzer:
    """Main code analyzer class."""

    def __init__(self):
        self.issues = []
        self.functions = []
        self.classes = []
        self.imports = []

    def analyze_file(self, file_path: str) -> List[CodeIssue]:
        """Analyze a Python file and return list of issues."""
        self.issues = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse AST
            tree = ast.parse(content, filename=file_path)

            # Run various analyses
            self._analyze_syntax_issues(content, file_path)
            self._analyze_structure_issues(tree, content)
            self._analyze_naming_conventions(tree)
            self._analyze_imports(tree)
            self._analyze_code_smells(tree, content)

        except SyntaxError as e:
            self.issues.append(CodeIssue(
                type="syntax_error",
                severity="error",
                line=e.lineno or 1,
                column=e.offset or 0,
                message=f"Syntax error: {e.msg}",
                auto_fixable=False
            ))
        except Exception as e:
            self.issues.append(CodeIssue(
                type="analysis_error",
                severity="error",
                line=1,
                column=0,
                message=f"Analysis failed: {str(e)}",
                auto_fixable=False
            ))

        return self.issues

    def analyze_functions(self, file_path: str) -> List[FunctionInfo]:
        """Analyze functions in a file."""
        self.functions = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)
            lines = content.splitlines()

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    func_info = self._analyze_function(node, lines)
                    self.functions.append(func_info)

        except Exception:
            pass  # Return empty list on error

        return self.functions

    def get_refactor_suggestions(self, file_path: str) -> List[Dict[str, Any]]:
        """Generate refactoring suggestions."""
        suggestions = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            lines = content.splitlines()
            file_size = len(lines)

            # Large file suggestion
            if file_size > 500:
                suggestions.append({
                    'type': 'split_file',
                    'priority': 'high',
                    'message': f'File has {file_size} lines. Consider splitting into smaller modules.',
                    'line': 1,
                    'auto_applicable': True
                })

            # Analyze functions for splitting opportunities
            functions = self.analyze_functions(file_path)
            for func in functions:
                if func.line_count > 50:
                    suggestions.append({
                        'type': 'split_function',
                        'priority': 'medium',
                        'message': f'Function {func.name} has {func.line_count} lines. Consider breaking it down.',
                        'line': func.start_line,
                        'auto_applicable': False,
                        'function_name': func.name
                    })

                if func.complexity > 10:
                    suggestions.append({
                        'type': 'reduce_complexity',
                        'priority': 'high',
                        'message': f'Function {func.name} has high complexity ({func.complexity}). Consider simplifying.',
                        'line': func.start_line,
                        'auto_applicable': False,
                        'function_name': func.name
                    })

            # Check for duplicate code patterns
            duplicates = self._find_duplicate_patterns(content)
            for dup in duplicates:
                suggestions.append({
                    'type': 'extract_duplicate',
                    'priority': 'medium',
                    'message': f'Duplicate code pattern found. Consider extracting to a function.',
                    'line': dup['line'],
                    'auto_applicable': True,
                    'pattern': dup['pattern']
                })

        except Exception:
            pass

        return suggestions

    def _analyze_syntax_issues(self, content: str, file_path: str):
        """Analyze basic syntax and formatting issues."""
        lines = content.splitlines()

        for i, line in enumerate(lines, 1):
            # Line too long
            if len(line) > 120:
                self.issues.append(CodeIssue(
                    type="line_too_long",
                    severity="warning",
                    line=i,
                    column=120,
                    message=f"Line too long ({len(line)} > 120 characters)",
                    suggestion="Break line into multiple lines",
                    auto_fixable=True
                ))

            # Trailing whitespace
            if line.rstrip() != line:
                self.issues.append(CodeIssue(
                    type="trailing_whitespace",
                    severity="suggestion",
                    line=i,
                    column=len(line.rstrip()),
                    message="Trailing whitespace",
                    suggestion="Remove trailing whitespace",
                    auto_fixable=True
                ))

            # Multiple blank lines
            if i > 1 and not line.strip() and not lines[i - 2].strip():
                self.issues.append(CodeIssue(
                    type="multiple_blank_lines",
                    severity="suggestion",
                    line=i,
                    column=0,
                    message="Multiple consecutive blank lines",
                    suggestion="Use single blank line",
                    auto_fixable=True
                ))

    def _analyze_structure_issues(self, tree: ast.AST, content: str):
        """Analyze structural issues."""
        lines = content.splitlines()

        for node in ast.walk(tree):
            # Large functions
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_lines = node.end_lineno - node.lineno + 1
                if func_lines > 50:
                    self.issues.append(CodeIssue(
                        type="large_function",
                        severity="warning",
                        line=node.lineno,
                        column=node.col_offset,
                        message=f"Function '{node.name}' is too long ({func_lines} lines)",
                        suggestion="Break function into smaller functions",
                        auto_fixable=False
                    ))

                # Missing docstring
                if not ast.get_docstring(node):
                    self.issues.append(CodeIssue(
                        type="missing_docstring",
                        severity="suggestion",
                        line=node.lineno,
                        column=node.col_offset,
                        message=f"Function '{node.name}' missing docstring",
                        suggestion="Add descriptive docstring",
                        auto_fixable=True
                    ))

            # Large classes
            elif isinstance(node, ast.ClassDef):
                if hasattr(node, 'end_lineno'):
                    class_lines = node.end_lineno - node.lineno + 1
                    if class_lines > 200:
                        self.issues.append(CodeIssue(
                            type="large_class",
                            severity="warning",
                            line=node.lineno,
                            column=node.col_offset,
                            message=f"Class '{node.name}' is too long ({class_lines} lines)",
                            suggestion="Consider breaking class into smaller classes",
                            auto_fixable=False
                        ))

                # Missing docstring
                if not ast.get_docstring(node):
                    self.issues.append(CodeIssue(
                        type="missing_docstring",
                        severity="suggestion",
                        line=node.lineno,
                        column=node.col_offset,
                        message=f"Class '{node.name}' missing docstring",
                        suggestion="Add descriptive docstring",
                        auto_fixable=True
                    ))

    def _analyze_naming_conventions(self, tree: ast.AST):
        """Analyze naming convention issues."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Function naming (should be snake_case)
                if not re.match(r'^[a-z_][a-z0-9_]*$', node.name) and not node.name.startswith('__'):
                    self.issues.append(CodeIssue(
                        type="naming_convention",
                        severity="suggestion",
                        line=node.lineno,
                        column=node.col_offset,
                        message=f"Function '{node.name}' should use snake_case",
                        suggestion=f"Rename to '{self._to_snake_case(node.name)}'",
                        auto_fixable=True
                    ))

            elif isinstance(node, ast.ClassDef):
                # Class naming (should be PascalCase)
                if not re.match(r'^[A-Z][a-zA-Z0-9]*$', node.name):
                    self.issues.append(CodeIssue(
                        type="naming_convention",
                        severity="suggestion",
                        line=node.lineno,
                        column=node.col_offset,
                        message=f"Class '{node.name}' should use PascalCase",
                        suggestion=f"Rename to '{self._to_pascal_case(node.name)}'",
                        auto_fixable=True
                    ))

            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                # Variable naming (should be snake_case)
                if (len(node.id) > 1 and
                        not node.id.isupper() and  # Not a constant
                        not re.match(r'^[a-z_][a-z0-9_]*$', node.id)):
                    self.issues.append(CodeIssue(
                        type="naming_convention",
                        severity="suggestion",
                        line=node.lineno,
                        column=node.col_offset,
                        message=f"Variable '{node.id}' should use snake_case",
                        suggestion=f"Rename to '{self._to_snake_case(node.id)}'",
                        auto_fixable=True
                    ))

    def _analyze_imports(self, tree: ast.AST):
        """Analyze import-related issues."""
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                imports.append(node)

        # Check for unused imports (simplified check)
        # This is a basic implementation - a full analyzer would track usage

        # Check import order (PEP 8)
        standard_libs = {'os', 'sys', 'json', 'datetime', 're', 'collections', 'typing'}
        stdlib_imports = []
        third_party_imports = []
        local_imports = []

        for node in imports:
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.split('.')[0] in standard_libs:
                        stdlib_imports.append((node.lineno, alias.name))
                    else:
                        third_party_imports.append((node.lineno, alias.name))
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.module.split('.')[0] in standard_libs:
                    stdlib_imports.append((node.lineno, node.module))
                elif node.level > 0:  # Relative import
                    local_imports.append((node.lineno, node.module or ''))
                else:
                    third_party_imports.append((node.lineno, node.module or ''))

        # Check if imports are properly ordered
        all_imports = stdlib_imports + third_party_imports + local_imports
        if len(all_imports) > 1:
            expected_order = sorted(stdlib_imports) + sorted(third_party_imports) + sorted(local_imports)
            actual_order = sorted(all_imports)

            if [imp[1] for imp in all_imports] != [imp[1] for imp in expected_order]:
                first_import_line = min(imp[0] for imp in all_imports)
                self.issues.append(CodeIssue(
                    type="import_order",
                    severity="suggestion",
                    line=first_import_line,
                    column=0,
                    message="Imports not ordered according to PEP 8",
                    suggestion="Organize imports: stdlib, third-party, local",
                    auto_fixable=True
                ))

    def _analyze_code_smells(self, tree: ast.AST, content: str):
        """Analyze code smells and anti-patterns."""
        for node in ast.walk(tree):
            # Long parameter list
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if len(node.args.args) > 6:
                    self.issues.append(CodeIssue(
                        type="long_parameter_list",
                        severity="warning",
                        line=node.lineno,
                        column=node.col_offset,
                        message=f"Function '{node.name}' has too many parameters ({len(node.args.args)})",
                        suggestion="Consider using a dataclass or reducing parameters",
                        auto_fixable=False
                    ))

            # Deeply nested code
            elif isinstance(node, (ast.If, ast.For, ast.While)):
                depth = self._calculate_nesting_depth(node)
                if depth > 4:
                    self.issues.append(CodeIssue(
                        type="deep_nesting",
                        severity="warning",
                        line=node.lineno,
                        column=node.col_offset,
                        message=f"Code nested too deeply (depth: {depth})",
                        suggestion="Extract nested logic into functions",
                        auto_fixable=False
                    ))

    def _analyze_function(self, node: ast.FunctionDef, lines: List[str]) -> FunctionInfo:
        """Analyze a single function."""
        # Calculate complexity
        complexity_analyzer = ComplexityAnalyzer()
        complexity_analyzer.visit(node)

        # Get function calls
        calls = []
        for child in ast.walk(node):
            if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
                calls.append(child.func.id)

        # Get arguments
        args = [arg.arg for arg in node.args.args]

        return FunctionInfo(
            name=node.name,
            start_line=node.lineno,
            end_line=getattr(node, 'end_lineno', node.lineno),
            line_count=getattr(node, 'end_lineno', node.lineno) - node.lineno + 1,
            complexity=complexity_analyzer.complexity,
            args=args,
            docstring=ast.get_docstring(node),
            calls=calls
        )

    def _find_duplicate_patterns(self, content: str) -> List[Dict[str, Any]]:
        """Find duplicate code patterns."""
        lines = content.splitlines()
        duplicates = []

        # Simple duplicate detection (3+ identical lines)
        for i in range(len(lines) - 2):
            pattern = []
            for j in range(i, min(i + 10, len(lines))):
                stripped = lines[j].strip()
                if stripped and not stripped.startswith('#'):
                    pattern.append(stripped)
                else:
                    break

            if len(pattern) >= 3:
                # Look for this pattern elsewhere
                pattern_str = '\n'.join(pattern)
                for k in range(i + len(pattern), len(lines) - len(pattern)):
                    candidate = []
                    for l in range(k, min(k + len(pattern), len(lines))):
                        stripped = lines[l].strip()
                        if stripped and not stripped.startswith('#'):
                            candidate.append(stripped)
                        else:
                            break

                    if len(candidate) == len(pattern) and '\n'.join(candidate) == pattern_str:
                        duplicates.append({
                            'line': i + 1,
                            'pattern': pattern_str,
                            'duplicate_at': k + 1
                        })
                        break

        return duplicates

    def _calculate_nesting_depth(self, node: ast.AST, current_depth: int = 0) -> int:
        """Calculate maximum nesting depth."""
        max_depth = current_depth

        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                depth = self._calculate_nesting_depth(child, current_depth + 1)
                max_depth = max(max_depth, depth)

        return max_depth

    def _to_snake_case(self, name: str) -> str:
        """Convert name to snake_case."""
        # Insert underscore before uppercase letters
        s1 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name)
        return s1.lower()

    def _to_pascal_case(self, name: str) -> str:
        """Convert name to PascalCase."""
        components = name.split('_')
        return ''.join(word.capitalize() for word in components)
