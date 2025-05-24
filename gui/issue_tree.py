"""
Issue tree widget for displaying code analysis results
"""

from typing import List, Dict, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem, QHeaderView, QMenu

from core.code_analyzer import CodeIssue


class IssueTreeWidget(QTreeWidget):
    """Tree widget for displaying code issues."""

    issue_selected = Signal(int, int)  # line, column
    issue_fix_requested = Signal(object)  # CodeIssue

    def __init__(self):
        super().__init__()
        self.issues = []
        self.init_tree()

    def init_tree(self):
        """Initialize the tree widget."""
        # Set headers
        self.setHeaderLabels(["Issue", "Line", "Type", "Severity"])

        # Configure columns
        header = self.header()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)

        # Set style
        self.setStyleSheet("""
            QTreeWidget {
                background-color: #252526;
                color: #cccccc;
                border: 1px solid #3e3e3e;
                alternate-background-color: #2a2a2a;
            }
            QTreeWidget::item:selected {
                background-color: #094771;
            }
            QTreeWidget::item:hover {
                background-color: #2a2a2a;
            }
        """)

        # Enable alternating row colors
        self.setAlternatingRowColors(True)

        # Connect signals
        self.itemClicked.connect(self.on_item_clicked)
        self.itemDoubleClicked.connect(self.on_item_double_clicked)

        # Enable context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def update_issues(self, issues: List[CodeIssue]):
        """Update the tree with new issues."""
        self.clear()
        self.issues = issues

        if not issues:
            # Show "no issues" message
            item = QTreeWidgetItem(["No issues found", "", "", ""])
            item.setForeground(0, QColor("#6a9955"))  # Green
            self.addTopLevelItem(item)
            return

        # Group issues by type
        grouped_issues = self._group_issues_by_type(issues)

        for issue_type, type_issues in grouped_issues.items():
            # Create parent item for issue type
            parent_item = QTreeWidgetItem([
                f"{issue_type.replace('_', ' ').title()} ({len(type_issues)})",
                "", "", ""
            ])
            parent_item.setFont(0, QFont("", -1, QFont.Bold))

            # Set parent color based on most severe issue in group
            severity_color = self._get_severity_color(
                max(issue.severity for issue in type_issues)
            )
            parent_item.setForeground(0, severity_color)

            self.addTopLevelItem(parent_item)

            # Add child items for each issue
            for issue in type_issues:
                child_item = QTreeWidgetItem([
                    issue.message,
                    str(issue.line),
                    issue.type.replace('_', ' ').title(),
                    issue.severity.title()
                ])

                # Set colors based on severity
                severity_color = self._get_severity_color(issue.severity)
                child_item.setForeground(3, severity_color)

                # Store issue data
                child_item.setData(0, Qt.UserRole, issue)

                # Add suggestion as tooltip if available
                if issue.suggestion:
                    child_item.setToolTip(0, f"Suggestion: {issue.suggestion}")

                parent_item.addChild(child_item)

        # Expand all items
        self.expandAll()

    def _group_issues_by_type(self, issues: List[CodeIssue]) -> Dict[str, List[CodeIssue]]:
        """Group issues by their type."""
        grouped = {}
        for issue in issues:
            if issue.type not in grouped:
                grouped[issue.type] = []
            grouped[issue.type].append(issue)

        # Sort each group by line number
        for issue_type in grouped:
            grouped[issue_type].sort(key=lambda x: x.line)

        return grouped

    def _get_severity_color(self, severity: str) -> QColor:
        """Get color for severity level."""
        if severity == "error":
            return QColor("#f44747")  # Red
        elif severity == "warning":
            return QColor("#ff8c00")  # Orange
        else:  # suggestion
            return QColor("#4fc1ff")  # Blue

    def on_item_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle item click."""
        issue = item.data(0, Qt.UserRole)
        if isinstance(issue, CodeIssue):
            self.issue_selected.emit(issue.line, issue.column)

    def on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle item double click."""
        issue = item.data(0, Qt.UserRole)
        if isinstance(issue, CodeIssue) and issue.auto_fixable:
            self.issue_fix_requested.emit(issue)

    def show_context_menu(self, position):
        """Show context menu for tree items."""
        item = self.itemAt(position)
        if not item:
            return

        issue = item.data(0, Qt.UserRole)
        if not isinstance(issue, CodeIssue):
            return

        menu = QMenu(self)

        # Jump to issue action
        jump_action = menu.addAction("Jump to Issue")
        jump_action.triggered.connect(
            lambda: self.issue_selected.emit(issue.line, issue.column)
        )

        # Fix action (if auto-fixable)
        if issue.auto_fixable:
            fix_action = menu.addAction("Apply Auto-Fix")
            fix_action.triggered.connect(
                lambda: self.issue_fix_requested.emit(issue)
            )

        # Copy message action
        copy_action = menu.addAction("Copy Message")
        copy_action.triggered.connect(
            lambda: self._copy_to_clipboard(issue.message)
        )

        # Show suggestion action
        if issue.suggestion:
            suggestion_action = menu.addAction("Show Suggestion")
            suggestion_action.triggered.connect(
                lambda: self._show_suggestion(issue)
            )

        menu.exec(self.mapToGlobal(position))

    def _copy_to_clipboard(self, text: str):
        """Copy text to clipboard."""
        from PySide6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(text)

    def _show_suggestion(self, issue: CodeIssue):
        """Show issue suggestion in a message box."""
        from PySide6.QtWidgets import QMessageBox

        msg = QMessageBox(self)
        msg.setWindowTitle("Suggestion")
        msg.setText(f"Issue: {issue.message}")
        msg.setInformativeText(f"Suggestion: {issue.suggestion}")
        msg.setIcon(QMessageBox.Information)
        msg.exec()

    def get_selected_issue(self) -> Optional[CodeIssue]:
        """Get currently selected issue."""
        current_item = self.currentItem()
        if current_item:
            issue = current_item.data(0, Qt.UserRole)
            if isinstance(issue, CodeIssue):
                return issue
        return None

    def clear_issues(self):
        """Clear all issues."""
        self.clear()
        self.issues = []

    def get_issue_count_by_severity(self) -> Dict[str, int]:
        """Get count of issues by severity."""
        counts = {"error": 0, "warning": 0, "suggestion": 0}
        for issue in self.issues:
            if issue.severity in counts:
                counts[issue.severity] += 1
        return counts

    def filter_by_severity(self, severities: List[str]):
        """Filter issues by severity levels."""
        filtered_issues = [
            issue for issue in self.issues
            if issue.severity in severities
        ]
        self.update_issues(filtered_issues)

    def filter_by_type(self, issue_types: List[str]):
        """Filter issues by type."""
        filtered_issues = [
            issue for issue in self.issues
            if issue.type in issue_types
        ]
        self.update_issues(filtered_issues)
