#!/usr/bin/env python3
"""
PDF Compare Tool Launcher
Cross-platform executable to start the PDF Compare application.
Usage: python run.py  (or ./run.py on Linux/macOS after chmod +x)
"""

import subprocess
import sys
import os
import platform
from pathlib import Path

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
    
    # Create/check virtual environment
    venv_path = script_dir / ".venv"
    if not venv_path.exists():
        print("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
        print("✓ Virtual environment created")
    
    # Determine the Python executable in venv
    if platform.system() == "Windows":
        venv_python = venv_path / "Scripts" / "python.exe"
    else:
        venv_python = venv_path / "bin" / "python"
    
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
