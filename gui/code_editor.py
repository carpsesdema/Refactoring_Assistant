"""
Advanced code editor widget with syntax highlighting and issue highlighting
"""

import re
from typing import List

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import (
    QFont, QTextCursor, QSyntaxHighlighter, QTextCharFormat,
    QColor, QPainter
)
from PySide6.QtWidgets import QTextEdit, QWidget

from core.code_analyzer import CodeIssue


class LineNumberArea(QWidget):
    """Widget for displaying line numbers."""

    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return self.editor.line_number_area_width()

    def paintEvent(self, event):
        self.editor.line_number_area_paint_event(event)


class PythonSyntaxHighlighter(QSyntaxHighlighter):
    """Enhanced Python syntax highlighter for dark theme."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlighting_rules = []

        # Keywords
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#569cd6"))
        keyword_format.setFontWeight(QFont.Bold)
        keywords = [
            "and", "as", "assert", "break", "class", "continue", "def",
            "del", "elif", "else", "except", "exec", "finally", "for",
            "from", "global", "if", "import", "in", "is", "lambda",
            "not", "or", "pass", "print", "raise", "return", "try",
            "while", "with", "yield", "async", "await", "nonlocal"
        ]
        for word in keywords:
            pattern = f"\\b{word}\\b"
            self.highlighting_rules.append((re.compile(pattern), keyword_format))

        # Built-in functions
        builtin_format = QTextCharFormat()
        builtin_format.setForeground(QColor("#dcdcaa"))
        builtins = [
            "abs", "all", "any", "bin", "bool", "callable", "chr", "classmethod",
            "compile", "complex", "delattr", "dict", "dir", "divmod", "enumerate",
            "eval", "filter", "float", "format", "frozenset", "getattr", "globals",
            "hasattr", "hash", "help", "hex", "id", "input", "int", "isinstance",
            "issubclass", "iter", "len", "list", "locals", "map", "max", "memoryview",
            "min", "next", "object", "oct", "open", "ord", "pow", "print", "property",
            "range", "repr", "reversed", "round", "set", "setattr", "slice", "sorted",
            "staticmethod", "str", "sum", "super", "tuple", "type", "vars", "zip"
        ]
        for word in builtins:
            pattern = f"\\b{word}\\b"
            self.highlighting_rules.append((re.compile(pattern), builtin_format))

        # Strings
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#ce9178"))
        self.highlighting_rules.append((re.compile(r'"([^"\\\\]|\\\\.)*"'), string_format))
        self.highlighting_rules.append((re.compile(r"'([^'\\\\]|\\\\.)*'"), string_format))
        self.highlighting_rules.append((re.compile(r'"""(.|\n)*?"""'), string_format))
        self.highlighting_rules.append((re.compile(r"'''(.|\n)*?'''"), string_format))

        # Comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6a9955"))
        self.highlighting_rules.append((re.compile(r"#.*$", re.MULTILINE), comment_format))

        # Numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#b5cea8"))
        self.highlighting_rules.append((re.compile(r"\b\d+\.?\d*\b"), number_format))

        # Decorators
        decorator_format = QTextCharFormat()
        decorator_format.setForeground(QColor("#4ec9b0"))
        self.highlighting_rules.append((re.compile(r"@\w+"), decorator_format))

        # Function/class definitions
        definition_format = QTextCharFormat()
        definition_format.setForeground(QColor("#dcdcaa"))
        definition_format.setFontWeight(QFont.Bold)
        self.highlighting_rules.append((re.compile(r"\b(def|class)\s+(\w+)"), definition_format))

    def highlightBlock(self, text):
        for pattern, format in self.highlighting_rules:
            for match in pattern.finditer(text):
                start = match.start()
                length = match.end() - start
                self.setFormat(start, length, format)


class CodeEditor(QTextEdit):
    """Advanced code editor with line numbers and issue highlighting."""

    line_clicked = Signal(int)

    def __init__(self):
        super().__init__()
        self.current_file = None
        self.issues = []

        self.init_editor()
        self.setup_line_numbers()

    def init_editor(self):
        """Initialize the editor."""
        # Set font
        font = QFont("Consolas", 10)
        font.setFixedPitch(True)
        self.setFont(font)

        # Set dark theme colors
        self.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #3e3e3e;
                selection-background-color: #264f78;
            }
        """)

        # Enable syntax highlighting
        self.highlighter = PythonSyntaxHighlighter(self.document())

        # Connect signals
        self.textChanged.connect(self.on_text_changed)
        self.cursorPositionChanged.connect(self.on_cursor_changed)

    def setup_line_numbers(self):
        """Setup line number area."""
        self.line_number_area = LineNumberArea(self)

        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)

        self.update_line_number_area_width(0)

    def line_number_area_width(self):
        """Calculate width needed for line numbers."""
        digits = len(str(max(1, self.blockCount())))
        space = 3 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def update_line_number_area_width(self, newBlockCount):
        """Update line number area width."""
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        """Update line number area."""
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(),
                                         self.line_number_area.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        """Handle resize event."""
        super().resizeEvent(event)

        cr = self.contentsRect()
        self.line_number_area.setGeometry(
            cr.left(), cr.top(), self.line_number_area_width(), cr.height()
        )

    def line_number_area_paint_event(self, event):
        """Paint line numbers."""
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor("#2d2d30"))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        height = self.fontMetrics().height()

        while block.isValid() and (top <= event.rect().bottom()):
            if block.isVisible() and (bottom >= event.rect().top()):
                number = str(block_number + 1)

                # Check if this line has an issue
                line_has_issue = any(issue.line == block_number + 1 for issue in self.issues)

                if line_has_issue:
                    painter.setPen(QColor("#f44747"))  # Red for issues
                else:
                    painter.setPen(QColor("#858585"))  # Gray for normal

                painter.drawText(0, int(top), self.line_number_area.width() - 3, height,
                                 Qt.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1

    def highlight_issues(self, issues: List[CodeIssue]):
        """Highlight issues in the code."""
        self.issues = issues

        # Clear previous highlights
        cursor = QTextCursor(self.document())
        cursor.select(QTextCursor.Document)

        # Apply issue highlights
        for issue in issues:
            self.highlight_line(issue.line - 1, issue.severity)  # Convert to 0-based

        # Update line number area to show issue indicators
        self.line_number_area.update()

    def highlight_line(self, line_number: int, severity: str):
        """Highlight a specific line based on issue severity."""
        if line_number < 0:
            return

        block = self.document().findBlockByLineNumber(line_number)
        if not block.isValid():
            return

        cursor = QTextCursor(block)
        cursor.select(QTextCursor.LineUnderCursor)

        # Create format based on severity
        format = QTextCharFormat()
        if severity == "error":
            format.setBackground(QColor("#3d1a1a"))  # Dark red
        elif severity == "warning":
            format.setBackground(QColor("#3d3d1a"))  # Dark yellow
        else:  # suggestion
            format.setBackground(QColor("#1a1a3d"))  # Dark blue

        # Apply format (this is simplified - in practice you'd want to use QTextEdit's extra selections)

    def jump_to_line(self, line: int, column: int = 0):
        """Jump to a specific line and column."""
        if line <= 0:
            return

        block = self.document().findBlockByLineNumber(line - 1)  # Convert to 0-based
        if block.isValid():
            cursor = QTextCursor(block)
            cursor.movePosition(QTextCursor.Right, QTextCursor.MoveAnchor, column)
            self.setTextCursor(cursor)
            self.centerCursor()

    def on_text_changed(self):
        """Handle text changes."""
        # Clear issues when text changes (they may no longer be valid)
        if self.issues:
            self.issues = []
            self.line_number_area.update()

    def on_cursor_changed(self):
        """Handle cursor position changes."""
        cursor = self.textCursor()
        line = cursor.blockNumber() + 1
        column = cursor.columnNumber()

        # Emit signal for status bar updates
        self.line_clicked.emit(line)

    def get_current_line_column(self) -> tuple:
        """Get current cursor position."""
        cursor = self.textCursor()
        return cursor.blockNumber() + 1, cursor.columnNumber()

    def insert_text_at_line(self, line: int, text: str):
        """Insert text at a specific line."""
        block = self.document().findBlockByLineNumber(line - 1)
        if block.isValid():
            cursor = QTextCursor(block)
            cursor.movePosition(QTextCursor.EndOfBlock)
            cursor.insertText('\n' + text)

    def get_line_text(self, line: int) -> str:
        """Get text of a specific line."""
        block = self.document().findBlockByLineNumber(line - 1)
        if block.isValid():
            return block.text()
        return ""

    def replace_line_text(self, line: int, new_text: str):
        """Replace text of a specific line."""
        block = self.document().findBlockByLineNumber(line - 1)
        if block.isValid():
            cursor = QTextCursor(block)
            cursor.select(QTextCursor.LineUnderCursor)
            cursor.insertText(new_text)
