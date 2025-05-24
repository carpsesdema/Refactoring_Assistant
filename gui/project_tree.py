"""
Project tree widget for browsing PyCharm projects
"""

import os
from typing import List, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem, QMenu, QMessageBox


class ProjectTreeWidget(QTreeWidget):
    """Tree widget for displaying project structure."""

    file_selected = Signal(str)  # file_path
    folder_selected = Signal(str)  # folder_path

    def __init__(self):
        super().__init__()
        self.project_path = None
        self.python_files = []
        self.init_tree()

    def init_tree(self):
        """Initialize the tree widget."""
        # Set headers
        self.setHeaderLabels(["Files"])

        # Hide header
        self.header().setVisible(False)

        # Set style
        self.setStyleSheet("""
            QTreeWidget {
                background-color: #252526;
                color: #cccccc;
                border: 1px solid #3e3e3e;
                outline: none;
            }
            QTreeWidget::item {
                padding: 2px;
                border: none;
            }
            QTreeWidget::item:selected {
                background-color: #094771;
                color: white;
            }
            QTreeWidget::item:hover {
                background-color: #2a2a2a;
            }
            QTreeWidget::branch:closed:has-children {
                image: url(none);
                border-image: none;
            }
            QTreeWidget::branch:open:has-children {
                image: url(none);
                border-image: none;
            }
        """)

        # Connect signals
        self.itemClicked.connect(self.on_item_clicked)
        self.itemDoubleClicked.connect(self.on_item_double_clicked)

        # Enable context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def load_project(self, project_path: str):
        """Load a PyCharm project."""
        self.clear()
        self.project_path = project_path

        try:
            if not os.path.exists(project_path):
                self._show_error("Project path does not exist")
                return

            # Check if it's a valid project directory
            if not self._is_valid_project(project_path):
                reply = QMessageBox.question(
                    self, "Load Directory",
                    "This doesn't appear to be a PyCharm project. Load as regular directory?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply != QMessageBox.Yes:
                    return

            # Load project structure
            self._load_directory_structure(project_path)

            # Expand root
            if self.topLevelItemCount() > 0:
                self.topLevelItem(0).setExpanded(True)

        except Exception as e:
            self._show_error(f"Failed to load project: {str(e)}")

    def _is_valid_project(self, path: str) -> bool:
        """Check if directory is a valid PyCharm project."""
        project_indicators = [
            ".idea",  # PyCharm project folder
            "requirements.txt",
            "setup.py",
            "pyproject.toml",
            "__pycache__",
            ".git"
        ]

        for indicator in project_indicators:
            if os.path.exists(os.path.join(path, indicator)):
                return True

        # Check if it contains Python files
        for root, dirs, files in os.walk(path):
            if any(f.endswith('.py') for f in files):
                return True

        return False

    def _load_directory_structure(self, path: str):
        """Load directory structure into tree."""
        self.python_files = []

        root_item = QTreeWidgetItem([os.path.basename(path)])
        root_item.setData(0, Qt.UserRole, {"type": "folder", "path": path})
        root_item.setFont(0, QFont("", -1, QFont.Bold))
        root_item.setForeground(0, QColor("#569cd6"))

        self.addTopLevelItem(root_item)

        self._populate_directory(root_item, path)

    def _populate_directory(self, parent_item: QTreeWidgetItem, dir_path: str):
        """Recursively populate directory structure."""
        try:
            entries = list(os.listdir(dir_path))
            entries.sort(key=lambda x: (not os.path.isdir(os.path.join(dir_path, x)), x.lower()))

            for entry in entries:
                full_path = os.path.join(dir_path, entry)

                # Skip hidden files and common non-essential directories
                if entry.startswith('.') and entry not in ['.idea']:
                    continue

                if entry in ['__pycache__', 'node_modules', '.git', 'venv', 'env']:
                    continue

                if os.path.isdir(full_path):
                    # Directory
                    dir_item = QTreeWidgetItem([entry])
                    dir_item.setData(0, Qt.UserRole, {"type": "folder", "path": full_path})
                    dir_item.setForeground(0, QColor("#dcaa7c"))

                    parent_item.addChild(dir_item)

                    # Recursively populate subdirectory (limit depth)
                    depth = full_path.count(os.sep) - self.project_path.count(os.sep)
                    if depth < 5:  # Limit recursion depth
                        self._populate_directory(dir_item, full_path)

                elif entry.endswith('.py'):
                    # Python file
                    file_item = QTreeWidgetItem([entry])
                    file_item.setData(0, Qt.UserRole, {"type": "file", "path": full_path})
                    file_item.setForeground(0, QColor("#4fc1ff"))

                    # Add file size info
                    try:
                        size = os.path.getsize(full_path)
                        lines = self._count_lines(full_path)

                        if lines > 500:
                            file_item.setForeground(0, QColor("#f44747"))  # Red for large files
                        elif lines > 200:
                            file_item.setForeground(0, QColor("#ff8c00"))  # Orange for medium files

                        file_item.setToolTip(0, f"Lines: {lines}, Size: {size} bytes")

                    except Exception:
                        pass

                    parent_item.addChild(file_item)
                    self.python_files.append(full_path)

                elif entry.endswith(('.txt', '.md', '.json', '.yml', '.yaml', '.toml', '.cfg', '.ini')):
                    # Configuration/documentation files
                    file_item = QTreeWidgetItem([entry])
                    file_item.setData(0, Qt.UserRole, {"type": "file", "path": full_path})
                    file_item.setForeground(0, QColor("#6a9955"))

                    parent_item.addChild(file_item)

        except PermissionError:
            # Skip directories we can't read
            pass

    def _count_lines(self, file_path: str) -> int:
        """Count lines in a file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return sum(1 for _ in f)
        except Exception:
            return 0

    def on_item_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle item click."""
        data = item.data(0, Qt.UserRole)
        if data:
            if data["type"] == "file":
                self.file_selected.emit(data["path"])
            elif data["type"] == "folder":
                self.folder_selected.emit(data["path"])

    def on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle item double click."""
        data = item.data(0, Qt.UserRole)
        if data and data["type"] == "file":
            self.file_selected.emit(data["path"])

    def show_context_menu(self, position):
        """Show context menu for tree items."""
        item = self.itemAt(position)
        if not item:
            return

        data = item.data(0, Qt.UserRole)
        if not data:
            return

        menu = QMenu(self)

        if data["type"] == "file":
            # File actions
            open_action = menu.addAction("Open File")
            open_action.triggered.connect(
                lambda: self.file_selected.emit(data["path"])
            )

            if data["path"].endswith('.py'):
                menu.addSeparator()

                analyze_action = menu.addAction("Analyze File")
                analyze_action.triggered.connect(
                    lambda: self._analyze_file(data["path"])
                )

                refactor_action = menu.addAction("Auto-Refactor")
                refactor_action.triggered.connect(
                    lambda: self._refactor_file(data["path"])
                )

        elif data["type"] == "folder":
            # Folder actions
            expand_action = menu.addAction("Expand All")
            expand_action.triggered.connect(
                lambda: self._expand_all_children(item)
            )

            collapse_action = menu.addAction("Collapse All")
            collapse_action.triggered.connect(
                lambda: self._collapse_all_children(item)
            )

            menu.addSeparator()

            analyze_folder_action = menu.addAction("Analyze All Python Files")
            analyze_folder_action.triggered.connect(
                lambda: self._analyze_folder(data["path"])
            )

        # Common actions
        menu.addSeparator()

        copy_path_action = menu.addAction("Copy Path")
        copy_path_action.triggered.connect(
            lambda: self._copy_to_clipboard(data["path"])
        )

        menu.exec(self.mapToGlobal(position))

    def _expand_all_children(self, item: QTreeWidgetItem):
        """Expand all children of an item."""
        item.setExpanded(True)
        for i in range(item.childCount()):
            self._expand_all_children(item.child(i))

    def _collapse_all_children(self, item: QTreeWidgetItem):
        """Collapse all children of an item."""
        item.setExpanded(False)
        for i in range(item.childCount()):
            self._collapse_all_children(item.child(i))

    def _analyze_file(self, file_path: str):
        """Analyze a specific file."""
        # This would trigger analysis in the main window
        self.file_selected.emit(file_path)

    def _refactor_file(self, file_path: str):
        """Refactor a specific file."""
        # This would trigger refactoring in the main window
        reply = QMessageBox.question(
            self, "Refactor File",
            f"Auto-refactor {os.path.basename(file_path)}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # Signal main window to refactor this file
            pass

    def _analyze_folder(self, folder_path: str):
        """Analyze all Python files in a folder."""
        python_files = []
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))

        if python_files:
            QMessageBox.information(
                self, "Folder Analysis",
                f"Found {len(python_files)} Python files to analyze.\n"
                f"This feature would analyze all files in batch."
            )
        else:
            QMessageBox.information(
                self, "Folder Analysis",
                "No Python files found in this folder."
            )

    def _copy_to_clipboard(self, text: str):
        """Copy text to clipboard."""
        from PySide6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(text)

    def _show_error(self, message: str):
        """Show error message."""
        QMessageBox.warning(self, "Error", message)

    def get_python_files(self) -> List[str]:
        """Get list of all Python files in the project."""
        return self.python_files.copy()

    def get_selected_path(self) -> Optional[str]:
        """Get path of currently selected item."""
        current_item = self.currentItem()
        if current_item:
            data = current_item.data(0, Qt.UserRole)
            if data:
                return data["path"]
        return None

    def refresh_project(self):
        """Refresh the current project."""
        if self.project_path:
            self.load_project(self.project_path)

    def find_large_files(self, min_lines: int = 200) -> List[str]:
        """Find Python files larger than specified line count."""
        large_files = []
        for file_path in self.python_files:
            lines = self._count_lines(file_path)
            if lines >= min_lines:
                large_files.append((file_path, lines))

        return sorted(large_files, key=lambda x: x[1], reverse=True)
