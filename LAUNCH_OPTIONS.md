## PDF Compare - Multiple Launch Options

This project includes several ways to run the application on any machine. Choose the one that best suits your system:

### Quick Launch Options

#### 1. **Windows Users** 🪟
   **Just double-click:** `run.bat`
   
   No setup needed! The script will:
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
2. Run in terminal:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows
   pip install -r requirements.txt
   python app.py
   ```

### What Each Script Does

| Script | OS | Advantages |
|--------|----|----|
| `run.sh` | Linux/macOS | Bash native, colored output, direct control |
| `run.bat` | Windows | Double-click support, automatic Python detection |
| `run.py` | Any | Pure Python, no shell scripting needed, portable |
| `create_app_bundle.sh` | macOS | Native macOS app bundle |

### Troubleshooting

**"Python not found"**
- Install from https://www.python.org/downloads/
- Windows: Check "Add Python to PATH" during installation
- macOS: Use `brew install python3` or download from python.org

**Port 5000 in use**
- Edit `app.py` and change: `app.run(host='127.0.0.1', port=5001, debug=True)`

**Permission denied (Linux/macOS)**
- Run: `chmod +x run.sh` first, then `./run.sh`

### First Run

1. Open browser to `http://localhost:5000`
2. Upload two PDF files
3. Use "Text Diff" button to compare
4. Navigate with Prev/Next or page number input
5. Use Zoom slider to inspect details

Enjoy your PDF comparison tool! 🎉
