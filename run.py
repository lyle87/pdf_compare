#!/usr/bin/env python3
"""
PDF Compare Tool Launcher
Cross-platform executable to start the PDF Compare application.
Usage: python run.py  (or ./run.py on Linux/macOS after chmod +x)
"""

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

def ensure_venv(venv_path: Path) -> Path:
    """Ensure a usable virtual environment exists and return its python path."""
    def venv_python_path(base: Path) -> Path:
        return base / ("Scripts" if platform.system() == "Windows" else "bin") / (
            "python.exe" if platform.system() == "Windows" else "python"
        )

    venv_python = venv_python_path(venv_path)
    needs_rebuild = (not venv_path.exists()) or (not venv_python.exists())

    if needs_rebuild:
        if venv_path.exists():
            print("Existing virtual environment is missing a Python executable. Rebuilding it...")
            shutil.rmtree(venv_path)

        print("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
        print("✓ Virtual environment created")
        venv_python = venv_python_path(venv_path)

    return venv_python


def main():
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)

    print("\n" + "="*50)
    print("PDF Compare Tool")
    print("="*50 + "\n")

    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8+ is required")
        print(f"   You have Python {sys.version_info.major}.{sys.version_info.minor}")
        sys.exit(1)

    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} found")

    venv_path = script_dir / ".venv"
    venv_python = ensure_venv(venv_path)

    # Install dependencies
    print("Installing dependencies...")
    subprocess.run([
        str(venv_python), "-m", "pip",
        "install", "--upgrade", "pip"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    subprocess.run([
        str(venv_python), "-m", "pip", "install", "-q", "-r", "requirements.txt"
    ], check=True)
    print("✓ Dependencies installed\n")

    # Run the app
    print("Starting PDF Compare Tool...")
    print(f"Open your browser to: http://localhost:5000")
    print("Press Ctrl+C to stop the server\n")

    subprocess.run([str(venv_python), "app.py"])

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nServer stopped.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
