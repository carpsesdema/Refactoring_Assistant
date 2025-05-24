#!/usr/bin/env python3
"""
Setup script for PyRefactor - Professional Python Code Refactoring Tool
"""

import os
import subprocess
import sys
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required!")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version}")
    return True


def install_dependencies():
    """Install required dependencies."""
    print("\n📦 Installing dependencies...")

    requirements_file = Path(__file__).parent / "requirements.txt"

    if not requirements_file.exists():
        print("❌ requirements.txt not found!")
        return False

    try:
        # Install requirements
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ])
        print("✅ Dependencies installed successfully!")
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        print("\n💡 Try manual installation:")
        print("   pip install PySide6 astroid")
        return False


def create_launcher():
    """Create launcher scripts for different platforms."""
    print("\n🚀 Creating launcher scripts...")

    main_py = Path(__file__).parent / "main.py"
    if not main_py.exists():
        print("❌ main.py not found!")
        return False

    # Windows launcher
    if sys.platform == "win32":
        launcher_bat = Path(__file__).parent / "PyRefactor.bat"
        with open(launcher_bat, 'w') as f:
            f.write(f'@echo off\n')
            f.write(f'cd /d "{Path(__file__).parent}"\n')
            f.write(f'python main.py %*\n')
            f.write(f'pause\n')
        print(f"✅ Created Windows launcher: {launcher_bat}")

    # Unix/Linux/Mac launcher
    launcher_sh = Path(__file__).parent / "PyRefactor.sh"
    with open(launcher_sh, 'w') as f:
        f.write(f'#!/bin/bash\n')
        f.write(f'cd "{Path(__file__).parent}"\n')
        f.write(f'python3 main.py "$@"\n')

    # Make executable on Unix systems
    if sys.platform != "win32":
        os.chmod(launcher_sh, 0o755)
        print(f"✅ Created Unix launcher: {launcher_sh}")

    return True


def verify_installation():
    """Verify that installation was successful."""
    print("\n🔍 Verifying installation...")

    try:
        # Test PySide6 import
        import PySide6
        print("✅ PySide6 is available")

        # Test astroid import
        import astroid
        print("✅ astroid is available")

        # Check if main modules can be imported
        sys.path.insert(0, str(Path(__file__).parent))

        from gui.main_window import RefactorMainWindow
        print("✅ GUI modules are available")

        from core.code_analyzer import CodeAnalyzer
        print("✅ Core modules are available")

        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False


def main():
    """Main setup function."""
    print("🔧 PyRefactor Setup")
    print("=" * 50)

    # Check Python version
    if not check_python_version():
        sys.exit(1)

    # Install dependencies
    if not install_dependencies():
        print("\n⚠️  Dependency installation failed, but you can try to run anyway.")

    # Create launchers
    create_launcher()

    # Verify installation
    if verify_installation():
        print("\n🎉 Setup completed successfully!")
        print("\n🚀 To start PyRefactor:")

        if sys.platform == "win32":
            print("   - Double-click PyRefactor.bat")
            print("   - Or run: python main.py")
        else:
            print("   - Run: ./PyRefactor.sh")
            print("   - Or run: python3 main.py")

        print("\n📖 See README.md for usage instructions")

    else:
        print("\n❌ Setup completed with errors")
        print("   Try running manually: python main.py")


if __name__ == "__main__":
    main()
