## PDF Compare - Multiple Launch Options

This project includes several ways to run the application on any machine. Choose the one that best suits your system:

### Quick Launch Options

#### 1. **Windows Users** 🪟

**Option A: Batch file (recommended)**
   Just double-click: `run.bat`
   
**Option B: VBScript (if batch doesn't work)**
   Double-click: `run.vbs`
   
**Option C: Python (most reliable)**
   Run in Command Prompt:
   ```cmd
   python run.py
   ```
   
The script will:
   - Check if Python is installed
   - Create a virtual environment
   - Install dependencies
   - Start the server
   
Then open your browser to `http://localhost:5000`

#### 2. **Linux / macOS Users** 🐧 / 🍎
   **Run in terminal:**
   ```bash
   ./run.sh
   ```
   
   Or with explicit bash:
   ```bash
   bash run.sh
   ```
   
   The script handles everything automatically.

#### 3. **Cross-Platform (Any OS)** 🔧
   **Python launcher (most reliable):**
   ```bash
   python run.py
   ```
   or
   ```bash
   python3 run.py
   ```
   
   This works on Windows, Linux, and macOS without modification.

#### 4. **macOS App Bundle** (Optional) 📦
   Create a native macOS app in Applications folder:
   ```bash
   ./create_app_bundle.sh
   ```
   
   Then double-click `PDF Compare.app` to launch.

### Manual Setup (If scripts don't work)

1. Ensure Python 3.8+ is installed: https://www.python.org/downloads/
2. Run in terminal/command prompt:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows
   pip install -r requirements.txt
   python app.py
   ```

### What Each Script Does

| Script | OS | Advantages |
|--------|----|----|
| `run.bat` | Windows | Double-click support, automatic Python detection |
| `run.vbs` | Windows | Alternative if .bat fails, VBScript native |
| `run.py` | Any | Pure Python, no shell scripting needed, portable |
| `run.sh` | Linux/macOS | Bash native, colored output, direct control |
| `create_app_bundle.sh` | macOS | Native macOS app bundle |

### Troubleshooting

**Windows: "The system cannot find the path specified"**
- This is usually a Python PATH issue
- Try `run.vbs` instead of `run.bat`
- Or use: `python run.py` in Command Prompt
- If still failing: Uninstall Python and reinstall, making sure to check "Add Python to PATH"

**Windows: "Python is not installed"**
- Install from https://www.python.org/downloads/ (3.8 or newer)
- Make sure to check ✓ "Add Python to PATH" during installation
- Restart Command Prompt after installing Python

**macOS/Linux: "Permission denied"**
- Run: `chmod +x run.sh` first, then `./run.sh`

**Port 5000 in use**
- Edit `app.py` and change: `app.run(host='127.0.0.1', port=5001, debug=True)`

**"Module not found" errors**
- Delete `.venv` folder: `rm -rf .venv` (Linux/macOS) or `rmdir /s .venv` (Windows)
- Re-run the launcher script to rebuild dependencies

### First Run

1. Open browser to `http://localhost:5000`
2. Upload two PDF files
3. Use "Text Diff" button to compare
4. Navigate with Prev/Next or page number input
5. Use Zoom slider to inspect details

Enjoy your PDF comparison tool! 🎉
