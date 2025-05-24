# PyRefactor - Professional Python Code Refactoring Tool

A powerful PySide6-based GUI application for analyzing, debugging, and automatically refactoring Python code. Perfect
for cleaning up large, messy codebases and integrating with PyCharm projects.

![PyRefactor Interface](https://via.placeholder.com/800x500/252526/cccccc?text=PyRefactor+Dark+Interface)

## 🚀 Features

### Code Analysis

- **AST-based Analysis**: Deep code structure understanding using Python's AST
- **Complexity Detection**: Cyclomatic complexity analysis for functions
- **Code Smell Detection**: Identifies anti-patterns and problematic code
- **Naming Convention Checks**: PEP 8 compliance validation
- **Import Organization**: Automatic import sorting and cleanup

### Automatic Refactoring

- **Large File Splitting**: Intelligently breaks down 1000+ line files
- **Function Extraction**: Identifies and extracts duplicate code patterns
- **Import Cleanup**: Organizes imports according to PEP 8
- **Docstring Generation**: Adds missing docstrings automatically
- **Code Formatting**: Removes trailing whitespace, fixes blank lines

### PyCharm Integration

- **Project Loading**: Direct PyCharm project directory support
- **File Auto-Save**: Automatically applies fixes and saves files
- **Large File Detection**: Highlights files over 200+ lines in red
- **Batch Processing**: Analyze entire project folders at once

### Professional GUI

- **Dark Theme**: Easy on the eyes for long coding sessions
- **Code Editor**: Syntax highlighting with line numbers
- **Issue Tree**: Organized view of all code problems
- **Project Browser**: Navigate your project structure easily
- **Real-time Analysis**: Background processing keeps UI responsive

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- PyCharm (optional, but recommended)

### Install Dependencies

```bash
# Clone or download the PyRefactor files
# Navigate to the PyRefactor directory

# Install required packages
pip install -r requirements.txt

# Alternative: Install minimal dependencies
pip install PySide6 astroid
```

### Project Structure

```
PyRefactor/
├── main.py                 # Application entry point
├── requirements.txt        # Dependencies
├── gui/
│   ├── __init__.py
│   ├── main_window.py      # Main application window
│   ├── code_editor.py      # Syntax-highlighted editor
│   ├── issue_tree.py       # Issue display tree
│   └── project_tree.py     # Project file browser
└── core/
    ├── __init__.py
    ├── code_analyzer.py     # Code analysis engine
    └── refactor_engine.py   # Refactoring engine
```

## 🎯 Usage

### Quick Start

```bash
# Launch the application
python main.py
```

### Opening Your PyCharm Project

1. Click **"Open Project"** or use `Ctrl+O`
2. Select your PyCharm project directory
3. The project tree will populate with all Python files
4. Large files (200+ lines) appear in orange/red

### Analyzing Code

1. **Single File**: Click any `.py` file in the project tree
2. **Auto-Analysis**: Analysis starts automatically when you open a file
3. **Manual Analysis**: Press `F5` or click "Analyze"
4. **View Issues**: Check the Issues panel for problems found

### Auto-Fixing Issues

1. **Review Issues**: Look at the suggestions in the Issues tree
2. **Apply Fixes**: Click "Auto-Fix" or use `Ctrl+F`
3. **Confirm Changes**: Review the prompt and confirm
4. **File Saved**: Fixed code is automatically saved to your file

### Issue Types Detected

#### 🔴 Errors (Critical)

- **Syntax Errors**: Python parsing failures
- **Analysis Errors**: File reading problems

#### 🟡 Warnings (Important)

- **Large Functions**: Functions over 50 lines
- **Large Classes**: Classes over 200 lines
- **Long Parameter Lists**: Functions with 6+ parameters
- **Deep Nesting**: Code nested more than 4 levels deep
- **High Complexity**: Cyclomatic complexity over 10

#### 🔵 Suggestions (Improvements)

- **Missing Docstrings**: Functions/classes without documentation
- **Naming Conventions**: Variables not following snake_case
- **Import Order**: Imports not organized per PEP 8
- **Line Length**: Lines over 120 characters
- **Trailing Whitespace**: Extra spaces at line ends
- **Multiple Blank Lines**: More than 2 consecutive empty lines

### Refactoring Options

#### Analysis Settings

- **Complexity Check**: Set maximum lines per function (default: 50)
- **Duplicate Detection**: Find repeated code patterns
- **Naming Validation**: Check PEP 8 naming conventions
- **Import Organization**: Sort and clean imports

#### Auto-Fix Options

- **Split Large Files**: Break files over 500 lines into modules
- **Extract Functions**: Create functions from duplicate code
- **Add Docstrings**: Generate basic documentation
- **Add Type Hints**: Include Python type annotations

## 🔧 Advanced Usage

### Working with Large Files (1600+ lines)

1. **Open Large File**: File appears red in project tree
2. **Analyze Structure**: Review function/class breakdown
3. **Split Suggestions**: Tool suggests logical split points
4. **Auto-Split**: Enable "Auto-split large files" option
5. **Manual Review**: Check generated split suggestions

### Batch Processing

1. **Right-click Folder**: In project tree
2. **Select "Analyze All"**: Processes all Python files
3. **Review Results**: Issues aggregated by file
4. **Batch Fix**: Apply fixes across multiple files

### Integration with PyCharm

- **Save and Reload**: PyCharm auto-detects file changes
- **Use with VCS**: Commit refactored changes separately
- **Backup Important**: Always backup before major refactoring

## ⚙️ Configuration

### Customizing Analysis Rules

Edit the settings in the right panel:

- **Max Function Lines**: Adjust complexity threshold
- **Check Duplicates**: Enable/disable duplicate detection
- **Naming Checks**: Toggle naming convention validation
- **Import Sorting**: Control import organization

### File Type Support

Currently supports:

- **Python Files**: `.py` (full analysis)
- **Config Files**: `.txt`, `.md`, `.json`, `.yml` (display only)

## 🐛 Troubleshooting

### Common Issues

#### Application Won't Start

```bash
# Check PySide6 installation
pip install --upgrade PySide6

# Verify Python version
python --version  # Should be 3.8+
```

#### Project Won't Load

- Ensure directory contains Python files
- Check file permissions
- Try loading as regular directory instead

#### Analysis Fails

- Check file encoding (should be UTF-8)
- Verify file syntax with `python -m py_compile filename.py`
- Look for very large files (>10MB)

### Error Messages

- **"Syntax error"**: Fix Python syntax before analysis
- **"Analysis failed"**: File may be corrupted or binary
- **"Auto-fix failed"**: Backup and try manual fixes

## 🤝 Contributing

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt
pip install pytest pytest-qt mypy

# Run tests
pytest

# Type checking
mypy .
```

### Feature Requests

- Large file splitting strategies
- More refactoring patterns
- Integration with other IDEs
- Custom rule configuration

## 📄 License

This project is open source. Feel free to modify and distribute.

## 🔗 Related Tools

- **Black**: Code formatting (`pip install black`)
- **isort**: Import sorting (`pip install isort`)
- **Pylint**: Advanced linting (`pip install pylint`)
- **MyPy**: Type checking (`pip install mypy`)

---

**PyRefactor** - Making Python code cleaner, one file at a time! 🐍✨