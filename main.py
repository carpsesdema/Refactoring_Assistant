#!/usr/bin/env python3
"""
PyRefactor - Professional Python Code Refactoring Tool
Main application entry point
"""

import sys

from PySide6.QtGui import QPalette, QColor
from PySide6.QtWidgets import QApplication

from gui.main_window import RefactorMainWindow


def setup_dark_theme(app):
    """Apply dark theme to the application."""
    dark_palette = QPalette()

    # Window colors
    dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.WindowText, QColor(255, 255, 255))

    # Base colors (input fields)
    dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
    dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))

    # Text colors
    dark_palette.setColor(QPalette.Text, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.BrightText, QColor(255, 0, 0))

    # Button colors
    dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))

    # Highlight colors
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))

    app.setPalette(dark_palette)

    # Set additional dark theme stylesheet
    app.setStyleSheet("""
        QToolTip {
            color: #ffffff;
            background-color: #2a2a2a;
            border: 1px solid white;
        }
        QTreeWidget::item:selected {
            background-color: #2a82da;
        }
        QTabBar::tab:selected {
            background-color: #2a82da;
        }
        QGroupBox {
            font-weight: bold;
            border: 2px solid #555;
            border-radius: 5px;
            margin-top: 1ex;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }
    """)


def main():
    """Main application entry point."""
    app = QApplication(sys.argv)

    # Set application properties
    app.setApplicationName("PyRefactor")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("PyRefactor Tools")

    # Apply dark theme
    setup_dark_theme(app)

    # Create and show main window
    window = RefactorMainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
