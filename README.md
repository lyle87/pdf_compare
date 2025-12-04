# PDF Compare

Side-by-side PDF comparison tool with text-based difference detection. Compare two PDFs and see differences highlighted in color-coded boxes on both pages.

## Features

- **Side-by-side PDF viewer** with synchronized navigation and zoom
- **Text-based comparison** - extracts and compares words from embedded text in PDFs
- **Color-coded highlights** - differences are highlighted with boxes
  - Yellow to red gradient: intensity based on character differences (dashes/pipes)
  - Blue: entries with numbers
- **UI Controls:**
  - Navigate between pages with prev/next or page number input
  - Zoom slider for detailed inspection
  - Sync checkbox to lock page navigation between PDFs
  - Text Diff button to enable/disable difference detection
  - Show Left Diffs toggle to control left-side visualization
- **Responsive design** - works on different screen sizes
- **Works with various PDF types** - supports PDFs with embedded text

## Quick Start

### Windows
**Simply double-click `run.bat`**

Or manually:
```bash
run.bat
```

### Linux / macOS
**Make the script executable and run it:**
```bash
chmod +x run.sh
./run.sh
```

Then open your browser to: **http://localhost:5000**

## Advanced Setup

### Manual Installation

If the automated scripts don't work, follow these steps:

1. **Install Python 3.8+** from https://www.python.org/downloads/

2. **Create a virtual environment:**
   ```bash
   python3 -m venv .venv
   ```

3. **Activate the virtual environment:**
   - **Linux/macOS:**
     ```bash
     source .venv/bin/activate
     ```
   - **Windows:**
     ```bash
     .venv\Scripts\activate
     ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the application:**
   ```bash
   python app.py
   ```

6. **Open your browser** to http://localhost:5000

### macOS App Bundle (Optional)

Create a native macOS app icon in your Applications folder:

```bash
chmod +x create_app_bundle.sh
./create_app_bundle.sh
```

This creates a `PDF Compare.app` bundle you can double-click to launch.

## Usage

1. **Upload Two PDFs**
   - Click "Upload PDFs" on the home page
   - Select your first PDF (left side)
   - Select your second PDF (right side)
   - Click "Compare"

2. **Navigate**
   - Use **Prev/Next** buttons or enter a page number
   - Use **arrow keys** as keyboard shortcuts
   - Adjust **Zoom** slider to inspect details

3. **Detect Differences**
   - Click **"Text Diff"** button to enable text-based comparison
   - Boxes appear on the PDF pages showing where text differs
   - **Right-side boxes:** Color indicates difference intensity
   - **Left-side boxes:** Toggle visibility with "Show Left Diffs"

4. **Sync Navigation**
   - Check **"Sync"** to keep both PDFs on the same page

## Technical Details

- **Backend:** Flask (Python) with PyMuPDF for text extraction
- **Frontend:** pdf.js for PDF rendering, vanilla JavaScript
- **Text Comparison:** Word-level comparison with spatial overlap detection
- **Storage:** Uploaded PDFs stored in `uploads/` directory (gitignored)

## Troubleshooting

**"Python is not installed"**
- Install Python 3.8+ from https://www.python.org/downloads/
- On Windows, check "Add Python to PATH" during installation

**Port 5000 already in use**
- Close the other application using port 5000, or edit `app.py` to use a different port:
  ```python
  app.run(host='127.0.0.1', port=5001, debug=True)
  ```

**Text differences not showing**
- Ensure the PDF has embedded text (not scanned images)
- Check browser console (F12) for error messages

**Boxes misaligned at different zoom levels**
- This is the expected behavior of DOM-based overlays; refresh the page if needed

## Notes

- Uploaded files are stored in the `uploads/` directory (safe to delete anytime)
- The application runs on `http://localhost:5000` by default
- For production use, consider using a WSGI server like Gunicorn instead of Flask's development server
