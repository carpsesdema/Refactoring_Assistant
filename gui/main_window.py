"""
Main window for the PyRefactor application
"""

from pathlib import Path

from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QSplitter,
    QPushButton, QFileDialog,
    QLabel, QProgressBar, QGroupBox, QCheckBox, QSpinBox,
    QMessageBox, QToolBar, QStatusBar
)

from core.code_analyzer import CodeAnalyzer
from core.refactor_engine import RefactorEngine
from gui.code_editor import CodeEditor
from gui.issue_tree import IssueTreeWidget
from gui.project_tree import ProjectTreeWidget


class AnalysisWorker(QThread):
    """Background worker for code analysis to keep UI responsive."""

    analysis_complete = Signal(dict)
    progress_update = Signal(int, str)

    def __init__(self, file_path: str, analyzer: CodeAnalyzer):
        super().__init__()
        self.file_path = file_path
        self.analyzer = analyzer

    def run(self):
        """Run analysis in background thread."""
        try:
            self.progress_update.emit(25, "Parsing code structure...")
            issues = self.analyzer.analyze_file(self.file_path)

            self.progress_update.emit(50, "Analyzing complexity...")
            functions = self.analyzer.analyze_functions(self.file_path)

            self.progress_update.emit(75, "Generating suggestions...")
            suggestions = self.analyzer.get_refactor_suggestions(self.file_path)

            self.progress_update.emit(100, "Analysis complete!")

            result = {
                'issues': issues,
                'functions': functions,
                'suggestions': suggestions,
                'file_path': self.file_path
            }

            self.analysis_complete.emit(result)

        except Exception as e:
            self.progress_update.emit(0, f"Error: {str(e)}")


class RefactorMainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.current_project_path = None
        self.analyzer = CodeAnalyzer()
        self.refactor_engine = RefactorEngine()
        self.analysis_worker = None

        self.init_ui()
        self.setup_connections()

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("PyRefactor - Professional Python Code Refactoring Tool")
        self.setGeometry(100, 100, 1400, 900)

        # Create menu bar
        self.create_menu_bar()

        # Create toolbar
        self.create_toolbar()

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QHBoxLayout(central_widget)

        # Create main splitter
        main_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(main_splitter)

        # Left panel - Project and Issues
        left_panel = self.create_left_panel()
        main_splitter.addWidget(left_panel)

        # Center panel - Code editor
        center_panel = self.create_center_panel()
        main_splitter.addWidget(center_panel)

        # Right panel - Controls and settings
        right_panel = self.create_right_panel()
        main_splitter.addWidget(right_panel)

        # Set splitter proportions
        main_splitter.setSizes([300, 700, 300])

        # Create status bar
        self.create_status_bar()

    def create_menu_bar(self):
        """Create application menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        open_project_action = QAction("Open PyCharm Project", self)
        open_project_action.setShortcut("Ctrl+O")
        open_project_action.triggered.connect(self.open_project)
        file_menu.addAction(open_project_action)

        open_file_action = QAction("Open File", self)
        open_file_action.setShortcut("Ctrl+Shift+O")
        open_file_action.triggered.connect(self.open_file)
        file_menu.addAction(open_file_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Tools menu
        tools_menu = menubar.addMenu("Tools")

        analyze_action = QAction("Analyze Current File", self)
        analyze_action.setShortcut("F5")
        analyze_action.triggered.connect(self.analyze_current_file)
        tools_menu.addAction(analyze_action)

        auto_fix_action = QAction("Auto-Fix Issues", self)
        auto_fix_action.setShortcut("Ctrl+F")
        auto_fix_action.triggered.connect(self.auto_fix_issues)
        tools_menu.addAction(auto_fix_action)

    def create_toolbar(self):
        """Create application toolbar."""
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        # Open project button
        open_project_btn = QPushButton("Open Project")
        open_project_btn.clicked.connect(self.open_project)
        toolbar.addWidget(open_project_btn)

        toolbar.addSeparator()

        # Analyze button
        analyze_btn = QPushButton("Analyze")
        analyze_btn.clicked.connect(self.analyze_current_file)
        toolbar.addWidget(analyze_btn)

        # Auto-fix button
        auto_fix_btn = QPushButton("Auto-Fix")
        auto_fix_btn.clicked.connect(self.auto_fix_issues)
        toolbar.addWidget(auto_fix_btn)

    def create_left_panel(self):
        """Create left panel with project tree and issues."""
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # Project tree
        project_group = QGroupBox("Project Files")
        project_layout = QVBoxLayout(project_group)

        self.project_tree = ProjectTreeWidget()
        project_layout.addWidget(self.project_tree)

        left_layout.addWidget(project_group)

        # Issues tree
        issues_group = QGroupBox("Code Issues")
        issues_layout = QVBoxLayout(issues_group)

        self.issue_tree = IssueTreeWidget()
        issues_layout.addWidget(self.issue_tree)

        left_layout.addWidget(issues_group)

        return left_widget

    def create_center_panel(self):
        """Create center panel with code editor."""
        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)

        # File info label
        self.file_info_label = QLabel("No file selected")
        self.file_info_label.setStyleSheet("QLabel { color: #888; font-style: italic; }")
        center_layout.addWidget(self.file_info_label)

        # Code editor
        self.code_editor = CodeEditor()
        center_layout.addWidget(self.code_editor)

        return center_widget

    def create_right_panel(self):
        """Create right panel with controls and settings."""
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # Analysis settings
        settings_group = QGroupBox("Analysis Settings")
        settings_layout = QVBoxLayout(settings_group)

        self.check_complexity = QCheckBox("Check complexity (max lines per function)")
        self.check_complexity.setChecked(True)
        settings_layout.addWidget(self.check_complexity)

        self.max_function_lines = QSpinBox()
        self.max_function_lines.setRange(10, 200)
        self.max_function_lines.setValue(50)
        settings_layout.addWidget(self.max_function_lines)

        self.check_duplicates = QCheckBox("Find duplicate code")
        self.check_duplicates.setChecked(True)
        settings_layout.addWidget(self.check_duplicates)

        self.check_naming = QCheckBox("Check naming conventions")
        self.check_naming.setChecked(True)
        settings_layout.addWidget(self.check_naming)

        self.check_imports = QCheckBox("Organize imports")
        self.check_imports.setChecked(True)
        settings_layout.addWidget(self.check_imports)

        right_layout.addWidget(settings_group)

        # Refactoring options
        refactor_group = QGroupBox("Refactoring Options")
        refactor_layout = QVBoxLayout(refactor_group)

        self.split_large_files = QCheckBox("Auto-split large files")
        self.split_large_files.setChecked(True)
        refactor_layout.addWidget(self.split_large_files)

        self.extract_functions = QCheckBox("Extract repeated code to functions")
        self.extract_functions.setChecked(True)
        refactor_layout.addWidget(self.extract_functions)

        self.add_docstrings = QCheckBox("Add missing docstrings")
        self.add_docstrings.setChecked(False)
        refactor_layout.addWidget(self.add_docstrings)

        self.add_type_hints = QCheckBox("Add type hints")
        self.add_type_hints.setChecked(False)
        refactor_layout.addWidget(self.add_type_hints)

        right_layout.addWidget(refactor_group)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        right_layout.addWidget(self.progress_bar)

        # Stretch to push everything to top
        right_layout.addStretch()

        return right_widget

    def create_status_bar(self):
        """Create status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def setup_connections(self):
        """Setup signal connections."""
        self.project_tree.file_selected.connect(self.load_file)
        self.issue_tree.issue_selected.connect(self.jump_to_issue)

    def open_project(self):
        """Open a PyCharm project directory."""
        project_path = QFileDialog.getExistingDirectory(
            self, "Select PyCharm Project Directory"
        )

        if project_path:
            self.current_project_path = project_path
            self.project_tree.load_project(project_path)
            self.status_bar.showMessage(f"Loaded project: {project_path}")

    def open_file(self):
        """Open a single Python file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Python File", "", "Python Files (*.py);;All Files (*)"
        )

        if file_path:
            self.load_file(file_path)

    def load_file(self, file_path: str):
        """Load a file into the editor."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            self.code_editor.setPlainText(content)
            self.code_editor.current_file = file_path

            # Update file info
            file_info = f"File: {Path(file_path).name} | Lines: {len(content.splitlines())} | Size: {len(content)} chars"
            self.file_info_label.setText(file_info)

            # Auto-analyze if enabled
            QTimer.singleShot(500, self.analyze_current_file)

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not load file: {str(e)}")

    def analyze_current_file(self):
        """Analyze the currently loaded file."""
        if not hasattr(self.code_editor, 'current_file'):
            QMessageBox.information(self, "Info", "No file loaded for analysis.")
            return

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_bar.showMessage("Analyzing code...")

        # Start analysis in background thread
        self.analysis_worker = AnalysisWorker(
            self.code_editor.current_file,
            self.analyzer
        )
        self.analysis_worker.analysis_complete.connect(self.on_analysis_complete)
        self.analysis_worker.progress_update.connect(self.on_progress_update)
        self.analysis_worker.start()

    def on_analysis_complete(self, result):
        """Handle completed analysis."""
        self.progress_bar.setVisible(False)
        self.status_bar.showMessage("Analysis complete")

        # Update issue tree
        self.issue_tree.update_issues(result['issues'])

        # Highlight issues in editor
        self.code_editor.highlight_issues(result['issues'])

    def on_progress_update(self, value, message):
        """Update progress bar and status."""
        self.progress_bar.setValue(value)
        self.status_bar.showMessage(message)

    def jump_to_issue(self, line: int, column: int):
        """Jump to a specific issue in the code editor."""
        self.code_editor.jump_to_line(line, column)

    def auto_fix_issues(self):
        """Automatically fix fixable issues."""
        if not hasattr(self.code_editor, 'current_file'):
            QMessageBox.information(self, "Info", "No file loaded for fixing.")
            return

        reply = QMessageBox.question(
            self, "Confirm Auto-Fix",
            "This will automatically apply fixes to your code. Continue?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                fixed_content = self.refactor_engine.auto_fix_file(
                    self.code_editor.current_file,
                    self.get_refactor_options()
                )

                if fixed_content:
                    self.code_editor.setPlainText(fixed_content)

                    # Save the file
                    with open(self.code_editor.current_file, 'w', encoding='utf-8') as f:
                        f.write(fixed_content)

                    QMessageBox.information(self, "Success", "Auto-fix applied and file saved!")

                    # Re-analyze
                    QTimer.singleShot(500, self.analyze_current_file)

            except Exception as e:
                QMessageBox.warning(self, "Error", f"Auto-fix failed: {str(e)}")

    def get_refactor_options(self):
        """Get current refactoring options from UI."""
        return {
            'max_function_lines': self.max_function_lines.value(),
            'check_complexity': self.check_complexity.isChecked(),
            'check_duplicates': self.check_duplicates.isChecked(),
            'check_naming': self.check_naming.isChecked(),
            'check_imports': self.check_imports.isChecked(),
            'split_large_files': self.split_large_files.isChecked(),
            'extract_functions': self.extract_functions.isChecked(),
            'add_docstrings': self.add_docstrings.isChecked(),
            'add_type_hints': self.add_type_hints.isChecked(),
        }
