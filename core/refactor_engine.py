"""
Code refactoring engine that applies automatic fixes
"""

import ast
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

from .code_analyzer import CodeAnalyzer


class RefactorEngine:
    """Engine for applying automatic code refactoring."""

    def __init__(self):
        self.analyzer = CodeAnalyzer()

    def auto_fix_file(self, file_path: str, options: Dict[str, Any]) -> Optional[str]:
        """Apply automatic fixes to a file and return the fixed content."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()

            content = original_content

            # Apply fixes in order of safety
            content = self._fix_trailing_whitespace(content)
            content = self._fix_multiple_blank_lines(content)
            content = self._fix_import_order(content)

            if options.get('add_docstrings', False):
                content = self._add_missing_docstrings(content)

            if options.get('split_large_files', False):
                content = self._handle_large_file_splitting(content, file_path, options)

            # Only return content if changes were made
            return content if content != original_content else None

        except Exception as e:
            print(f"Error during auto-fix: {e}")
            return None

    def split_large_file(self, file_path: str, options: Dict[str, Any]) -> List[str]:
        """Split a large file into smaller modules."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)

            # Analyze the structure
            classes = []
            functions = []
            imports = []
            module_vars = []

            for node in ast.iter_child_nodes(tree):
                if isinstance(node, ast.ClassDef):
                    classes.append(node)
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    functions.append(node)
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    imports.append(node)
                elif isinstance(node, ast.Assign):
                    module_vars.append(node)

            # Create split strategy
            split_files = self._create_split_strategy(
                file_path, classes, functions, imports, module_vars, content
            )

            return split_files

        except Exception as e:
            print(f"Error during file splitting: {e}")
            return []

    def _fix_trailing_whitespace(self, content: str) -> str:
        """Remove trailing whitespace from all lines."""
        lines = content.splitlines()
        fixed_lines = [line.rstrip() for line in lines]
        return '\n'.join(fixed_lines)

    def _fix_multiple_blank_lines(self, content: str) -> str:
        """Replace multiple consecutive blank lines with single blank lines."""
        # Replace 3+ consecutive newlines with 2 newlines
        return re.sub(r'\n\s*\n\s*\n+', '\n\n', content)

    def _fix_import_order(self, content: str) -> str:
        """Organize imports according to PEP 8."""
        try:
            tree = ast.parse(content)
            lines = content.splitlines()

            # Find all imports and their line numbers
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    imports.append((node.lineno - 1, node))  # Convert to 0-based

            if not imports:
                return content

            # Sort imports by line number
            imports.sort(key=lambda x: x[0])

            # Categorize imports
            stdlib_imports = []
            third_party_imports = []
            local_imports = []

            standard_libs = {
                'os', 'sys', 'json', 'datetime', 're', 'collections', 'typing',
                'pathlib', 'itertools', 'functools', 'operator', 'copy',
                'math', 'random', 'string', 'time', 'urllib', 'http',
                'email', 'html', 'xml', 'csv', 'sqlite3', 'pickle',
                'logging', 'unittest', 'argparse', 'configparser'
            }

            for line_num, node in imports:
                import_line = lines[line_num]

                if isinstance(node, ast.Import):
                    module_name = node.names[0].name.split('.')[0]
                    if module_name in standard_libs:
                        stdlib_imports.append(import_line)
                    else:
                        third_party_imports.append(import_line)
                elif isinstance(node, ast.ImportFrom):
                    if node.level > 0:  # Relative import
                        local_imports.append(import_line)
                    elif node.module:
                        module_name = node.module.split('.')[0]
                        if module_name in standard_libs:
                            stdlib_imports.append(import_line)
                        else:
                            third_party_imports.append(import_line)
                    else:
                        local_imports.append(import_line)

            # Remove duplicates while preserving order
            def remove_duplicates(lst):
                seen = set()
                result = []
                for item in lst:
                    if item not in seen:
                        seen.add(item)
                        result.append(item)
                return result

            stdlib_imports = remove_duplicates(sorted(stdlib_imports))
            third_party_imports = remove_duplicates(sorted(third_party_imports))
            local_imports = remove_duplicates(sorted(local_imports))

            # Build new import section
            new_imports = []
            if stdlib_imports:
                new_imports.extend(stdlib_imports)
                new_imports.append('')
            if third_party_imports:
                new_imports.extend(third_party_imports)
                new_imports.append('')
            if local_imports:
                new_imports.extend(local_imports)
                new_imports.append('')

            # Remove trailing empty line if no code follows
            if new_imports and new_imports[-1] == '':
                new_imports.pop()

            # Find the range of lines to replace
            first_import_line = imports[0][0]
            last_import_line = imports[-1][0]

            # Find the end of the import block (including any trailing blank lines)
            end_line = last_import_line
            while (end_line + 1 < len(lines) and
                   (not lines[end_line + 1].strip() or
                    lines[end_line + 1].strip().startswith('#'))):
                end_line += 1

            # Replace the import section
            new_lines = (
                    lines[:first_import_line] +
                    new_imports +
                    lines[end_line + 1:]
            )

            return '\n'.join(new_lines)

        except Exception:
            return content  # Return original on error

    def _add_missing_docstrings(self, content: str) -> str:
        """Add basic docstrings to functions and classes missing them."""
        try:
            tree = ast.parse(content)
            lines = content.splitlines()

            # Find functions and classes without docstrings
            additions = []

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    if not ast.get_docstring(node):
                        # Generate basic docstring
                        if isinstance(node, ast.ClassDef):
                            docstring = f'"""A {node.name} class."""'
                        else:
                            docstring = f'"""Execute {node.name} operation."""'

                        # Find insertion point (after function/class definition)
                        insert_line = node.lineno  # Line after def/class
                        indent = self._get_line_indent(lines[node.lineno - 1]) + "    "

                        additions.append((insert_line, f'{indent}{docstring}'))

            # Sort by line number in reverse order to maintain line numbers
            additions.sort(key=lambda x: x[0], reverse=True)

            # Apply additions
            for line_num, docstring_line in additions:
                lines.insert(line_num, docstring_line)

            return '\n'.join(lines)

        except Exception:
            return content

    def _handle_large_file_splitting(self, content: str, file_path: str, options: Dict[str, Any]) -> str:
        """Handle large files by suggesting or creating splits."""
        lines = content.splitlines()

        if len(lines) > 500 and options.get('split_large_files', False):
            # For now, just add a comment suggesting the split
            # In a full implementation, this would create the actual split files
            suggestion_comment = [
                "# TODO: This file is large ({} lines). Consider splitting into:".format(len(lines)),
                "# - Separate modules for classes",
                "# - Utility functions in utils.py",
                "# - Constants in constants.py",
                "# - Main logic in main.py",
                ""
            ]

            # Add suggestion at the top after imports
            tree = ast.parse(content)
            import_end_line = 0

            for node in ast.iter_child_nodes(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    import_end_line = max(import_end_line, node.lineno)
                else:
                    break

            # Insert suggestion after imports
            insert_pos = import_end_line
            for i, comment in enumerate(suggestion_comment):
                lines.insert(insert_pos + i, comment)

            return '\n'.join(lines)

        return content

    def _create_split_strategy(self, file_path: str, classes: List[ast.ClassDef],
                               functions: List[ast.FunctionDef], imports: List[ast.AST],
                               module_vars: List[ast.AST], content: str) -> List[str]:
        """Create a strategy for splitting a large file."""
        base_path = Path(file_path).parent
        base_name = Path(file_path).stem

        split_files = []

        # Create utils file for standalone functions
        if functions:
            utils_content = self._create_utils_file(functions, imports, content)
            utils_path = base_path / f"{base_name}_utils.py"
            split_files.append(str(utils_path))

        # Create separate files for large classes
        for cls in classes:
            if self._get_class_line_count(cls, content) > 100:
                class_content = self._create_class_file(cls, imports, content)
                class_path = base_path / f"{base_name}_{cls.name.lower()}.py"
                split_files.append(str(class_path))

        # Create constants file for module-level variables
        if module_vars:
            constants_content = self._create_constants_file(module_vars, content)
            constants_path = base_path / f"{base_name}_constants.py"
            split_files.append(str(constants_path))

        return split_files

    def _create_utils_file(self, functions: List[ast.FunctionDef],
                           imports: List[ast.AST], content: str) -> str:
        """Create a utils file with standalone functions."""
        lines = content.splitlines()

        # Start with imports
        utils_lines = ['"""Utility functions."""', '']

        # Add necessary imports
        for imp in imports:
            utils_lines.append(lines[imp.lineno - 1])

        utils_lines.append('')

        # Add functions
        for func in functions:
            start_line = func.lineno - 1
            end_line = getattr(func, 'end_lineno', func.lineno) - 1

            for i in range(start_line, end_line + 1):
                if i < len(lines):
                    utils_lines.append(lines[i])

            utils_lines.append('')  # Blank line between functions

        return '\n'.join(utils_lines)

    def _create_class_file(self, cls: ast.ClassDef, imports: List[ast.AST], content: str) -> str:
        """Create a separate file for a class."""
        lines = content.splitlines()

        class_lines = [f'"""{cls.name} class module."""', '']

        # Add imports
        for imp in imports:
            class_lines.append(lines[imp.lineno - 1])

        class_lines.append('')

        # Add the class
        start_line = cls.lineno - 1
        end_line = getattr(cls, 'end_lineno', cls.lineno) - 1

        for i in range(start_line, end_line + 1):
            if i < len(lines):
                class_lines.append(lines[i])

        return '\n'.join(class_lines)

    def _create_constants_file(self, module_vars: List[ast.AST], content: str) -> str:
        """Create a constants file."""
        lines = content.splitlines()

        constants_lines = ['"""Module constants."""', '']

        for var in module_vars:
            constants_lines.append(lines[var.lineno - 1])

        return '\n'.join(constants_lines)

    def _get_line_indent(self, line: str) -> str:
        """Get the indentation of a line."""
        return line[:len(line) - len(line.lstrip())]

    def _get_class_line_count(self, cls: ast.ClassDef, content: str) -> int:
        """Get the line count of a class."""
        if hasattr(cls, 'end_lineno'):
            return cls.end_lineno - cls.lineno + 1
        else:
            # Fallback: estimate based on content
            return 50  # Default assumption
